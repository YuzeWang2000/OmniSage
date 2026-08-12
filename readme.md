# OmniSage

OmniSage 是一个以 FastAPI 为唯一业务后端、React 为 Web 客户端的 RAG 智能问答与知识工作台。它提供认证、会话、流式问答、知识库、文档索引、Wiki/知识库搜索和在线模型 API Key 管理。

## 架构

- `backend/`：Python、FastAPI、SQLAlchemy、LangChain、ChromaDB 与模型服务集成。
- `frontend/`：TypeScript strict、React、Vite、React Router、TanStack Query、Zustand、Tailwind CSS 与 shadcn/ui。
- `frontend-legacy/`：迁移前的 Gradio 前端，仅保留作回退和行为参考，不是默认入口。
- `FRONTEND_MIGRATION_PLAN.md`：旧功能审计、接口映射、保留行为与接口缺口。

React 只负责展示和交互；认证、对话持久化、检索、索引、Wiki 与模型调用仍由 FastAPI 完成，没有引入 Node.js 业务后端或 Next.js。

## 环境要求

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- Node.js 20.19+ 或 22.12+
- pnpm 11
- Ollama（使用本地模型、嵌入或知识库功能时）
- 可选：MySQL；未设置 `DATABASE_URL` 时后端使用本地 SQLite `omnisage.db`

## 启动后端

```bash
cd backend
uv sync
uv run python scripts/create_tables.py
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

启动后可访问：

- 健康检查：`http://127.0.0.1:8000/health`
- OpenAPI：`http://127.0.0.1:8000/openapi.json`
- Swagger UI：`http://127.0.0.1:8000/docs`

常用后端环境变量：

| 变量 | 说明 | 默认值 |
| --- | --- | --- |
| `DATABASE_URL` | SQLAlchemy 数据库连接 | `sqlite:///./omnisage.db` |
| `DATA_DIR` | 上传文件、向量库等数据根目录 | `.` |
| `OLLAMA_BASE_URL` | Ollama 地址 | `http://localhost:11434` |
| `DEFAULT_MODEL` | 默认聊天模型 | `gemma3n` |
| `EMBEDDING_MODEL` | 默认嵌入模型 | `nomic-embed-text` |
| `JWT_SECRET_KEY` | JWT 签名密钥；生产必须显式设置强随机值 | 本地进程临时随机值 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 有效期 | `1440` |
| `CORS_ALLOWED_ORIGINS` | 逗号分隔的允许来源 | 本地 Vite 两个来源 |
| `OPENAI_API_KEY` / `DEEPSEEK_API_KEY` | 可选全局在线模型密钥 | 未设置 |

生产环境必须显式配置 `JWT_SECRET_KEY`。不要把 `.env`、Token、密码或 API Key 提交到 Git。

## 启动 React 前端

```bash
cd frontend
pnpm install
copy .env.example .env.local
pnpm dev
```

浏览器访问 `http://127.0.0.1:5173`。开发环境默认使用 `/api` 并由 Vite 代理到 `http://127.0.0.1:8000`。

前端环境变量：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_DEV_PROXY_TARGET=http://127.0.0.1:8000
VITE_REQUEST_TIMEOUT_MS=30000
VITE_UPLOAD_TIMEOUT_MS=180000
VITE_CHAT_TIMEOUT_MS=120000
```

若不创建 `.env.local`，Vite 开发模式会自动使用 `/api` 代理。前后端分别部署在不同域名时，将 `VITE_API_BASE_URL` 设为浏览器可访问的绝对 API 地址，并把前端来源加入后端 `CORS_ALLOWED_ORIGINS`。生产环境与开发环境应使用独立的环境文件或构建参数。

## 构建与测试

在 `frontend/` 中执行：

```bash
pnpm install
pnpm typecheck
pnpm lint
pnpm test
pnpm build
pnpm exec playwright test
```

- Vitest/React Testing Library 覆盖认证表单、401、受保护路由、会话切换、安全 Markdown、RAG/Wiki、知识库空状态、搜索结果和 API Key 掩码。
- Playwright 覆盖登录/工作台、聊天与 SSE、停止生成、RAG/Wiki、知识库创建与上传、搜索详情、设置、退出及 390px 无横向溢出。
- E2E 使用可控网络拦截，不调用真实外部大模型；真实后端联调仍需单独启动 FastAPI 和所需 Ollama 模型。

更新 OpenAPI 类型：

```bash
pnpm generate:api
```

## Docker Compose

设置 MySQL 与 JWT 环境变量后运行：

```bash
docker compose up --build
```

生产前端由 Nginx 暴露在 `http://localhost:7860`，同源 `/api/` 代理到 FastAPI，并关闭聊天流的代理缓冲。Compose 会拒绝缺少 `JWT_SECRET_KEY` 的启动配置。

## 安全说明

- 模型输出使用 `react-markdown`、`remark-gfm` 和 `rehype-sanitize`，不使用 `dangerouslySetInnerHTML`。
- 外部链接只接受 HTTP(S)，并带 `noopener noreferrer nofollow`。
- 上传文件在前后端都校验类型和 10MB 大小上限。
- API Key 响应不含明文；前端只显示固定掩码。
- 后端客户端错误使用安全通用消息，日志不记录 Token、密码、API Key、Prompt、文档正文或推理块。

## 当前限制

- 模型列表、嵌入、RAG 和真实聊天依赖可用的 Ollama/在线模型配置。
- Wiki 离线模式需要预先准备 Wiki 数据。
- 旧 Gradio 的本地 Vosk 语音输入没有对应 FastAPI 接口，因此未复制到 React 客户端；如需恢复，应先设计受控的后端转写 API。
