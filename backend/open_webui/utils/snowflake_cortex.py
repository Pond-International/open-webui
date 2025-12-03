"""
Snowflake Cortex Search Integration
用于在聊天请求处理前，先从 Snowflake Cortex Search 中搜索相关结果
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

log = logging.getLogger(__name__)

# 尝试导入 Snowflake 相关库
try:
    from snowflake.core import Root
    from snowflake.snowpark import Session
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False
    log.warning("Snowflake libraries not available. Install with: pip install snowflake-snowpark-python cryptography")

# 尝试加载环境变量
try:
    from dotenv import load_dotenv
    project_root = Path(__file__).parent.parent.parent
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        log.info(f"Loaded environment variables from: {env_file}")
except ImportError:
    log.warning("python-dotenv not installed, using system environment variables")


class SnowflakeCortexSearch:
    """Snowflake Cortex Search 客户端"""
    
    def __init__(self):
        if not SNOWFLAKE_AVAILABLE:
            raise RuntimeError("Snowflake libraries not available")
        
        # 从环境变量读取配置
        self.account = os.getenv("SNOWFLAKE_ACCOUNT", "")
        self.user = os.getenv("SNOWFLAKE_USER", "")
        self.password = os.getenv("SNOWFLAKE_PASSWORD", "")
        self.role = os.getenv("SNOWFLAKE_ROLE", "")
        self.warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "")
        self.database = os.getenv("SNOWFLAKE_DATABASE", "")
        self.schema = os.getenv("SNOWFLAKE_SCHEMA", "")
        self.cortex_service = os.getenv("SNOWFLAKE_CORTEX_SERVICE", "")
        self.private_key_pem = os.getenv("SNOWFLAKE_PRIVATE_KEY_PEM", "")
        
        # 检查必要配置
        if not self.cortex_service:
            raise ValueError("SNOWFLAKE_CORTEX_SERVICE not set")
        
        self.session = None
        self.root = None
        self.service = None
        self._initialized = False
    
    def _initialize(self):
        """初始化 Snowflake 连接"""
        if self._initialized:
            return
        
        # 构建连接参数
        connection_params = {
            "account": self.account,
            "user": self.user,
            "role": self.role,
            "warehouse": self.warehouse,
            "database": self.database,
            "schema": self.schema,
        }
        
        # 优先使用私钥认证（更安全）
        if self.private_key_pem:
            try:
                private_key = serialization.load_pem_private_key(
                    self.private_key_pem.encode("utf-8"),
                    password=None,
                    backend=default_backend(),
                )
                private_key_bytes = private_key.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
                connection_params["private_key"] = private_key_bytes
                connection_params["authenticator"] = "SNOWFLAKE_JWT"
                log.info("Using private key authentication")
            except Exception as e:
                log.error(f"Private key authentication failed: {e}")
                if self.password:
                    connection_params["password"] = self.password
                    log.info("Falling back to password authentication")
                else:
                    raise RuntimeError("Private key authentication failed and SNOWFLAKE_PASSWORD not set")
        elif self.password:
            connection_params["password"] = self.password
            log.info("Using password authentication")
        else:
            raise RuntimeError("Must set either SNOWFLAKE_PRIVATE_KEY_PEM or SNOWFLAKE_PASSWORD")
        
        # 创建会话
        log.info(f"Connecting to Snowflake account: {self.account}")
        self.session = Session.builder.configs(connection_params).create()
        self.root = Root(self.session)
        
        # 获取 Cortex Search Service
        self.service = (
            self.root
            .databases[self.database]
            .schemas[self.schema]
            .cortex_search_services[self.cortex_service]
        )
        
        log.info(f"Cortex Search Service '{self.cortex_service}' loaded")
        self._initialized = True
    
    def search(
        self,
        query: str,
        columns: Optional[List[str]] = None,
        limit: int = 3
    ) -> Optional[Dict[str, Any]]:
        """
        执行 Cortex Search 查询
        
        Args:
            query: 搜索查询字符串
            columns: 要返回的列（默认：["CONTENT", "FILE_NAME", "FILE_SOURCE"]）
            limit: 返回结果数量限制（默认：3）
        
        Returns:
            搜索结果字典，如果出错则返回 None
        """
        if not SNOWFLAKE_AVAILABLE:
            log.warning("Snowflake libraries not available, skipping search")
            return None
        
        try:
            self._initialize()
            
            if columns is None:
                columns = ["CONTENT", "FILE_NAME", "FILE_SOURCE"]
            
            log.info(f"Executing Snowflake Cortex Search query: {query}")
            resp = self.service.search(
                query=query,
                columns=columns,
                limit=limit,
            )
            
            # 转换为 JSON 格式
            # to_json() 返回的是字符串，需要解析为字典
            json_str = resp.to_json()
            if isinstance(json_str, str):
                result = json.loads(json_str)
            else:
                # 如果已经是字典，直接使用
                result = json_str
            
            # 确保结果是字典格式
            if not isinstance(result, dict):
                log.error(f"Unexpected result type: {type(result)}, value: {result}")
                return None
            
            log.info(f"Snowflake search completed, found {len(result.get('results', []))} results")
            return result
            
        except Exception as e:
            log.error(f"Error executing Snowflake Cortex Search: {e}")
            return None
    
    def format_search_results(self, search_results: Dict[str, Any]) -> str:
        """
        格式化搜索结果，用于添加到用户消息中
        
        Args:
            search_results: 搜索结果字典
        
        Returns:
            格式化后的字符串
        """
        if not search_results or "results" not in search_results:
            return ""
        
        results = search_results.get("results", [])
        if not results:
            return ""
        
        formatted_parts = ["\n\n=== Snowflake Cortex Search Results ===\n"]
        
        for idx, result in enumerate(results, 1):
            content = result.get("CONTENT", "")
            file_name = result.get("FILE_NAME", "Unknown")
            file_source = result.get("FILE_SOURCE", "Unknown")
            
            formatted_parts.append(f"[Result {idx}]\n")
            formatted_parts.append(f"Source: {file_source} / {file_name}\n")
            formatted_parts.append(f"Content: {content}\n")
            formatted_parts.append("\n")
        
        formatted_parts.append("=== End of Search Results ===\n")
        
        return "\n".join(formatted_parts)
    
    def close(self):
        """关闭 Snowflake 会话"""
        if self.session:
            try:
                self.session.close()
                log.info("Snowflake session closed")
            except Exception as e:
                log.error(f"Error closing Snowflake session: {e}")
            finally:
                self.session = None
                self._initialized = False


# 全局单例实例
_snowflake_client: Optional[SnowflakeCortexSearch] = None


def get_snowflake_client() -> Optional[SnowflakeCortexSearch]:
    """获取 Snowflake Cortex Search 客户端单例"""
    global _snowflake_client
    
    if _snowflake_client is None:
        try:
            _snowflake_client = SnowflakeCortexSearch()
        except Exception as e:
            log.warning(f"Failed to initialize Snowflake Cortex Search: {e}")
            return None
    
    return _snowflake_client


async def search_snowflake_cortex(query: str, limit: int = 3) -> Optional[str]:
    """
    执行 Snowflake Cortex Search 并返回格式化结果
    
    Args:
        query: 搜索查询
        limit: 结果数量限制
    
    Returns:
        格式化后的搜索结果字符串，如果出错则返回 None
    """
    client = get_snowflake_client()
    if not client:
        return None
    
    try:
        results = client.search(query=query, limit=limit)
        if results:
            return client.format_search_results(results)
        return None
    except Exception as e:
        log.error(f"Error in search_snowflake_cortex: {e}")
        return None
