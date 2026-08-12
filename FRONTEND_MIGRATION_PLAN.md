# OmniSage 前端迁移计划

## 当前功能清单

- JWT 用户注册、登录、退出；旧前端仅以内存 `gr.State` 保存登录态，刷新后不会恢复。
- 工作台展示最近对话、常用知识库和聊天/知识库/搜索快捷入口。
- 对话的新建、切换、重命名、删除、历史加载，以及 SSE 文本流式回答。
- Chat / Generate 模式、模型选择、RAG 与 Wiki 开关、Wiki 在线/离线模式。
- 知识库创建、列表、统计、删除、同步上传与向量化、文件列表和文件删除。
- Wiki 搜索、指定知识库的结构化搜索。
- API Key 创建、列表和删除；列表接口不会返回密钥正文。
- Vosk 语音转写仅存在于 Gradio 进程，不属于 FastAPI 能力，本次 React 迁移不复制这段 Python 业务。

## 后端接口映射

| 功能域 | 现有 FastAPI 接口 | React 前端用途 |
| --- | --- | --- |
| 服务 | `GET /health`, `GET /models` | 服务状态、模型列表 |
| 认证 | `POST /auth/register`, `POST /auth/login` | 注册、登录、取得 JWT |
| 对话 | `POST /conversations/`, `GET /conversations/user/{user_id}`, `GET /conversations/{id}/messages`, `PATCH /conversations/{id}`, `DELETE /conversations/{id}` | 会话 CRUD 与消息历史 |
| 聊天 | `POST /chat/stream` | SSE 流式生成 |
| 知识库 | `POST /rag/knowledge-bases`, `GET /rag/knowledge-bases/{user_id}`, `DELETE /rag/knowledge-bases/{id}`, `GET /rag/stats/{user_id}` | 知识库 CRUD、概览 |
| 文件 | `POST/GET /rag/knowledge-bases/{id}/files`, `DELETE /rag/knowledge-bases/{id}/files/{file_id}` | 上传、处理结果、列表、删除 |
| 搜索 | `GET /rag/knowledge-bases/{id}/search`, `GET /rag/enhance-context-with-wiki` | 结构化知识库结果、Wiki 内容 |
| Wiki | `GET /rag/wiki/status`, `POST /rag/wiki/switch-mode` | 状态与在线/离线切换 |
| API Key | `POST /api-keys/`, `GET /api-keys/user/{user_id}`, `DELETE /api-keys/{id}` | 新增、掩码列表、删除 |

## 新前端目录结构

React 版本先在 `frontend-react/` 独立完成和验证，验收后将现有 Gradio 文件保留到 `frontend-legacy/`，再由 React 版本接管 `frontend/`。应用按 `api`、`components`、`features`、`layouts`、`pages`、`routes`、`stores`、`styles`、`types` 与 `utils` 分域；单元测试与 Playwright 测试分别放在 `src/**/*.test.ts(x)` 和 `tests/e2e/`。

## 必须保留的行为

- JWT Bearer 身份校验与后端基于令牌确定用户身份的规则。
- 新会话使用“新对话”，首条消息后由后端自动生成标题。
- RAG、Wiki、Chat / Generate 和模型参数保持现有请求语义。
- 流式协议继续解析 `data: {"chunk": ...}`、`data: {"error": ...}` 与 `data: {"done": true}`。
- 上传仍由 FastAPI 同步处理并返回文档块数量；成功后刷新知识库、统计和文件查询。
- API Key 列表不返回也不展示完整密钥。
- 既有 FastAPI 启动方式和业务服务保持不变。

## 已发现的接口缺口

- 没有 `/auth/me` 或刷新令牌接口；登录恢复只能依赖集中保存的 JWT/用户元数据，并由任一受保护请求和统一 401 处理完成校验。
- API Key 更新路由被注释，无法可靠满足“更新”要求；需要恢复一个带所有权校验的最小向后兼容 `PUT /api-keys/{id}`。
- 没有用户设置持久化接口；默认模型、RAG/Wiki 默认值只能明确作为设备级偏好集中保存，Wiki 服务模式仍使用现有后端接口。
- 聊天请求没有知识库选择字段，RAG 实际固定使用用户的第一个知识库；需要新增可选 `knowledge_base_id`，缺省时继续沿用旧行为。
- 聊天 SSE 不返回结构化引用；前端可在 RAG 回答后调用现有知识库搜索接口展示同一问题的引用，但 Wiki 引用只有非结构化上下文。
- 停止生成只能由浏览器中止连接，后端生成器没有独立取消接口；“重新生成”也只能重新提交最后一条用户消息。
- 上传是同步处理，现有接口只能提供网络上传进度，不能提供服务端索引阶段的细粒度进度。
- FastAPI 未配置 CORS；开发代理可避免跨域，但直连生产 API 需要最小、可配置的允许来源。
- OpenAPI 对若干动态字典响应和 SSE 响应未定义结构，因此自动生成类型后仍需为这些边界补充手写类型守卫。

## 实施结果

- 已新增 `/auth/me`、API Key 更新、指定知识库检索、结构化 Wiki 搜索、聊天重新生成字段和可配置 CORS；改动均为向后兼容的可选能力。
- SSE 保留现有 `chunk/error/done` 协议，并补充正确媒体类型、禁用代理缓冲和客户端中止处理。
- 设置默认值按设备保存在集中式 Zustand store；后端仍负责 Wiki 运行模式。读取失败不会重置正在编辑的表单。
- 上传仍是同步索引接口，因此界面可显示网络上传进度和“解析/索引中”状态，但无法显示服务端逐块索引百分比。
- 旧 Vosk 语音能力没有 FastAPI 接口，未迁移到 React；旧实现保存在 `frontend-legacy/`。
