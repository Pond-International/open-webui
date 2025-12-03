import asyncio
import hashlib
import json
import logging
from typing import Optional

import aiohttp
from aiocache import cached
import requests

from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from fastapi import Depends, HTTPException, Request, APIRouter
from fastapi.responses import (
    FileResponse,
    StreamingResponse,
    JSONResponse,
    PlainTextResponse,
)
from pydantic import BaseModel
from starlette.background import BackgroundTask

from open_webui.models.models import Models
from open_webui.config import (
    CACHE_DIR,
)
from open_webui.env import (
    MODELS_CACHE_TTL,
    AIOHTTP_CLIENT_SESSION_SSL,
    AIOHTTP_CLIENT_TIMEOUT,
    AIOHTTP_CLIENT_TIMEOUT_MODEL_LIST,
    ENABLE_FORWARD_USER_INFO_HEADERS,
    BYPASS_MODEL_ACCESS_CONTROL,
)
from open_webui.models.users import UserModel

from open_webui.constants import ERROR_MESSAGES
from open_webui.env import SRC_LOG_LEVELS


from open_webui.utils.payload import (
    apply_model_params_to_body_openai,
    apply_system_prompt_to_body,
)
from open_webui.utils.misc import (
    convert_logit_bias_input_to_json,
    stream_chunks_handler,
)

from open_webui.utils.auth import get_admin_user, get_verified_user
from open_webui.utils.access_control import has_access
from open_webui.utils.headers import include_user_info_headers


log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)

# 导入 Snowflake Cortex Search
try:
    from open_webui.utils.snowflake_cortex import search_snowflake_cortex
    SNOWFLAKE_CORTEX_AVAILABLE = True
except ImportError:
    SNOWFLAKE_CORTEX_AVAILABLE = False
    log.warning("Snowflake Cortex Search not available")


##########################################
#
# Utility functions
#
##########################################


async def send_get_request(url, key=None, user: UserModel = None):
    timeout = aiohttp.ClientTimeout(total=AIOHTTP_CLIENT_TIMEOUT_MODEL_LIST)
    try:
        async with aiohttp.ClientSession(timeout=timeout, trust_env=True) as session:
            headers = {
                **({"Authorization": f"Bearer {key}"} if key else {}),
            }

            if ENABLE_FORWARD_USER_INFO_HEADERS and user:
                headers = include_user_info_headers(headers, user)

            async with session.get(
                url,
                headers=headers,
                ssl=AIOHTTP_CLIENT_SESSION_SSL,
            ) as response:
                return await response.json()
    except Exception as e:
        # Handle connection error here
        log.error(f"Connection error: {e}")
        return None


async def cleanup_response(
    response: Optional[aiohttp.ClientResponse],
    session: Optional[aiohttp.ClientSession],
):
    if response:
        response.close()
    if session:
        await session.close()


async def enhance_payload_with_snowflake_search(payload: dict) -> tuple[dict, bool]:
    """
    使用 Snowflake Cortex Search 增强 payload，将检索结果合并到用户消息中
    
    Args:
        payload: OpenAI API 请求的 payload
        
    Returns:
        (增强后的 payload, 是否使用了 Snowflake Cortex Search)
    """
    log.info(f"enhance_payload_with_snowflake_search called, SNOWFLAKE_CORTEX_AVAILABLE={SNOWFLAKE_CORTEX_AVAILABLE}")
    
    if not SNOWFLAKE_CORTEX_AVAILABLE:
        log.info("Snowflake Cortex Search not available, skipping")
        return payload, False
    
    if "messages" not in payload:
        log.info("No messages in payload, skipping Snowflake search")
        return payload, False
    
    # 提取最后一个用户消息作为搜索查询
    user_query = None
    user_message_index = None
    
    # 从后往前查找最后一个用户消息
    for i in range(len(payload["messages"]) - 1, -1, -1):
        message = payload["messages"][i]
        if message.get("role") == "user":
            user_message_index = i
            content = message.get("content", "")
            
            # 处理不同类型的content格式
            if isinstance(content, str):
                user_query = content
            elif isinstance(content, list):
                # 如果是列表格式，提取文本内容
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                user_query = " ".join(text_parts)
            break
    
    # 如果没有找到用户消息，直接返回
    if not user_query or user_message_index is None:
        return payload, False
    
    try:
        # 执行 Snowflake Cortex Search
        log.info(f"Executing Snowflake Cortex Search for query: {user_query[:100]}...")
        search_results = await search_snowflake_cortex(query=user_query, limit=5)
        
        if search_results:
            # 将检索结果合并到用户消息中
            original_content = payload["messages"][user_message_index].get("content", "")
            
            # 构建增强后的消息内容
            if isinstance(original_content, str):
                # 简单字符串格式：在用户问题前添加检索结果
                enhanced_content = f"{search_results}\n\n用户问题：{original_content}"
                payload["messages"][user_message_index]["content"] = enhanced_content
            elif isinstance(original_content, list):
                # 列表格式（可能包含图片等）：在列表开头添加文本内容
                enhanced_text = f"{search_results}\n\n用户问题："
                # 提取原有文本内容
                text_content = ""
                other_items = []
                for item in original_content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_content = item.get("text", "")
                    else:
                        other_items.append(item)
                
                # 构建新的content列表
                new_content = [
                    {"type": "text", "text": f"{enhanced_text}{text_content}"}
                ]
                new_content.extend(other_items)
                payload["messages"][user_message_index]["content"] = new_content
            
            log.info("Successfully enhanced payload with Snowflake Cortex Search results")
            return payload, True
        else:
            log.debug("No Snowflake Cortex Search results found")
            return payload, False
            
    except Exception as e:
        log.error(f"Error enhancing payload with Snowflake Cortex Search: {e}")
        # 即使搜索失败，也继续处理原始请求
        return payload, False


def add_knowledge_base_marker_to_stream(stream, marker: str):
    """
    在流式响应的第一个内容 chunk 前添加知识库引用标记
    
    Args:
        stream: 原始流
        marker: 要添加的标记文本
        
    Returns:
        修改后的流生成器
    """
    async def enhanced_stream():
        first_content_chunk = True
        marker_sent = False
        
        async for chunk in stream:
            # 跳过空行和 metadata 行
            if not chunk or chunk.strip() == b"":
                yield chunk
                continue
            
            chunk_str = chunk.decode('utf-8', errors='ignore') if isinstance(chunk, bytes) else chunk
            
            # 检查是否是内容 chunk (data: {"choices":...})
            if chunk_str.startswith("data: ") and '"content"' in chunk_str:
                if first_content_chunk and not marker_sent:
                    try:
                        # 解析 JSON
                        data_str = chunk_str[6:]  # 移除 "data: " 前缀
                        if data_str.strip() and data_str.strip() != "[DONE]":
                            data = json.loads(data_str)
                            # 在第一个内容 chunk 前添加标记
                            if "choices" in data and len(data["choices"]) > 0:
                                choice = data["choices"][0]
                                if "delta" in choice and "content" in choice["delta"]:
                                    # 在内容前添加标记
                                    original_content = choice["delta"]["content"]
                                    choice["delta"]["content"] = f"{marker}\n\n{original_content}"
                                    # 重新编码
                                    yield f"data: {json.dumps(data)}\n\n".encode('utf-8')
                                    marker_sent = True
                                    first_content_chunk = False
                                    continue
                    except (json.JSONDecodeError, KeyError) as e:
                        log.debug(f"Error parsing chunk for marker: {e}")
            
            yield chunk
            first_content_chunk = False
    
    return enhanced_stream()


def add_knowledge_base_marker_to_response(response: dict, marker: str) -> dict:
    """
    在非流式响应的内容前添加知识库引用标记
    
    Args:
        response: 响应字典
        marker: 要添加的标记文本
        
    Returns:
        修改后的响应
    """
    if isinstance(response, dict) and "choices" in response:
        for choice in response.get("choices", []):
            if "message" in choice and "content" in choice["message"]:
                original_content = choice["message"]["content"]
                choice["message"]["content"] = f"{marker}\n\n{original_content}"
    return response


def openai_reasoning_model_handler(payload):
    """
    Handle reasoning model specific parameters
    """
    if "max_tokens" in payload:
        # Convert "max_tokens" to "max_completion_tokens" for all reasoning models
        payload["max_completion_tokens"] = payload["max_tokens"]
        del payload["max_tokens"]

    # Handle system role conversion based on model type
    if payload["messages"][0]["role"] == "system":
        model_lower = payload["model"].lower()
        # Legacy models use "user" role instead of "system"
        if model_lower.startswith("o1-mini") or model_lower.startswith("o1-preview"):
            payload["messages"][0]["role"] = "user"
        else:
            payload["messages"][0]["role"] = "developer"

    return payload


async def get_headers_and_cookies(
    request: Request,
    url,
    key=None,
    config=None,
    metadata: Optional[dict] = None,
    user: UserModel = None,
):
    cookies = {}
    headers = {
        "Content-Type": "application/json",
        **(
            {
                "HTTP-Referer": "https://openwebui.com/",
                "X-Title": "Open WebUI",
            }
            if "openrouter.ai" in url
            else {}
        ),
    }

    if ENABLE_FORWARD_USER_INFO_HEADERS and user:
        headers = include_user_info_headers(headers, user)
        if metadata and metadata.get("chat_id"):
            headers["X-OpenWebUI-Chat-Id"] = metadata.get("chat_id")

    token = None
    auth_type = config.get("auth_type")

    if auth_type == "bearer" or auth_type is None:
        # Default to bearer if not specified
        token = f"{key}"
    elif auth_type == "none":
        token = None
    elif auth_type == "session":
        cookies = request.cookies
        token = request.state.token.credentials
    elif auth_type == "system_oauth":
        cookies = request.cookies

        oauth_token = None
        try:
            if request.cookies.get("oauth_session_id", None):
                oauth_token = await request.app.state.oauth_manager.get_oauth_token(
                    user.id,
                    request.cookies.get("oauth_session_id", None),
                )
        except Exception as e:
            log.error(f"Error getting OAuth token: {e}")

        if oauth_token:
            token = f"{oauth_token.get('access_token', '')}"

    elif auth_type in ("azure_ad", "microsoft_entra_id"):
        token = get_microsoft_entra_id_access_token()

    if token:
        headers["Authorization"] = f"Bearer {token}"

    if config.get("headers") and isinstance(config.get("headers"), dict):
        headers = {**headers, **config.get("headers")}

    return headers, cookies


def get_microsoft_entra_id_access_token():
    """
    Get Microsoft Entra ID access token using DefaultAzureCredential for Azure OpenAI.
    Returns the token string or None if authentication fails.
    """
    try:
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )
        return token_provider()
    except Exception as e:
        log.error(f"Error getting Microsoft Entra ID access token: {e}")
        return None


##########################################
#
# API routes
#
##########################################

router = APIRouter()


@router.get("/config")
async def get_config(request: Request, user=Depends(get_admin_user)):
    return {
        "ENABLE_OPENAI_API": request.app.state.config.ENABLE_OPENAI_API,
        "OPENAI_API_BASE_URLS": request.app.state.config.OPENAI_API_BASE_URLS,
        "OPENAI_API_KEYS": request.app.state.config.OPENAI_API_KEYS,
        "OPENAI_API_CONFIGS": request.app.state.config.OPENAI_API_CONFIGS,
    }


class OpenAIConfigForm(BaseModel):
    ENABLE_OPENAI_API: Optional[bool] = None
    OPENAI_API_BASE_URLS: list[str]
    OPENAI_API_KEYS: list[str]
    OPENAI_API_CONFIGS: dict


@router.post("/config/update")
async def update_config(
    request: Request, form_data: OpenAIConfigForm, user=Depends(get_admin_user)
):
    request.app.state.config.ENABLE_OPENAI_API = form_data.ENABLE_OPENAI_API
    request.app.state.config.OPENAI_API_BASE_URLS = form_data.OPENAI_API_BASE_URLS
    request.app.state.config.OPENAI_API_KEYS = form_data.OPENAI_API_KEYS

    # Check if API KEYS length is same than API URLS length
    if len(request.app.state.config.OPENAI_API_KEYS) != len(
        request.app.state.config.OPENAI_API_BASE_URLS
    ):
        if len(request.app.state.config.OPENAI_API_KEYS) > len(
            request.app.state.config.OPENAI_API_BASE_URLS
        ):
            request.app.state.config.OPENAI_API_KEYS = (
                request.app.state.config.OPENAI_API_KEYS[
                    : len(request.app.state.config.OPENAI_API_BASE_URLS)
                ]
            )
        else:
            request.app.state.config.OPENAI_API_KEYS += [""] * (
                len(request.app.state.config.OPENAI_API_BASE_URLS)
                - len(request.app.state.config.OPENAI_API_KEYS)
            )

    request.app.state.config.OPENAI_API_CONFIGS = form_data.OPENAI_API_CONFIGS

    # Remove the API configs that are not in the API URLS
    keys = list(map(str, range(len(request.app.state.config.OPENAI_API_BASE_URLS))))
    request.app.state.config.OPENAI_API_CONFIGS = {
        key: value
        for key, value in request.app.state.config.OPENAI_API_CONFIGS.items()
        if key in keys
    }

    return {
        "ENABLE_OPENAI_API": request.app.state.config.ENABLE_OPENAI_API,
        "OPENAI_API_BASE_URLS": request.app.state.config.OPENAI_API_BASE_URLS,
        "OPENAI_API_KEYS": request.app.state.config.OPENAI_API_KEYS,
        "OPENAI_API_CONFIGS": request.app.state.config.OPENAI_API_CONFIGS,
    }


@router.post("/audio/speech")
async def speech(request: Request, user=Depends(get_verified_user)):
    idx = None
    try:
        idx = request.app.state.config.OPENAI_API_BASE_URLS.index(
            "https://api.openai.com/v1"
        )

        body = await request.body()
        name = hashlib.sha256(body).hexdigest()

        SPEECH_CACHE_DIR = CACHE_DIR / "audio" / "speech"
        SPEECH_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        file_path = SPEECH_CACHE_DIR.joinpath(f"{name}.mp3")
        file_body_path = SPEECH_CACHE_DIR.joinpath(f"{name}.json")

        # Check if the file already exists in the cache
        if file_path.is_file():
            return FileResponse(file_path)

        url = request.app.state.config.OPENAI_API_BASE_URLS[idx]
        key = request.app.state.config.OPENAI_API_KEYS[idx]
        api_config = request.app.state.config.OPENAI_API_CONFIGS.get(
            str(idx),
            request.app.state.config.OPENAI_API_CONFIGS.get(url, {}),  # Legacy support
        )

        headers, cookies = await get_headers_and_cookies(
            request, url, key, api_config, user=user
        )

        r = None
        try:
            r = requests.post(
                url=f"{url}/audio/speech",
                data=body,
                headers=headers,
                cookies=cookies,
                stream=True,
            )

            r.raise_for_status()

            # Save the streaming content to a file
            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            with open(file_body_path, "w") as f:
                json.dump(json.loads(body.decode("utf-8")), f)

            # Return the saved file
            return FileResponse(file_path)

        except Exception as e:
            log.exception(e)

            detail = None
            if r is not None:
                try:
                    res = r.json()
                    if "error" in res:
                        detail = f"External: {res['error']}"
                except Exception:
                    detail = f"External: {e}"

            raise HTTPException(
                status_code=r.status_code if r else 500,
                detail=detail if detail else "Open WebUI: Server Connection Error",
            )

    except ValueError:
        raise HTTPException(status_code=401, detail=ERROR_MESSAGES.OPENAI_NOT_FOUND)


async def get_all_models_responses(request: Request, user: UserModel) -> list:
    if not request.app.state.config.ENABLE_OPENAI_API:
        return []

    # Check if API KEYS length is same than API URLS length
    num_urls = len(request.app.state.config.OPENAI_API_BASE_URLS)
    num_keys = len(request.app.state.config.OPENAI_API_KEYS)

    if num_keys != num_urls:
        # if there are more keys than urls, remove the extra keys
        if num_keys > num_urls:
            new_keys = request.app.state.config.OPENAI_API_KEYS[:num_urls]
            request.app.state.config.OPENAI_API_KEYS = new_keys
        # if there are more urls than keys, add empty keys
        else:
            request.app.state.config.OPENAI_API_KEYS += [""] * (num_urls - num_keys)

    request_tasks = []
    for idx, url in enumerate(request.app.state.config.OPENAI_API_BASE_URLS):
        if (str(idx) not in request.app.state.config.OPENAI_API_CONFIGS) and (
            url not in request.app.state.config.OPENAI_API_CONFIGS  # Legacy support
        ):
            request_tasks.append(
                send_get_request(
                    f"{url}/models",
                    request.app.state.config.OPENAI_API_KEYS[idx],
                    user=user,
                )
            )
        else:
            api_config = request.app.state.config.OPENAI_API_CONFIGS.get(
                str(idx),
                request.app.state.config.OPENAI_API_CONFIGS.get(
                    url, {}
                ),  # Legacy support
            )

            enable = api_config.get("enable", True)
            model_ids = api_config.get("model_ids", [])

            if enable:
                if len(model_ids) == 0:
                    request_tasks.append(
                        send_get_request(
                            f"{url}/models",
                            request.app.state.config.OPENAI_API_KEYS[idx],
                            user=user,
                        )
                    )
                else:
                    model_list = {
                        "object": "list",
                        "data": [
                            {
                                "id": model_id,
                                "name": model_id,
                                "owned_by": "openai",
                                "openai": {"id": model_id},
                                "urlIdx": idx,
                            }
                            for model_id in model_ids
                        ],
                    }

                    request_tasks.append(
                        asyncio.ensure_future(asyncio.sleep(0, model_list))
                    )
            else:
                request_tasks.append(asyncio.ensure_future(asyncio.sleep(0, None)))

    responses = await asyncio.gather(*request_tasks)

    for idx, response in enumerate(responses):
        if response:
            url = request.app.state.config.OPENAI_API_BASE_URLS[idx]
            api_config = request.app.state.config.OPENAI_API_CONFIGS.get(
                str(idx),
                request.app.state.config.OPENAI_API_CONFIGS.get(
                    url, {}
                ),  # Legacy support
            )

            connection_type = api_config.get("connection_type", "external")
            prefix_id = api_config.get("prefix_id", None)
            tags = api_config.get("tags", [])

            model_list = (
                response if isinstance(response, list) else response.get("data", [])
            )
            if not isinstance(model_list, list):
                # Catch non-list responses
                model_list = []

            for model in model_list:
                # Remove name key if its value is None #16689
                if "name" in model and model["name"] is None:
                    del model["name"]

                if prefix_id:
                    model["id"] = (
                        f"{prefix_id}.{model.get('id', model.get('name', ''))}"
                    )

                if tags:
                    model["tags"] = tags

                if connection_type:
                    model["connection_type"] = connection_type

    log.debug(f"get_all_models:responses() {responses}")
    return responses


async def get_filtered_models(models, user):
    # Filter models based on user access control
    filtered_models = []
    for model in models.get("data", []):
        model_info = Models.get_model_by_id(model["id"])
        if model_info:
            if user.id == model_info.user_id or has_access(
                user.id, type="read", access_control=model_info.access_control
            ):
                filtered_models.append(model)
    return filtered_models


@cached(
    ttl=MODELS_CACHE_TTL,
    key=lambda _, user: f"openai_all_models_{user.id}" if user else "openai_all_models",
)
async def get_all_models(request: Request, user: UserModel) -> dict[str, list]:
    log.info("get_all_models()")

    if not request.app.state.config.ENABLE_OPENAI_API:
        return {"data": []}

    responses = await get_all_models_responses(request, user=user)

    def extract_data(response):
        if response and "data" in response:
            return response["data"]
        if isinstance(response, list):
            return response
        return None

    def is_supported_openai_models(model_id):
        if any(
            name in model_id
            for name in [
                "babbage",
                "dall-e",
                "davinci",
                "embedding",
                "tts",
                "whisper",
            ]
        ):
            return False
        return True

    def get_merged_models(model_lists):
        log.debug(f"merge_models_lists {model_lists}")
        models = {}

        for idx, model_list in enumerate(model_lists):
            if model_list is not None and "error" not in model_list:
                for model in model_list:
                    model_id = model.get("id") or model.get("name")

                    if (
                        "api.openai.com"
                        in request.app.state.config.OPENAI_API_BASE_URLS[idx]
                        and not is_supported_openai_models(model_id)
                    ):
                        # Skip unwanted OpenAI models
                        continue

                    if model_id and model_id not in models:
                        models[model_id] = {
                            **model,
                            "name": model.get("name", model_id),
                            "owned_by": "openai",
                            "openai": model,
                            "connection_type": model.get("connection_type", "external"),
                            "urlIdx": idx,
                        }

        return models

    models = get_merged_models(map(extract_data, responses))
    log.debug(f"models: {models}")

    request.app.state.OPENAI_MODELS = models
    return {"data": list(models.values())}


@router.get("/models")
@router.get("/models/{url_idx}")
async def get_models(
    request: Request, url_idx: Optional[int] = None, user=Depends(get_verified_user)
):
    models = {
        "data": [],
    }

    if url_idx is None:
        models = await get_all_models(request, user=user)
    else:
        url = request.app.state.config.OPENAI_API_BASE_URLS[url_idx]
        key = request.app.state.config.OPENAI_API_KEYS[url_idx]

        api_config = request.app.state.config.OPENAI_API_CONFIGS.get(
            str(url_idx),
            request.app.state.config.OPENAI_API_CONFIGS.get(url, {}),  # Legacy support
        )

        r = None
        async with aiohttp.ClientSession(
            trust_env=True,
            timeout=aiohttp.ClientTimeout(total=AIOHTTP_CLIENT_TIMEOUT_MODEL_LIST),
        ) as session:
            try:
                headers, cookies = await get_headers_and_cookies(
                    request, url, key, api_config, user=user
                )

                if api_config.get("azure", False):
                    models = {
                        "data": api_config.get("model_ids", []) or [],
                        "object": "list",
                    }
                else:
                    async with session.get(
                        f"{url}/models",
                        headers=headers,
                        cookies=cookies,
                        ssl=AIOHTTP_CLIENT_SESSION_SSL,
                    ) as r:
                        if r.status != 200:
                            # Extract response error details if available
                            error_detail = f"HTTP Error: {r.status}"
                            res = await r.json()
                            if "error" in res:
                                error_detail = f"External Error: {res['error']}"
                            raise Exception(error_detail)

                        response_data = await r.json()

                        # Check if we're calling OpenAI API based on the URL
                        if "api.openai.com" in url:
                            # Filter models according to the specified conditions
                            response_data["data"] = [
                                model
                                for model in response_data.get("data", [])
                                if not any(
                                    name in model["id"]
                                    for name in [
                                        "babbage",
                                        "dall-e",
                                        "davinci",
                                        "embedding",
                                        "tts",
                                        "whisper",
                                    ]
                                )
                            ]

                        models = response_data
            except aiohttp.ClientError as e:
                # ClientError covers all aiohttp requests issues
                log.exception(f"Client error: {str(e)}")
                raise HTTPException(
                    status_code=500, detail="Open WebUI: Server Connection Error"
                )
            except Exception as e:
                log.exception(f"Unexpected error: {e}")
                error_detail = f"Unexpected error: {str(e)}"
                raise HTTPException(status_code=500, detail=error_detail)

    if user.role == "user" and not BYPASS_MODEL_ACCESS_CONTROL:
        models["data"] = await get_filtered_models(models, user)

    return models


class ConnectionVerificationForm(BaseModel):
    url: str
    key: str

    config: Optional[dict] = None


@router.post("/verify")
async def verify_connection(
    request: Request,
    form_data: ConnectionVerificationForm,
    user=Depends(get_admin_user),
):
    url = form_data.url
    key = form_data.key

    api_config = form_data.config or {}

    async with aiohttp.ClientSession(
        trust_env=True,
        timeout=aiohttp.ClientTimeout(total=AIOHTTP_CLIENT_TIMEOUT_MODEL_LIST),
    ) as session:
        try:
            headers, cookies = await get_headers_and_cookies(
                request, url, key, api_config, user=user
            )

            if api_config.get("azure", False):
                # Only set api-key header if not using Azure Entra ID authentication
                auth_type = api_config.get("auth_type", "bearer")
                if auth_type not in ("azure_ad", "microsoft_entra_id"):
                    headers["api-key"] = key

                api_version = api_config.get("api_version", "") or "2023-03-15-preview"
                async with session.get(
                    url=f"{url}/openai/models?api-version={api_version}",
                    headers=headers,
                    cookies=cookies,
                    ssl=AIOHTTP_CLIENT_SESSION_SSL,
                ) as r:
                    try:
                        response_data = await r.json()
                    except Exception:
                        response_data = await r.text()

                    if r.status != 200:
                        if isinstance(response_data, (dict, list)):
                            return JSONResponse(
                                status_code=r.status, content=response_data
                            )
                        else:
                            return PlainTextResponse(
                                status_code=r.status, content=response_data
                            )

                    return response_data
            else:
                async with session.get(
                    f"{url}/models",
                    headers=headers,
                    cookies=cookies,
                    ssl=AIOHTTP_CLIENT_SESSION_SSL,
                ) as r:
                    try:
                        response_data = await r.json()
                    except Exception:
                        response_data = await r.text()

                    if r.status != 200:
                        if isinstance(response_data, (dict, list)):
                            return JSONResponse(
                                status_code=r.status, content=response_data
                            )
                        else:
                            return PlainTextResponse(
                                status_code=r.status, content=response_data
                            )

                    return response_data

        except aiohttp.ClientError as e:
            # ClientError covers all aiohttp requests issues
            log.exception(f"Client error: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Open WebUI: Server Connection Error"
            )
        except Exception as e:
            log.exception(f"Unexpected error: {e}")
            raise HTTPException(
                status_code=500, detail="Open WebUI: Server Connection Error"
            )


def get_azure_allowed_params(api_version: str) -> set[str]:
    allowed_params = {
        "messages",
        "temperature",
        "role",
        "content",
        "contentPart",
        "contentPartImage",
        "enhancements",
        "dataSources",
        "n",
        "stream",
        "stop",
        "max_tokens",
        "presence_penalty",
        "frequency_penalty",
        "logit_bias",
        "user",
        "function_call",
        "functions",
        "tools",
        "tool_choice",
        "top_p",
        "log_probs",
        "top_logprobs",
        "response_format",
        "seed",
        "max_completion_tokens",
        "reasoning_effort",
    }

    try:
        if api_version >= "2024-09-01-preview":
            allowed_params.add("stream_options")
    except ValueError:
        log.debug(
            f"Invalid API version {api_version} for Azure OpenAI. Defaulting to allowed parameters."
        )

    return allowed_params


def is_openai_reasoning_model(model: str) -> bool:
    return model.lower().startswith(("o1", "o3", "o4", "gpt-5"))


def convert_to_azure_payload(url, payload: dict, api_version: str):
    model = payload.get("model", "")

    # Filter allowed parameters based on Azure OpenAI API
    allowed_params = get_azure_allowed_params(api_version)

    # Special handling for o-series models
    if is_openai_reasoning_model(model):
        # Convert max_tokens to max_completion_tokens for o-series models
        if "max_tokens" in payload:
            payload["max_completion_tokens"] = payload["max_tokens"]
            del payload["max_tokens"]

        # Remove temperature if not 1 for o-series models
        if "temperature" in payload and payload["temperature"] != 1:
            log.debug(
                f"Removing temperature parameter for o-series model {model} as only default value (1) is supported"
            )
            del payload["temperature"]

    # Filter out unsupported parameters
    payload = {k: v for k, v in payload.items() if k in allowed_params}

    url = f"{url}/openai/deployments/{model}"
    return url, payload


@router.post("/chat/completions")
async def generate_chat_completion(
    request: Request,
    form_data: dict,
    user=Depends(get_verified_user),
    bypass_filter: Optional[bool] = False,
):
    if BYPASS_MODEL_ACCESS_CONTROL:
        bypass_filter = True

    idx = 0

    payload = {**form_data}
    metadata = payload.pop("metadata", None)

    # 初始化 Snowflake Cortex Search 相关变量
    snowflake_search_used = False

    knowledge_base_marker = "📚 **Referenced Knowledge Base**\n\n*This answer is generated based on the knowledge base content retrieved from project and pond.*"

    model_id = form_data.get("model")
    model_info = Models.get_model_by_id(model_id)

    # Check model info and override the payload
    if model_info:
        if model_info.base_model_id:
            payload["model"] = model_info.base_model_id
            model_id = model_info.base_model_id

        params = model_info.params.model_dump()

        if params:
            system = params.pop("system", None)

            payload = apply_model_params_to_body_openai(params, payload)
            payload = apply_system_prompt_to_body(system, payload, metadata, user)
        
        # 无论是否有 params，都尝试使用 Snowflake Cortex Search
        log.info(f"About to call enhance_payload_with_snowflake_search, model_id={model_id}")
        payload, snowflake_search_used = await enhance_payload_with_snowflake_search(payload)
        log.info(f"Snowflake search result: used={snowflake_search_used}")

        # Check if user has access to the model
        if not bypass_filter and user.role == "user":
            if not (
                user.id == model_info.user_id
                or has_access(
                    user.id, type="read", access_control=model_info.access_control
                )
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Model not found",
                )
    elif not bypass_filter:
        if user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Model not found",
            )
        # 即使没有 model_info，也尝试使用 Snowflake Cortex Search
        log.info(f"About to call enhance_payload_with_snowflake_search (no model_info), model_id={model_id}")
        payload, snowflake_search_used = await enhance_payload_with_snowflake_search(payload)
        log.info(f"Snowflake search result: used={snowflake_search_used}")
    else:
        # 即使没有 model_info，也尝试使用 Snowflake Cortex Search
        log.info(f"About to call enhance_payload_with_snowflake_search (bypass_filter), model_id={model_id}")
        payload, snowflake_search_used = await enhance_payload_with_snowflake_search(payload)
        log.info(f"Snowflake search result: used={snowflake_search_used}")

    await get_all_models(request, user=user)
    model = request.app.state.OPENAI_MODELS.get(model_id)

    # 如果模型不在列表中，但模型 ID 是 gpt-4.1-mini 或 gpt-4o-mini，使用第一个可用的 OpenAI API
    if not model and model_id in ['gpt-4.1-mini', 'gpt-4o-mini']:
        if request.app.state.config.ENABLE_OPENAI_API and len(request.app.state.config.OPENAI_API_BASE_URLS) > 0:
            # 使用第一个可用的 OpenAI API URL
            idx = 0
            model = {
                "id": model_id,
                "name": model_id,
                "owned_by": "openai",
                "urlIdx": idx,
            }
            # 将模型添加到 OPENAI_MODELS 中，以便后续使用
            request.app.state.OPENAI_MODELS[model_id] = model
            log.info(f"Added fixed model {model_id} to OPENAI_MODELS")
        else:
            log.error(f"ENABLE_OPENAI_API: {request.app.state.config.ENABLE_OPENAI_API}, OPENAI_API_BASE_URLS length: {len(request.app.state.config.OPENAI_API_BASE_URLS)}")
            raise HTTPException(
                status_code=404,
                detail="Model not found",
            )
    elif model:
        idx = model["urlIdx"]
    else:
        log.error(f"Model {model_id} not found in OPENAI_MODELS. Available models: {list(request.app.state.OPENAI_MODELS.keys())[:10]}")
        raise HTTPException(
            status_code=404,
            detail="Model not found",
        )

    # Get the API config for the model
    api_config = request.app.state.config.OPENAI_API_CONFIGS.get(
        str(idx),
        request.app.state.config.OPENAI_API_CONFIGS.get(
            request.app.state.config.OPENAI_API_BASE_URLS[idx], {}
        ),  # Legacy support
    )

    prefix_id = api_config.get("prefix_id", None)
    if prefix_id:
        payload["model"] = payload["model"].replace(f"{prefix_id}.", "")

    # Add user info to the payload if the model is a pipeline
    if "pipeline" in model and model.get("pipeline"):
        payload["user"] = {
            "name": user.name,
            "id": user.id,
            "email": user.email,
            "role": user.role,
        }

    url = request.app.state.config.OPENAI_API_BASE_URLS[idx]
    key = request.app.state.config.OPENAI_API_KEYS[idx]

    # Check if model is a reasoning model that needs special handling
    if is_openai_reasoning_model(payload["model"]):
        payload = openai_reasoning_model_handler(payload)
    elif "api.openai.com" not in url:
        # Remove "max_completion_tokens" from the payload for backward compatibility
        if "max_completion_tokens" in payload:
            payload["max_tokens"] = payload["max_completion_tokens"]
            del payload["max_completion_tokens"]

    if "max_tokens" in payload and "max_completion_tokens" in payload:
        del payload["max_tokens"]

    # Convert the modified body back to JSON
    if "logit_bias" in payload:
        payload["logit_bias"] = json.loads(
            convert_logit_bias_input_to_json(payload["logit_bias"])
        )

    headers, cookies = await get_headers_and_cookies(
        request, url, key, api_config, metadata, user=user
    )

    if api_config.get("azure", False):
        api_version = api_config.get("api_version", "2023-03-15-preview")
        request_url, payload = convert_to_azure_payload(url, payload, api_version)

        # Only set api-key header if not using Azure Entra ID authentication
        auth_type = api_config.get("auth_type", "bearer")
        if auth_type not in ("azure_ad", "microsoft_entra_id"):
            headers["api-key"] = key

        headers["api-version"] = api_version
        request_url = f"{request_url}/chat/completions?api-version={api_version}"
    else:
        request_url = f"{url}/chat/completions"

    payload = json.dumps(payload)

    r = None
    session = None
    streaming = False
    response = None

    try:
        session = aiohttp.ClientSession(
            trust_env=True, timeout=aiohttp.ClientTimeout(total=AIOHTTP_CLIENT_TIMEOUT)
        )

        r = await session.request(
            method="POST",
            url=request_url,
            data=payload,
            headers=headers,
            cookies=cookies,
            ssl=AIOHTTP_CLIENT_SESSION_SSL,
        )

        # Check if response is SSE
        if "text/event-stream" in r.headers.get("Content-Type", ""):
            streaming = True
            # 如果使用了 Snowflake Cortex Search，在流式响应中添加标记
            if snowflake_search_used:
                stream = add_knowledge_base_marker_to_stream(
                    stream_chunks_handler(r.content),
                    knowledge_base_marker
                )
            else:
                stream = stream_chunks_handler(r.content)
            
            return StreamingResponse(
                stream,
                status_code=r.status,
                headers=dict(r.headers),
                background=BackgroundTask(
                    cleanup_response, response=r, session=session
                ),
            )
        else:
            try:
                response = await r.json()
            except Exception as e:
                log.error(e)
                response = await r.text()

            if r.status >= 400:
                if isinstance(response, (dict, list)):
                    return JSONResponse(status_code=r.status, content=response)
                else:
                    return PlainTextResponse(status_code=r.status, content=response)

            # 如果使用了 Snowflake Cortex Search，在非流式响应中添加标记
            if snowflake_search_used and isinstance(response, dict):
                response = add_knowledge_base_marker_to_response(response, knowledge_base_marker)

            return response
    except Exception as e:
        log.exception(e)

        raise HTTPException(
            status_code=r.status if r else 500,
            detail="Open WebUI: Server Connection Error",
        )
    finally:
        if not streaming:
            await cleanup_response(r, session)


async def embeddings(request: Request, form_data: dict, user):
    """
    Calls the embeddings endpoint for OpenAI-compatible providers.

    Args:
        request (Request): The FastAPI request context.
        form_data (dict): OpenAI-compatible embeddings payload.
        user (UserModel): The authenticated user.

    Returns:
        dict: OpenAI-compatible embeddings response.
    """
    idx = 0
    # Prepare payload/body
    body = json.dumps(form_data)
    # Find correct backend url/key based on model
    await get_all_models(request, user=user)
    model_id = form_data.get("model")
    models = request.app.state.OPENAI_MODELS
    if model_id in models:
        idx = models[model_id]["urlIdx"]

    url = request.app.state.config.OPENAI_API_BASE_URLS[idx]
    key = request.app.state.config.OPENAI_API_KEYS[idx]
    api_config = request.app.state.config.OPENAI_API_CONFIGS.get(
        str(idx),
        request.app.state.config.OPENAI_API_CONFIGS.get(url, {}),  # Legacy support
    )

    r = None
    session = None
    streaming = False

    headers, cookies = await get_headers_and_cookies(
        request, url, key, api_config, user=user
    )
    try:
        session = aiohttp.ClientSession(trust_env=True)
        r = await session.request(
            method="POST",
            url=f"{url}/embeddings",
            data=body,
            headers=headers,
            cookies=cookies,
        )

        if "text/event-stream" in r.headers.get("Content-Type", ""):
            streaming = True
            return StreamingResponse(
                r.content,
                status_code=r.status,
                headers=dict(r.headers),
                background=BackgroundTask(
                    cleanup_response, response=r, session=session
                ),
            )
        else:
            try:
                response_data = await r.json()
            except Exception:
                response_data = await r.text()

            if r.status >= 400:
                if isinstance(response_data, (dict, list)):
                    return JSONResponse(status_code=r.status, content=response_data)
                else:
                    return PlainTextResponse(
                        status_code=r.status, content=response_data
                    )

            return response_data
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=r.status if r else 500,
            detail="Open WebUI: Server Connection Error",
        )
    finally:
        if not streaming:
            await cleanup_response(r, session)


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(path: str, request: Request, user=Depends(get_verified_user)):
    """
    Deprecated: proxy all requests to OpenAI API
    """

    body = await request.body()

    idx = 0
    url = request.app.state.config.OPENAI_API_BASE_URLS[idx]
    key = request.app.state.config.OPENAI_API_KEYS[idx]
    api_config = request.app.state.config.OPENAI_API_CONFIGS.get(
        str(idx),
        request.app.state.config.OPENAI_API_CONFIGS.get(
            request.app.state.config.OPENAI_API_BASE_URLS[idx], {}
        ),  # Legacy support
    )

    r = None
    session = None
    streaming = False

    try:
        headers, cookies = await get_headers_and_cookies(
            request, url, key, api_config, user=user
        )

        if api_config.get("azure", False):
            api_version = api_config.get("api_version", "2023-03-15-preview")

            # Only set api-key header if not using Azure Entra ID authentication
            auth_type = api_config.get("auth_type", "bearer")
            if auth_type not in ("azure_ad", "microsoft_entra_id"):
                headers["api-key"] = key

            headers["api-version"] = api_version

            payload = json.loads(body)
            url, payload = convert_to_azure_payload(url, payload, api_version)
            body = json.dumps(payload).encode()

            request_url = f"{url}/{path}?api-version={api_version}"
        else:
            request_url = f"{url}/{path}"

        session = aiohttp.ClientSession(trust_env=True)
        r = await session.request(
            method=request.method,
            url=request_url,
            data=body,
            headers=headers,
            cookies=cookies,
            ssl=AIOHTTP_CLIENT_SESSION_SSL,
        )

        # Check if response is SSE
        if "text/event-stream" in r.headers.get("Content-Type", ""):
            streaming = True
            return StreamingResponse(
                r.content,
                status_code=r.status,
                headers=dict(r.headers),
                background=BackgroundTask(
                    cleanup_response, response=r, session=session
                ),
            )
        else:
            try:
                response_data = await r.json()
            except Exception:
                response_data = await r.text()

            if r.status >= 400:
                if isinstance(response_data, (dict, list)):
                    return JSONResponse(status_code=r.status, content=response_data)
                else:
                    return PlainTextResponse(
                        status_code=r.status, content=response_data
                    )

            return response_data

    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=r.status if r else 500,
            detail="Open WebUI: Server Connection Error",
        )
    finally:
        if not streaming:
            await cleanup_response(r, session)
