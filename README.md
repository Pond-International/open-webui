# Open WebUI 👋

![GitHub stars](https://img.shields.io/github/stars/open-webui/open-webui?style=social)
![GitHub forks](https://img.shields.io/github/forks/open-webui/open-webui?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/open-webui/open-webui?style=social)
![GitHub repo size](https://img.shields.io/github/repo-size/open-webui/open-webui)
![GitHub language count](https://img.shields.io/github/languages/count/open-webui/open-webui)
![GitHub top language](https://img.shields.io/github/languages/top/open-webui/open-webui)
![GitHub last commit](https://img.shields.io/github/last-commit/open-webui/open-webui?color=red)
[![Discord](https://img.shields.io/badge/Discord-Open_WebUI-blue?logo=discord&logoColor=white)](https://discord.gg/5rJgQTnV4s)
[![](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86)](https://github.com/sponsors/tjbck)

**Open WebUI is an [extensible](https://docs.openwebui.com/features/plugin/), feature-rich, and user-friendly self-hosted AI platform designed to operate entirely offline.** It supports various LLM runners like **Ollama** and **OpenAI-compatible APIs**, with **built-in inference engine** for RAG, making it a **powerful AI deployment solution**.

Passionate about open-source AI? [Join our team →](https://careers.openwebui.com/)

![Open WebUI Demo](./demo.gif)

> [!TIP]  
> **Looking for an [Enterprise Plan](https://docs.openwebui.com/enterprise)?** – **[Speak with Our Sales Team Today!](https://docs.openwebui.com/enterprise)**
>
> Get **enhanced capabilities**, including **custom theming and branding**, **Service Level Agreement (SLA) support**, **Long-Term Support (LTS) versions**, and **more!**

For more information, be sure to check out our [Open WebUI Documentation](https://docs.openwebui.com/).

## Key Features of Open WebUI ⭐

- 🚀 **Effortless Setup**: Install seamlessly using Docker or Kubernetes (kubectl, kustomize or helm) for a hassle-free experience with support for both `:ollama` and `:cuda` tagged images.

- 🤝 **Ollama/OpenAI API Integration**: Effortlessly integrate OpenAI-compatible APIs for versatile conversations alongside Ollama models. Customize the OpenAI API URL to link with **LMStudio, GroqCloud, Mistral, OpenRouter, and more**.

- 🛡️ **Granular Permissions and User Groups**: By allowing administrators to create detailed user roles and permissions, we ensure a secure user environment. This granularity not only enhances security but also allows for customized user experiences, fostering a sense of ownership and responsibility amongst users.

- 📱 **Responsive Design**: Enjoy a seamless experience across Desktop PC, Laptop, and Mobile devices.

- 📱 **Progressive Web App (PWA) for Mobile**: Enjoy a native app-like experience on your mobile device with our PWA, providing offline access on localhost and a seamless user interface.

- ✒️🔢 **Full Markdown and LaTeX Support**: Elevate your LLM experience with comprehensive Markdown and LaTeX capabilities for enriched interaction.

- 🎤📹 **Hands-Free Voice/Video Call**: Experience seamless communication with integrated hands-free voice and video call features using multiple Speech-to-Text providers (Local Whisper, OpenAI, Deepgram, Azure) and Text-to-Speech engines (Azure, ElevenLabs, OpenAI, Transformers, WebAPI), allowing for dynamic and interactive chat environments.

- 🛠️ **Model Builder**: Easily create Ollama models via the Web UI. Create and add custom characters/agents, customize chat elements, and import models effortlessly through [Open WebUI Community](https://openwebui.com/) integration.

- 🐍 **Native Python Function Calling Tool**: Enhance your LLMs with built-in code editor support in the tools workspace. Bring Your Own Function (BYOF) by simply adding your pure Python functions, enabling seamless integration with LLMs.

- 💾 **Persistent Artifact Storage**: Built-in key-value storage API for artifacts, enabling features like journals, trackers, leaderboards, and collaborative tools with both personal and shared data scopes across sessions.

- 📚 **Local RAG Integration**: Dive into the future of chat interactions with groundbreaking Retrieval Augmented Generation (RAG) support using your choice of 9 vector databases and multiple content extraction engines (Tika, Docling, Document Intelligence, Mistral OCR, External loaders). Load documents directly into chat or add files to your document library, effortlessly accessing them using the `#` command before a query.

- 🔍 **Web Search for RAG**: Perform web searches using 15+ providers including `SearXNG`, `Google PSE`, `Brave Search`, `Kagi`, `Mojeek`, `Tavily`, `Perplexity`, `serpstack`, `serper`, `Serply`, `DuckDuckGo`, `SearchApi`, `SerpApi`, `Bing`, `Jina`, `Exa`, `Sougou`, `Azure AI Search`, and `Ollama Cloud`, injecting results directly into your chat experience.

- 🌐 **Web Browsing Capability**: Seamlessly integrate websites into your chat experience using the `#` command followed by a URL. This feature allows you to incorporate web content directly into your conversations, enhancing the richness and depth of your interactions.

- 🎨 **Image Generation & Editing Integration**: Create and edit images using multiple engines including OpenAI's DALL-E, Gemini, ComfyUI (local), and AUTOMATIC1111 (local), with support for both generation and prompt-based editing workflows.

- ⚙️ **Many Models Conversations**: Effortlessly engage with various models simultaneously, harnessing their unique strengths for optimal responses. Enhance your experience by leveraging a diverse set of models in parallel.

- 🔐 **Role-Based Access Control (RBAC)**: Ensure secure access with restricted permissions; only authorized individuals can access your Ollama, and exclusive model creation/pulling rights are reserved for administrators.

- 🗄️ **Flexible Database & Storage Options**: Choose from SQLite (with optional encryption), PostgreSQL, or configure cloud storage backends (S3, Google Cloud Storage, Azure Blob Storage) for scalable deployments.

- 🔍 **Advanced Vector Database Support**: Select from 9 vector database options including ChromaDB, PGVector, Qdrant, Milvus, Elasticsearch, OpenSearch, Pinecone, S3Vector, and Oracle 23ai for optimal RAG performance.

- 🔐 **Enterprise Authentication**: Full support for LDAP/Active Directory integration, SCIM 2.0 automated provisioning, and SSO via trusted headers alongside OAuth providers. Enterprise-grade user and group provisioning through SCIM 2.0 protocol, enabling seamless integration with identity providers like Okta, Azure AD, and Google Workspace for automated user lifecycle management.

- ☁️ **Cloud-Native Integration**: Native support for Google Drive and OneDrive/SharePoint file picking, enabling seamless document import from enterprise cloud storage.

- 📊 **Production Observability**: Built-in OpenTelemetry support for traces, metrics, and logs, enabling comprehensive monitoring with your existing observability stack.

- ⚖️ **Horizontal Scalability**: Redis-backed session management and WebSocket support for multi-worker and multi-node deployments behind load balancers.

- 🌐🌍 **Multilingual Support**: Experience Open WebUI in your preferred language with our internationalization (i18n) support. Join us in expanding our supported languages! We're actively seeking contributors!

- 🧩 **Pipelines, Open WebUI Plugin Support**: Seamlessly integrate custom logic and Python libraries into Open WebUI using [Pipelines Plugin Framework](https://github.com/open-webui/pipelines). Launch your Pipelines instance, set the OpenAI URL to the Pipelines URL, and explore endless possibilities. [Examples](https://github.com/open-webui/pipelines/tree/main/examples) include **Function Calling**, User **Rate Limiting** to control access, **Usage Monitoring** with tools like Langfuse, **Live Translation with LibreTranslate** for multilingual support, **Toxic Message Filtering** and much more.

- 🌟 **Continuous Updates**: We are committed to improving Open WebUI with regular updates, fixes, and new features.

Want to learn more about Open WebUI's features? Check out our [Open WebUI documentation](https://docs.openwebui.com/features) for a comprehensive overview!

---

We are incredibly grateful for the generous support of our sponsors. Their contributions help us to maintain and improve our project, ensuring we can continue to deliver quality work to our community. Thank you!

## How to Install 🚀

### Installation via Python pip 🐍

Open WebUI can be installed using pip, the Python package installer. Before proceeding, ensure you're using **Python 3.11** to avoid compatibility issues.

1. **Install Open WebUI**:
   Open your terminal and run the following command to install Open WebUI:

   ```bash
   pip install open-webui
   ```

2. **Running Open WebUI**:
   After installation, you can start Open WebUI by executing:

   ```bash
   open-webui serve
   ```

This will start the Open WebUI server, which you can access at [http://localhost:8080](http://localhost:8080)

### Quick Start with Docker 🐳

> [!NOTE]  
> Please note that for certain Docker environments, additional configurations might be needed. If you encounter any connection issues, our detailed guide on [Open WebUI Documentation](https://docs.openwebui.com/) is ready to assist you.

> [!WARNING]
> When using Docker to install Open WebUI, make sure to include the `-v open-webui:/app/backend/data` in your Docker command. This step is crucial as it ensures your database is properly mounted and prevents any loss of data.

> [!TIP]  
> If you wish to utilize Open WebUI with Ollama included or CUDA acceleration, we recommend utilizing our official images tagged with either `:cuda` or `:ollama`. To enable CUDA, you must install the [Nvidia CUDA container toolkit](https://docs.nvidia.com/dgx/nvidia-container-runtime-upgrade/) on your Linux/WSL system.

### Installation with Default Configuration

- **If Ollama is on your computer**, use this command:

  ```bash
  docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
  ```

- **If Ollama is on a Different Server**, use this command:

  To connect to Ollama on another server, change the `OLLAMA_BASE_URL` to the server's URL:

  ```bash
  docker run -d -p 3000:8080 -e OLLAMA_BASE_URL=https://example.com -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
  ```

- **To run Open WebUI with Nvidia GPU support**, use this command:

  ```bash
  docker run -d -p 3000:8080 --gpus all --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:cuda
  ```

### Installation for OpenAI API Usage Only

- **If you're only using OpenAI API**, use this command:

  ```bash
  docker run -d -p 3000:8080 -e OPENAI_API_KEY=your_secret_key -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
  ```

### Installing Open WebUI with Bundled Ollama Support

This installation method uses a single container image that bundles Open WebUI with Ollama, allowing for a streamlined setup via a single command. Choose the appropriate command based on your hardware setup:

- **With GPU Support**:
  Utilize GPU resources by running the following command:

  ```bash
  docker run -d -p 3000:8080 --gpus=all -v ollama:/root/.ollama -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:ollama
  ```

- **For CPU Only**:
  If you're not using a GPU, use this command instead:

  ```bash
  docker run -d -p 3000:8080 -v ollama:/root/.ollama -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:ollama
  ```

Both commands facilitate a built-in, hassle-free installation of both Open WebUI and Ollama, ensuring that you can get everything up and running swiftly.

After installation, you can access Open WebUI at [http://localhost:3000](http://localhost:3000). Enjoy! 😄

### Other Installation Methods

We offer various installation alternatives, including non-Docker native installation methods, Docker Compose, Kustomize, and Helm. Visit our [Open WebUI Documentation](https://docs.openwebui.com/getting-started/) or join our [Discord community](https://discord.gg/5rJgQTnV4s) for comprehensive guidance.

Look at the [Local Development Guide](https://docs.openwebui.com/getting-started/advanced-topics/development) for instructions on setting up a local development environment.

### Troubleshooting

Encountering connection issues? Our [Open WebUI Documentation](https://docs.openwebui.com/troubleshooting/) has got you covered. For further assistance and to join our vibrant community, visit the [Open WebUI Discord](https://discord.gg/5rJgQTnV4s).

#### Open WebUI: Server Connection Error

If you're experiencing connection issues, it’s often due to the WebUI docker container not being able to reach the Ollama server at 127.0.0.1:11434 (host.docker.internal:11434) inside the container . Use the `--network=host` flag in your docker command to resolve this. Note that the port changes from 3000 to 8080, resulting in the link: `http://localhost:8080`.

**Example Docker Command**:

```bash
docker run -d --network=host -v open-webui:/app/backend/data -e OLLAMA_BASE_URL=http://127.0.0.1:11434 --name open-webui --restart always ghcr.io/open-webui/open-webui:main
```

### Keeping Your Docker Installation Up-to-Date

In case you want to update your local Docker installation to the latest version, you can do it with [Watchtower](https://containrrr.dev/watchtower/):

```bash
docker run --rm --volume /var/run/docker.sock:/var/run/docker.sock containrrr/watchtower --run-once open-webui
```

In the last part of the command, replace `open-webui` with your container name if it is different.

Check our Updating Guide available in our [Open WebUI Documentation](https://docs.openwebui.com/getting-started/updating).

### Using the Dev Branch 🌙

> [!WARNING]
> The `:dev` branch contains the latest unstable features and changes. Use it at your own risk as it may have bugs or incomplete features.

If you want to try out the latest bleeding-edge features and are okay with occasional instability, you can use the `:dev` tag like this:

```bash
docker run -d -p 3000:8080 -v open-webui:/app/backend/data --name open-webui --add-host=host.docker.internal:host-gateway --restart always ghcr.io/open-webui/open-webui:dev
```

### Offline Mode

If you are running Open WebUI in an offline environment, you can set the `HF_HUB_OFFLINE` environment variable to `1` to prevent attempts to download models from the internet.

```bash
export HF_HUB_OFFLINE=1
```

## Crypto Pond 知识库 RAG 系统 🚀

本项目基于 Open WebUI 扩展，集成了 **Snowflake Cortex Search** 和 **OpenAI GPT-4.1-mini**，为 Crypto Pond 平台提供智能知识库问答服务。

### 技术选型说明

本次架构设计基于支持 **3 个独立项目（Project）**（约 **50 个以内的内部用户**）的使用场景。选用 **Open WebUI** 作为前端多用户聊天界面方案，主要考虑：

- 前后端结合且开源、可自部署，易于二次开发与集成
- 原生支持多用户、工作区（Workspace）与 API 接口扩展
- 技术栈为 **Python + FastAPI + React**

> **注意**：Open WebUI 并非唯一或最佳方案。由于其后端基于 Python + FastAPI，而团队当前后端工程主要是 **Go 相关**，因此在未来可以根据项目增长和性能需求收敛技术栈，评估替换或自研基于 Go 的多用户 Chat 平台，或引入更成熟的企业级开源方案。本方案旨在提供一个 **可快速落地验证的基线架构（MVP）**。

### 相关文档

- **Open WebUI**: [https://docs.openwebui.com/](https://docs.openwebui.com/)
- **Snowflake Cortex Search Service**: [https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/query-cortex-search-service](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/query-cortex-search-service)

### 系统架构

```
┌────────────────────────────┐
│          用户前端          │
│ cryptopond.xyz（嵌入按钮） │
└─────────────┬──────────────┘
              │ user_id / email
              ▼
┌────────────────────────────┐
│        Open WebUI 层       │
│ - 承载聊天界面               │
│ - 后端交互                  │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│  授权验证 & 中间服务层     │
│ - 校验 user_id 是否属于审核项目成员 │
│ - 生成会话上下文           │
│ - 调用搜索与生成模块       │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────────────┐
│       数据与智能处理层（RAG）      │
│                                    │
│ ┌──────────────┐   ┌──────────────┐ │
│ │ Snowflake     │   │ OpenAI GPT‑4.1-mini │ │
│ │ Cortex Search │   │ (LLM生成回答)       │ │
│ └──────────────┘   └──────────────┘ │
│   ↑ 向量检索结果     ↓ 上下文生成回答     │
└────────────────────────────────────┘
              │
              ▼
┌────────────────────────────┐
│        Open WebUI 前端     │
│ 展示回答、引用、上下文来源 │
└────────────────────────────┘
```

### 数据流程

| 流程阶段 | 输入 | 输出 | 说明 |
| --- | --- | --- | --- |
| ① 用户访问 | user_id / email | — | 用户在 cryptopond.xyz 触发 Open WebUI |
| ② 授权验证 | user_id | 是否有权限 | 后端查询业务库确认是否为过审项目的成员 |
| ③ 语义检索 | user_id + 用户问题 | Top 4 语义匹配文档 | 调用 Snowflake Cortex Search 检索知识片段 |
| ④ 上下文拼接 | 检索结果 + 用户问题 | prompt context | 将结果组织成系统提示上下文 |
| ⑤ 模型生成 | prompt context | 回答文本 | GPT‑4.1-mini 生成自然语言回答 |
| ⑥ 前端展示 | 回答 + 来源信息 | 可视化展示 | Open WebUI 展示回答与引用来源 |

### 已实现功能 ✅

1. **Snowflake Cortex Search 集成** - 已完成
   - `backend/open_webui/utils/snowflake_cortex.py` 已实现搜索功能
   - `backend/open_webui/routers/openai.py` 已集成到聊天流程

2. **搜索结果合并到 Prompt** - 已完成
   - `enhance_payload_with_snowflake_search()` 函数已实现

3. **知识库标记** - 已完成
   - 流式和非流式响应都已添加标记

4. **基础用户认证** - Open WebUI 自带
   - `get_verified_user` 依赖已存在

### 待实现功能 ❌

#### 高优先级（核心功能）

1. **项目成员验证服务层**
   - 位置: `backend/open_webui/routers/auths.py` 或新建 `backend/open_webui/routers/project_auth.py`
   - 需要实现:
     - 创建 API 端点验证 user_id/email 是否为审核项目成员
     - 集成业务数据库（需要确定数据库类型和连接方式）
     - 实现项目成员查询逻辑
     - 添加中间件在请求处理前进行验证

2. **用户过滤功能**
   - 位置: `backend/open_webui/utils/snowflake_cortex.py`
   - 需要实现:
     - 修改 `search_snowflake_cortex()` 函数，接受 `user_id` 或 `email` 参数
     - 在 Snowflake 查询中添加用户过滤条件（如果 Snowflake 表中有用户字段）
     - 或者在后处理阶段过滤结果

3. **来源信息提取和传递**
   - 位置: `backend/open_webui/utils/snowflake_cortex.py` 和 `backend/open_webui/routers/openai.py`
   - 需要实现:
     - 修改 `search_snowflake_cortex()` 返回结构化数据（包含来源信息）
     - 在响应中添加 `sources` 字段（参考 Open WebUI 现有的 citations 格式）
     - 确保前端能正确解析和显示来源

#### 中优先级（增强功能）

4. **前端嵌入集成**
   - 位置: 新建 `src/lib/components/embed/` 或修改现有组件
   - 需要实现:
     - 创建嵌入式聊天组件（iframe 或 widget）
     - 实现从 cryptopond.xyz 传递 user_id/email 的机制
     - 处理跨域认证和会话管理
     - 样式适配（嵌入式场景）

5. **环境变量和配置**
   - 位置: `backend/open_webui/env.py` 和 `.env.example`
   - 需要添加:
     - `PROJECT_DB_URL` - 业务数据库连接字符串
     - `PROJECT_DB_TYPE` - 数据库类型（MySQL/PostgreSQL/MongoDB等）
     - `ENABLE_PROJECT_AUTH` - 是否启用项目成员验证
     - `CRYPTOPOND_EMBED_SECRET` - 嵌入式认证密钥（可选）

#### 低优先级（优化功能）

6. **日志和监控**
   - 位置: `backend/open_webui/routers/openai.py`
   - 需要添加:
     - 项目成员验证的日志记录
     - 用户过滤的日志记录
     - 来源信息提取的日志记录

### 技术决策点

在开始实现前，需要确认以下信息：

1. **业务数据库类型**: 需要确认是 MySQL、PostgreSQL 还是其他
2. **项目成员表结构**: 需要确认表名、字段名（user_id, email, project_id 等）
3. **Snowflake 表结构**: 需要确认是否有用户字段可用于过滤
4. **嵌入式认证方式**: JWT token、API key 还是其他方式
5. **来源信息格式**: 需要确认 Snowflake 返回的数据结构，如何提取来源

### 配置说明

#### Snowflake Cortex Search 配置

在 `.env` 文件中配置以下环境变量：

```bash
# Snowflake 连接配置
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_PRIVATE_KEY_PEM=your_private_key  # 可选，优先使用私钥认证
SNOWFLAKE_ROLE=your_role
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
SNOWFLAKE_CORTEX_SERVICE=your_cortex_service_name

# RAG 相关配置
OPENAI_MODEL=gpt-4.1-mini
RAG_CONTEXT_LIMIT=4000
ENABLE_USER_EMAIL_FILTER=false
```

#### 项目成员验证配置（待实现）

```bash
# 项目成员验证配置
ENABLE_PROJECT_AUTH=true
PROJECT_DB_URL=mysql://user:password@host:port/database
PROJECT_DB_TYPE=mysql  # 或 postgresql, http_api
PROJECT_MEMBERS_TABLE=project_members
PROJECT_MEMBERS_USER_ID_COLUMN=user_id
PROJECT_MEMBERS_EMAIL_COLUMN=email
PROJECT_MEMBERS_STATUS_COLUMN=status
PROJECT_MEMBERS_APPROVED_STATUS=approved
```

## What's Next? 🌟

Discover upcoming features on our roadmap in the [Open WebUI Documentation](https://docs.openwebui.com/roadmap/).

## License 📜

This project contains code under multiple licenses. The current codebase includes components licensed under the Open WebUI License with an additional requirement to preserve the "Open WebUI" branding, as well as prior contributions under their respective original licenses. For a detailed record of license changes and the applicable terms for each section of the code, please refer to [LICENSE_HISTORY](./LICENSE_HISTORY). For complete and updated licensing details, please see the [LICENSE](./LICENSE) and [LICENSE_HISTORY](./LICENSE_HISTORY) files.

## Support 💬

If you have any questions, suggestions, or need assistance, please open an issue or join our
[Open WebUI Discord community](https://discord.gg/5rJgQTnV4s) to connect with us! 🤝

## Star History

<a href="https://star-history.com/#open-webui/open-webui&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=open-webui/open-webui&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=open-webui/open-webui&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=open-webui/open-webui&type=Date" />
  </picture>
</a>

---

Created by [Timothy Jaeryang Baek](https://github.com/tjbck) - Let's make Open WebUI even more amazing together! 💪
