# Crypto Pond 知识库 RAG 系统 🚀

本项目基于 [Open WebUI](https://github.com/open-webui/open-webui) 扩展，集成了 **Snowflake Cortex Search** 和 **OpenAI GPT-4.1-mini**，为 Crypto Pond 平台提供智能知识库问答服务。

> **关于 Open WebUI**  
> 本项目基于开源项目 [Open WebUI](https://github.com/open-webui/open-webui) 进行二次开发。  
> - GitHub: [https://github.com/open-webui/open-webui](https://github.com/open-webui/open-webui)  
> - 官方文档: [https://docs.openwebui.com/](https://docs.openwebui.com/)  
> - 官方 Discord: [https://discord.gg/5rJgQTnV4s](https://discord.gg/5rJgQTnV4s)

## 项目目的

本项目旨在为 Crypto Pond 平台构建一个智能知识库问答系统，通过集成 Snowflake Cortex Search 实现语义检索，结合 OpenAI GPT-4.1-mini 生成自然语言回答，为平台用户提供基于知识库的智能问答服务。

## 快速开始

### 使用 Docker 安装

```bash
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
```

安装完成后，访问 [http://localhost:3000](http://localhost:3000) 即可使用。

> **注意**: 使用 Docker 安装时，请确保包含 `-v open-webui:/app/backend/data` 参数，以确保数据持久化。

更多安装方式请参考 [Open WebUI 官方文档](https://docs.openwebui.com/getting-started/).

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

---

## English Version

# Crypto Pond Knowledge Base RAG System 🚀

This project extends [Open WebUI](https://github.com/open-webui/open-webui) and integrates **Snowflake Cortex Search** and **OpenAI GPT-4.1-mini** to provide intelligent knowledge base Q&A services for the Crypto Pond platform.

> **About Open WebUI**  
> This project is a fork of the open-source project [Open WebUI](https://github.com/open-webui/open-webui).  
> - GitHub: [https://github.com/open-webui/open-webui](https://github.com/open-webui/open-webui)  
> - Official Documentation: [https://docs.openwebui.com/](https://docs.openwebui.com/)  
> - Official Discord: [https://discord.gg/5rJgQTnV4s](https://discord.gg/5rJgQTnV4s)

## Project Purpose

This project aims to build an intelligent knowledge base Q&A system for the Crypto Pond platform. By integrating Snowflake Cortex Search for semantic retrieval and combining it with OpenAI GPT-4.1-mini for natural language generation, it provides intelligent Q&A services based on the knowledge base for platform users.

## Quick Start

### Installation with Docker

```bash
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
```

After installation, access [http://localhost:3000](http://localhost:3000) to use the system.

> **Note**: When installing with Docker, make sure to include the `-v open-webui:/app/backend/data` parameter to ensure data persistence.

For more installation methods, please refer to the [Open WebUI Official Documentation](https://docs.openwebui.com/getting-started/).

### Technical Selection

This architecture is designed to support **3 independent projects** (approximately **50 internal users**). **Open WebUI** is chosen as the frontend multi-user chat interface solution, primarily considering:

- Full-stack open-source solution that can be self-deployed, easy for secondary development and integration
- Native support for multi-user, workspace, and API interface extensions
- Technology stack: **Python + FastAPI + React**

> **Note**: Open WebUI is not the only or best solution. Since its backend is based on Python + FastAPI, while the team's current backend engineering is primarily **Go-related**, we can evaluate replacing or developing a Go-based multi-user Chat platform in the future based on project growth and performance requirements, or introduce more mature enterprise-grade open-source solutions. This solution aims to provide a **baseline architecture (MVP) that can be quickly validated**.

### Related Documentation

- **Open WebUI**: [https://docs.openwebui.com/](https://docs.openwebui.com/)
- **Snowflake Cortex Search Service**: [https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/query-cortex-search-service](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/query-cortex-search-service)

### System Architecture

```
┌────────────────────────────┐
│      User Frontend         │
│ cryptopond.xyz (Embedded)  │
└─────────────┬──────────────┘
              │ user_id / email
              ▼
┌────────────────────────────┐
│      Open WebUI Layer      │
│ - Chat Interface           │
│ - Backend Interaction      │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│ Auth & Middleware Layer     │
│ - Verify user_id membership│
│ - Generate session context │
│ - Call search & generation │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────────────┐
│   Data & AI Processing (RAG)      │
│                                    │
│ ┌──────────────┐   ┌──────────────┐ │
│ │ Snowflake     │   │ OpenAI GPT‑4.1-mini │ │
│ │ Cortex Search │   │ (LLM Answer)        │ │
│ └──────────────┘   └──────────────┘ │
│   ↑ Vector Results  ↓ Context Answer│
└────────────────────────────────────┘
              │
              ▼
┌────────────────────────────┐
│      Open WebUI Frontend   │
│ Display Answer & Sources   │
└────────────────────────────┘
```

### Data Flow

| Stage | Input | Output | Description |
| --- | --- | --- | --- |
| ① User Access | user_id / email | — | User triggers Open WebUI from cryptopond.xyz |
| ② Authorization | user_id | Permission Status | Backend queries business DB to verify approved project membership |
| ③ Semantic Search | user_id + user query | Top 4 semantic matches | Call Snowflake Cortex Search to retrieve knowledge fragments |
| ④ Context Assembly | Search results + user query | prompt context | Organize results into system prompt context |
| ⑤ Model Generation | prompt context | Answer text | GPT‑4.1-mini generates natural language answer |
| ⑥ Frontend Display | Answer + source info | Visual display | Open WebUI displays answer and citation sources |

### Implemented Features ✅

1. **Snowflake Cortex Search Integration** - Completed
   - `backend/open_webui/utils/snowflake_cortex.py` implements search functionality
   - `backend/open_webui/routers/openai.py` integrated into chat flow

2. **Search Results Merged into Prompt** - Completed
   - `enhance_payload_with_snowflake_search()` function implemented

3. **Knowledge Base Marker** - Completed
   - Both streaming and non-streaming responses include markers

4. **Basic User Authentication** - Built-in Open WebUI
   - `get_verified_user` dependency exists

### Pending Features ❌

#### High Priority (Core Features)

1. **Project Member Verification Service Layer**
   - Location: `backend/open_webui/routers/auths.py` or create new `backend/open_webui/routers/project_auth.py`
   - To implement:
     - Create API endpoint to verify if user_id/email is an approved project member
     - Integrate business database (need to determine database type and connection method)
     - Implement project member query logic
     - Add middleware for pre-request verification

2. **User Filtering Functionality**
   - Location: `backend/open_webui/utils/snowflake_cortex.py`
   - To implement:
     - Modify `search_snowflake_cortex()` function to accept `user_id` or `email` parameters
     - Add user filtering conditions in Snowflake queries (if user fields exist in Snowflake tables)
     - Or filter results in post-processing stage

3. **Source Information Extraction and Transmission**
   - Location: `backend/open_webui/utils/snowflake_cortex.py` and `backend/open_webui/routers/openai.py`
   - To implement:
     - Modify `search_snowflake_cortex()` to return structured data (including source information)
     - Add `sources` field in response (reference Open WebUI's existing citations format)
     - Ensure frontend can correctly parse and display sources

#### Medium Priority (Enhancement Features)

4. **Frontend Embedding Integration**
   - Location: Create new `src/lib/components/embed/` or modify existing components
   - To implement:
     - Create embedded chat component (iframe or widget)
     - Implement mechanism to pass user_id/email from cryptopond.xyz
     - Handle cross-origin authentication and session management
     - Style adaptation (embedded scenarios)

5. **Environment Variables and Configuration**
   - Location: `backend/open_webui/env.py` and `.env.example`
   - To add:
     - `PROJECT_DB_URL` - Business database connection string
     - `PROJECT_DB_TYPE` - Database type (MySQL/PostgreSQL/MongoDB, etc.)
     - `ENABLE_PROJECT_AUTH` - Enable project member verification
     - `CRYPTOPOND_EMBED_SECRET` - Embedded authentication secret (optional)

#### Low Priority (Optimization Features)

6. **Logging and Monitoring**
   - Location: `backend/open_webui/routers/openai.py`
   - To add:
     - Logging for project member verification
     - Logging for user filtering
     - Logging for source information extraction

### Technical Decision Points

Before implementation, the following information needs to be confirmed:

1. **Business Database Type**: Need to confirm if it's MySQL, PostgreSQL, or others
2. **Project Member Table Structure**: Need to confirm table name, field names (user_id, email, project_id, etc.)
3. **Snowflake Table Structure**: Need to confirm if user fields exist for filtering
4. **Embedded Authentication Method**: JWT token, API key, or other methods
5. **Source Information Format**: Need to confirm Snowflake's returned data structure and how to extract sources

### Configuration

#### Snowflake Cortex Search Configuration

Configure the following environment variables in the `.env` file:

```bash
# Snowflake Connection Configuration
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_PRIVATE_KEY_PEM=your_private_key  # Optional, private key authentication preferred
SNOWFLAKE_ROLE=your_role
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
SNOWFLAKE_CORTEX_SERVICE=your_cortex_service_name

# RAG Related Configuration
OPENAI_MODEL=gpt-4.1-mini
RAG_CONTEXT_LIMIT=4000
ENABLE_USER_EMAIL_FILTER=false
```

#### Project Member Verification Configuration (To Be Implemented)

```bash
# Project Member Verification Configuration
ENABLE_PROJECT_AUTH=true
PROJECT_DB_URL=mysql://user:password@host:port/database
PROJECT_DB_TYPE=mysql  # or postgresql, http_api
PROJECT_MEMBERS_TABLE=project_members
PROJECT_MEMBERS_USER_ID_COLUMN=user_id
PROJECT_MEMBERS_EMAIL_COLUMN=email
PROJECT_MEMBERS_STATUS_COLUMN=status
PROJECT_MEMBERS_APPROVED_STATUS=approved
```

## License 📜

This project contains code under multiple licenses. The current codebase includes components licensed under the Open WebUI License with an additional requirement to preserve the "Open WebUI" branding, as well as prior contributions under their respective original licenses. For a detailed record of license changes and the applicable terms for each section of the code, please refer to [LICENSE_HISTORY](./LICENSE_HISTORY). For complete and updated licensing details, please see the [LICENSE](./LICENSE) and [LICENSE_HISTORY](./LICENSE_HISTORY) files.
