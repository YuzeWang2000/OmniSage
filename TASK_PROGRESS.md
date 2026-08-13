# OmniSage AI Provider 重构进度

## Goal
- 最终目标：完成 AI Provider 架构重构、前后端迁移、安全加固、数据库工具、测试、OpenAPI 与文档同步。
- 完成标准：附件“最终验收”和“最终交付”全部有实际证据，或明确记录当前授权范围内无法解决的真实阻塞。
- 当前总体状态：completed
- 最近更新时间：2026-08-12 13:45 Asia/Shanghai

## 用户约束与安全边界
- 禁止事项：未经明确要求不得提交、推送、重置或清理 Git；不得自动重置数据库；不得以虚假结果冒充未实现能力；不得使用真实付费模型或真实 API Key 做自动化测试。
- 已获授权：修改 `D:\Workspace\OmniSage` 内代码、测试、配置与文档；运行本地审计、测试、构建、临时数据库与受控假 Provider 验证。
- 仍需授权：任何 Git 提交/推送；真实外部凭证或付费 Provider 调用；生产数据库重置。

## 基线与工作区状态
- 当前分支：`develop`（跟踪 `origin/develop`）。
- 初始未提交修改：已存在大量 AI Provider 重构改动；详见 2026-08-12 首次 `git status --short --branch`。全部按用户现有工作保留并审计，不假定为已完成。
- 需要保留的用户文件：所有首次审计中已修改、删除及未跟踪文件；尤其 `backend/app/ai/`、`backend/tests/`、`docs/`、前端迁移改动、`openapi.json`。
- 兼容/重置策略：采用“干净重构 + 显式数据库重置”。旧 `user_api_keys`、`chat_history`、裸模型字符串无法可靠映射到多连接、ContentPart 和 connection-scoped model key；不保留双运行时。普通重置只重建 SQL 表，默认保留上传、Chroma 与 Wiki 文件；本任务不对真实数据库执行重置。

## 阶段检查点
### 阶段 1：审计、官方文档和兼容决策
- 状态：completed
- 目标：完整审计附件指定材料、现有 diff、运行路径、持久化数据、官方接口及兼容成本。
- 已完成：读取附件；确认 Goal 约束；检查 Git 基线、diff、根目录、指定后端/前端/数据路径、OpenAPI、现有新增架构/测试/文档；梳理旧模型选择、Key、实例创建、SSE、消息、RAG、前端状态与持久化；查阅三家官方文档；确定干净重构策略；输出实施计划。
- 修改文件：`TASK_PROGRESS.md`
- 数据库/API/OpenAPI 变化：确认已有 `provider_connections`、`ai_model_cache`、`chat_messages` 与 `/ai/*`、新 Chat/SSE；旧 `/models`、`/api-keys/*` 和旧运行时已从当前 diff 删除。
- 文档变化：建立持久化检查点；审计现有 README、架构/API/迁移/扩展文档及 CHANGELOG。
- 验证命令及结果：项目 venv `pytest backend/tests -q`：10 passed；`compileall`：exit 0；前端 `pnpm typecheck`：exit 0；`pnpm lint`：exit 0。仅证明现有覆盖，不代表最终验收。
- 未完成：无；后续阶段需补足远多于现有 10 项的验收覆盖。
- 下一步：阶段 2，逐项验证并完善标准契约及其测试。
- 风险或阻塞：现有实现骨架正确但覆盖偏薄；DashScope 连接测试未发起受控 Provider 请求；错误分类、停止/取消、数据库恢复、前端 E2E 等需继续验证。

### 阶段 2：标准数据契约
- 状态：completed
- 目标：验证并完善 Provider、ModelDescriptor、ModelTaskType、ContentPart、任务请求/响应、事件和错误契约。
- 已完成：验证 Provider/Model/Task/Modality/Capability、ContentPart、Chat/Embedding/Rerank/TTS；补 SpeechRecognition、ImageUnderstanding、ImageGeneration、VideoUnderstanding 类型契约；补全部任务 Adapter Protocol；未知 ContentPart、错误任务和不支持能力均安全失败；修复 grounded chat 本地检索参数错位与结果结构处理。
- 修改文件：`backend/app/ai/contracts/requests.py`、`backend/app/ai/providers/base.py`、`backend/app/ai/errors.py`、`backend/app/ai/workflows/grounded_chat.py`、相关测试。
- 数据库/API/OpenAPI 变化：仅增加内部前向兼容契约，尚无新 HTTP 调用入口；OpenAPI 不宣称未实现任务。
- 文档变化：现有扩展文档已审计；阶段 10 统一同步细节。
- 验证命令及结果：`pytest backend/tests -q`：14 passed（阶段 2 时点）；`compileall`：exit 0。
- 未完成：无；未实现任务保持仅契约/Protocol，无虚假响应。
- 下一步：阶段 3 Registry 与 Adapter。
- 风险或阻塞：无。

### 阶段 3：Provider Registry 与基础 Adapter
- 状态：completed
- 目标：验证并完善 Registry、Ollama、OpenAI-compatible 基础层及无名称推断。
- 已完成：验证 Registry 注册/重复/未知查找；`/ai/providers` 从 Adapter `supports_task` 动态声明任务；OpenAI-compatible 严格映射文本/usage/content/reasoning/tool call；401/403、429、超时、无效 JSON/SSE 分别标准化；DeepSeek 畸形目录返回 502 类错误；Ollama 从 `/api/show` capabilities 严格分类，不再把未知能力默认为 Chat，vision 从 modality 派生，reasoning 使用官方 `think` 字段。
- 修改文件：`backend/app/ai/providers/openai_compatible/provider.py`、`deepseek/provider.py`、`ollama/provider.py`、`backend/app/ai/routers.py`、`backend/app/ai/errors.py`、相关测试。
- 数据库/API/OpenAPI 变化：Provider 列表的 supported_tasks 现在反映实际 Adapter；标准错误新增 `ProviderInvalidResponse`=502。
- 文档变化：阶段 10 同步错误表与 Ollama reasoning。
- 验证命令及结果：`pytest backend/tests -q`：17 passed；`compileall`：exit 0。
- 未完成：无；流取消与完整路由 SSE 验证归阶段 7/10。
- 下一步：阶段 4 数据库、凭证、缓存和重置工具。
- 风险或阻塞：无。

### 阶段 4：数据库、凭证与重置
- 状态：completed
- 目标：验证并完善连接、模型缓存、消息结构、凭证加密及安全重置/备份/恢复工具。
- 已完成：验证新表与幂等空库；连接/目录用户隔离；禁用连接不可调用；缓存过期/stale 与单连接失败隔离；Key 加密、更新轮换、掩码与不回显；SSRF 基线；重置 CLI dry-run、确认、路径保护、生产双确认、SQLite 备份完整性及恢复。修复重置脚本未导入 ORM 导致 metadata 为空却虚假成功的严重缺陷，统一 SQLite 路径来源。
- 修改文件：`backend/app/models.py`（既有）、`backend/app/ai/services/*`、`backend/app/ai/security/credentials.py`、`backend/scripts/reset_database.py`、`backend/app/config.py`、`.env.example`、`compose.yaml`、相关测试。
- 数据库/API/OpenAPI 变化：禁用连接从 available 模型目录排除；新增 `APP_ENV`；重置 CLI 新增 `--restore-from`、`--production-confirm`，移除无真实独立语义的 `--include-ai-cache`。
- 文档变化：阶段 10 同步新 CLI 与生产保护。
- 验证命令及结果：数据库/凭证专项 7 passed；全后端 26 passed；compileall exit 0。所有破坏性验证仅作用于 pytest 临时 SQLite。
- 未完成：无；MySQL 只支持外部 `mysqldump/mysql`，工具不实现 schema drop，需如实记录。
- 下一步：阶段 5 DeepSeek。
- 风险或阻塞：不得对用户真实数据库执行破坏性操作；本阶段未执行。

### 阶段 5：DeepSeek
- 状态：completed
- 目标：动态发现、文本聊天、Reasoning、Streaming、Tool Calling 契约和官方映射。
- 已完成：动态 `/models` 发现，不含硬编码别名；文本 Chat Completions、结构化 `thinking`、`high|max` effort、reasoning/content 分流、usage/tool call、上游错误分类；thinking 时过滤 temperature。
- 修改文件：DeepSeek/OpenAI-compatible Provider 与测试。
- 数据库/API/OpenAPI 变化：模型目录完全由连接实际发现结果生成。
- 文档变化：官方接口已记录，阶段 10统一校准。
- 验证命令及结果：受控 mock 发现、畸形目录、reasoning 映射包含于 26 passed。
- 未完成：不使用真实 Key/付费模型；工具多轮 reasoning_content 不默认持久化完整思维链，保持安全限制。
- 下一步：阶段 6 百炼。
- 风险或阻塞：不使用真实 Key。

### 阶段 6：阿里云百炼
- 状态：completed
- 目标：地域/Workspace、发现或 fallback、聊天、Reasoning、协议差异与官方映射。
- 已完成：地域/Workspace/Base URL 严格模板与校验；OpenAI-compatible 文本 Chat；无推理 `/models` 连接鉴权；不把平台候选模型冒充用户可调用目录；只暴露用户明确模型 ID；新增显式 per-model capability override，reasoning/effort 由能力声明驱动并用 `enable_thinking` 映射。
- 修改文件：DashScope Provider、连接 Schema/Service、测试。
- 数据库/API/OpenAPI 变化：连接 config 新增 `manual_model_capabilities`；仍不存 Provider 特有字段于工作流。
- 文档变化：阶段 10 同步表单/API/能力覆盖。
- 验证命令及结果：手工目录、远程无推理探测、能力覆盖、Workspace 注入拒绝包含于 26 passed。
- 未完成：无可靠 per-credential 模型发现 API，故明确采用 manual source；真实 Key 未调用。
- 下一步：阶段 7 Chat/SSE/工作流。
- 风险或阻塞：不使用真实 Key。

### 阶段 7：聊天与工作流
- 状态：completed
- 目标：model key、ContentPart、标准 SSE、direct/grounded chat、本地 Embedding/Reranker 抽象。
- 已完成：model key/ContentPart/workflow 前置验证；标准 SSE content/reasoning/usage/done/error；前端完成帧检测、错误和取消；reasoning 与 answer 分流且仅本次展示；消息结构持久化；最近历史取最新 N 条并正序；grounded chat 继续使用本地 Ollama Embedding/本地 Reranker 边界，生成模型进入选中 Provider。
- 修改文件：Chat router、DatabaseService、grounded workflow、前端 chat API/workspace/message/types、相关测试。
- 数据库/API/OpenAPI 变化：无新增路由；修复历史窗口语义。
- 文档变化：阶段 10 同步 reasoning 安全与 SSE。
- 验证命令及结果：后端 27 passed；前端 20 passed（阶段 7 时点）；typecheck/lint exit 0。
- 未完成：无；完整 E2E 归阶段 10。
- 下一步：阶段 8 前端连接与目录。

### 阶段 8：前端连接与模型目录
- 状态：completed
- 目标：连接 CRUD/测试、模型刷新/分组、能力标签和失败保护。
- 已完成：连接创建/删除/测试/刷新、Key 独立轮换且不读取旧值；百炼地域/Workspace/手工模型/显式能力覆盖；连接模型按 connection 展示 source、stale、task、capability；列表/操作失败不覆盖表单。
- 修改文件：前端 settings API、`provider-connections.tsx`、组件测试、E2E mock。
- 数据库/API/OpenAPI 变化：前端已支持 `manual_model_capabilities`，待本轮生成 OpenAPI 类型产物。
- 文档变化：阶段 10 更新 frontend README/API 文档。
- 验证命令及结果：前端 22 passed；typecheck/lint exit 0。
- 未完成：OpenAPI 类型生成、build/E2E 归阶段 10。
- 下一步：阶段 9 能力驱动 UI。
- 风险或阻塞：无。

### 阶段 9：能力驱动 UI
- 状态：completed
- 目标：Reasoning/Effort/Workflow/参数清理、多模态安全边界。
- 已完成：Reasoning/Effort 只在 capability 确认时显示；agent 在无 tools 时禁用；切模型清理 reasoning/effort/workflow/RAG 参数；stale 清晰显示；多模态仍无上传入口且服务端安全拒绝；reasoning/content 分流展示。
- 修改文件：Chat composer/workspace/message/types 及测试。
- 数据库/API/OpenAPI 变化：无。
- 文档变化：阶段 10 同步未实现边界。
- 验证命令及结果：前端 22 passed；typecheck/lint exit 0。
- 未完成：完整 build/E2E 归阶段 10。
- 下一步：阶段 10 OpenAPI、文档、安全复核、最终验收。
- 风险或阻塞：无。

### 阶段 10：安全、测试、OpenAPI 与文档
- 状态：completed
- 目标：SSRF、错误脱敏、完整测试/构建/E2E、OpenAPI 类型、README/架构/API/迁移/扩展文档及 CHANGELOG。
- 已完成：SSRF/凭证/错误脱敏、生产重置保护、OpenAPI 临时库安全生成、TS 类型生成、README/架构/API/数据库/Provider/Task/CHANGELOG 同步、过期关键词和本地链接审计、FastAPI 独立启动、完整后端/前端/build/E2E 验收。
- 修改文件：本任务 Git 状态中全部 AI Provider、数据库、Chat、前端、测试、配置、OpenAPI 与文档变更；未提交或推送。
- 数据库/API/OpenAPI 变化：`openapi.json` 已从当前 FastAPI 生成；`schema.d.ts` 已由该产物生成；8 条 `/ai/*` 路径与 `/chat/stream` 实际启动验证通过。
- 文档变化：根/后端/前端 README、五份 docs、FRONTEND_MIGRATION_PLAN、CHANGELOG、TASK_PROGRESS 均与当前实现同步。
- 验证命令及结果：后端 28 passed；compileall exit 0；前端 22 passed；typecheck/lint/build exit 0；Playwright 5 passed；Markdown 10 文件无坏链/未闭合围栏；FastAPI `/health=ok`、OpenAPI 8 条 AI 路径与 Chat 路径存在。
- 未完成：无本提示要求内未完成项；真实付费 Provider 未调用是安全约束，不是缺口。在线 Embedding/Rerank、TTS/STT、视觉/图像/视频调用按要求仅保留契约，明确未实现。
- 下一步：用户可审阅 diff；如需提交/推送须另行明确授权。
- 风险或阻塞：MySQL 备份/恢复依赖外部 `mysqldump/mysql`；PostgreSQL/Alembic 未支持并已记录；百炼无可靠 per-credential 目录，采用 manual source 与显式能力覆盖。

## 决策记录
- 2026-08-12 / 将现有未提交重构作为待审计成果而非重新实现 / 防止覆盖用户工作并保持幂等恢复 / 后续以代码和测试证据决定完成状态。
- 2026-08-12 / 采用干净重构与显式数据库重置 / 旧 Key、消息和裸模型字符串不能可靠表达多连接和类型化契约 / 删除旧 API 与双运行时；重置会丢失 SQL 内用户、会话、Key 和知识库元数据，文件默认保留但可能孤立。
- 2026-08-12 / 实施计划 / 先加固契约与 Registry，再完成连接/缓存/凭证/重置，随后校准 DeepSeek/百炼/Ollama、聊天工作流、前端与安全，最后执行完整后端/前端/E2E/OpenAPI/文档验收 / 每阶段以测试证据关闭。

## 官方文档记录
- 2026-08-12 / DeepSeek / https://api-docs.deepseek.com/api/list-models / 采用 `GET /models` 动态发现，不预设模型 ID。
- 2026-08-12 / DeepSeek / https://api-docs.deepseek.com/api/create-chat-completion 与 https://api-docs.deepseek.com/guides/thinking_mode / 采用 `POST /chat/completions`、SSE `reasoning_content`/`content`；思考 `thinking.type=enabled|disabled`，effort 仅暴露模型声明的 `high|max`；工具轮次需保留 Provider 推理上下文，当前标准消息不默认持久化完整思维链。
- 2026-08-12 / 阿里云百炼 Model Studio / https://help.aliyun.com/zh/model-studio/deep-thinking 与 https://help.aliyun.com/zh/model-studio/what-is-model-studio / 采用 OpenAI-compatible Chat Completions；`enable_thinking` 是非标准扩展字段；地域、Workspace 与 Base URL 绑定，子空间需模型授权，调优模型存在协议限制。
- 2026-08-12 / Ollama / https://docs.ollama.com/api/chat 与 https://docs.ollama.com/api-reference/show-model-details / 采用 `/api/tags`、逐模型 `/api/show` capabilities 与 `/api/chat`；`think` 可为布尔或受支持 effort 字符串，`message.thinking` 与内容分流。

## 测试与验收矩阵
- Git 与文件基线 / completed / `git status --short --branch` 与文件清单 / 已记录已有未提交改动。
- 附件要求读取 / in_progress / 原始读取及编码诊断 / 技术结构和验收项已提取，继续交叉核对。
- 阶段 1 基线测试 / completed / backend venv pytest、compileall、pnpm typecheck、pnpm lint / 10 passed，三个静态检查 exit 0。
- 阶段 2 契约与 grounded chat 回归 / completed / `pytest backend/tests -q`、compileall / 14 passed，compileall exit 0。
- 阶段 3 Registry 与 Adapter / completed / `pytest backend/tests -q`、compileall / 17 passed，compileall exit 0。
- 阶段 4-6 数据/安全/Provider / completed / 专项与全量 pytest、compileall / 26 passed，compileall exit 0；临时 SQLite 备份重置恢复通过。
- 阶段 7 Chat/SSE/工作流 / completed / 后端 27 passed；前端 20 passed；typecheck/lint exit 0。
- 阶段 8-9 前端连接/目录/能力 UI / completed / 前端 22 passed；typecheck/lint exit 0。
- 最终后端 / completed / `backend/.venv/Scripts/python.exe -m pytest backend/tests -q` / 28 passed；compileall exit 0。
- 最终前端 / completed / typecheck、lint、Vitest、build / 22 passed，全部 exit 0，生产产物生成成功。
- 最终 E2E / completed / `frontend/node_modules/.bin/playwright.CMD test` / 5 passed；含登录、连接 Key 掩码、connection-scoped model、标准 SSE、停止及 390px 无横向溢出。
- OpenAPI/启动 / completed / 临时 SQLite 生成与独立 Uvicorn / health=ok，8 条 AI 路径，Chat stream 存在；临时服务/数据库已清理。
- 文档 / completed / 交付范围 10 个 Markdown 本地链接和围栏扫描 / 无坏链、无未闭合围栏；旧关键词仅在明确删除/迁移说明中。
- 连接表单回归验收 / completed / 后端 32 passed；前端 25 passed；typecheck、lint、compileall、build 通过；Playwright 5 passed / 使用临时数据库和 mock Provider，未调用真实付费 API。

## 恢复指令
- 最后一个已验证完成的检查点：阶段 10 与全部最终验收。
- 当前正在进行的操作：无；目标已完成，等待用户审阅。
- 恢复后第一步：若用户提出后续修改，先读取本文件和 Git 状态/diff，保留全部未提交成果。
- 不得重复的副作用操作：不得重置数据库、删除数据、提交/推送/重置 Git；目前尚未执行任何数据库写操作。

## 最终未完成项
- 无。本次未使用真实 DeepSeek/百炼 Key 发起外部调用，属于明确的安全测试边界。

## 回归修复：连接创建表单（2026-08-12）
- 状态：completed
- 根因：后端进程未加载仓库根目录 `.env`，因此在线连接保存凭据时缺少 `CREDENTIAL_ENCRYPTION_KEY` 并返回 422；前端又丢弃了标准 `error.message`。百炼公共北京端点被错误强制要求 Workspace ID，未处理的 `ValueError` 进一步变成 500。
- 已修复：统一从根目录加载 `.env` 且保留系统环境变量优先级；校准百炼公共/Workspace 地域规则并返回标准 422；trim 表单字段；展示后端具体错误和字段级错误；增加 DeepSeek/百炼 API Key、地域、Workspace、模型 ID 可见标签与提示；表单失败后保留内容；移动端弹窗限制在视口内。
- 验收：后端 `32 passed` 与 compileall 通过；前端 `25 passed`、typecheck、lint、build 通过；Playwright Chromium/390px `5 passed`；OpenAPI 与 TS 类型已重新生成。

## 回归修复：百炼自动目录与首次聊天（2026-08-12）
- 状态：completed
- 根因：百炼 Adapter 的 `list_models` 只读取 `manual_models`，虽然连接测试请求了 `/models`，却丢弃了响应；聊天 SSE 生成器捕获了请求级 Session 中的 ORM 连接，首次更新会话标题的 `commit` 使属性过期，流开始后读取密钥触发 `DetachedInstanceError`。
- 已修复：百炼刷新合并兼容 `/models` 候选与手工补充模型，远端项以 `metadata.authorization_unverified=true` 明示权限仍需实际调用验证；前端将手工输入降级为可选“补充模型 ID”并展示权限待验证标签。聊天在返回 SSE 前创建不可变运行时连接快照并解密凭据，流结束后使用独立 Session 保存消息，不再跨流持有 ORM 实例或请求级 Session。
- 验收：后端 `34 passed`、compileall 通过；前端 `25 passed`、typecheck、lint、build 通过；Playwright `5 passed`。未使用真实 Key 或付费推理验证单个候选模型权限。

## 回归修复：百炼白名单与多任务目录（2026-08-12）
- 状态：completed
- 语义：`manual_models` 为空时返回 `/models` 全部候选；非空时作为严格白名单，仅返回用户指定 ID，不再与远端目录合并。
- 分类：优先读取供应商响应的 `task_types`/`tasks`/`capabilities`；缺失时依据百炼官方模型族保守区分 Chat/文本生成、视觉/视频理解、图像/视频生成、语音识别/合成、Embedding、Rerank。未知模型保持空任务和空模态，不默认标为 Chat。新增 `video_generation` 标准任务类型。
- UI：设置页请求完整目录并显示中文任务标签、输入/输出模态、未知任务及权限待调用验证；聊天和默认模型设置使用独立查询缓存，继续只请求 text Chat，避免非聊天模型进入聊天选择器。
- 依据：百炼官方总览明确覆盖文本、视觉、图像、视频、语音与向量；具体模型族参考官方 Chat、Embedding/Rerank、图像生成及模型上下架文档。动态控制台不是后端稳定 API，因此不运行时抓取页面 HTML。
- 验收：后端 `35 passed`、compileall 通过；前端 `25 passed`、typecheck、lint、build 通过；Playwright `5 passed`；OpenAPI 与 TS 类型已重新生成。未使用真实 Key 或付费推理验证。

## 回归修复：供应商 401 误触发注销（2026-08-12）
- 状态：completed
- 根因：上游供应商拒绝 API Key 被映射为 `CredentialInvalid` HTTP 401；前端对所有 401 都执行全局会话清理，因而测试连接/刷新时跳转登录页。
- 已修复：HTTP 401 仅保留给 OmniSage JWT 认证；`CredentialInvalid` 改为 HTTP 424。前端解析标准错误码，并兼容旧后端的 `401 + CredentialInvalid`，仅真正的应用认证 401 才清除登录状态。
- 验收：后端 `36 passed`、compileall 通过；前端 `27 passed`、typecheck、lint、build 通过。覆盖真实 JWT 401 注销、旧版供应商 401 不注销和新版供应商 424 不注销三种场景。

## 回归修复：grounded chat 缺少知识库（2026-08-12）
- 状态：completed
- 根因：前端切换为 `grounded_chat` 时只设置了 `ragEnabled`，没有提供知识库选择；后端将缺失 `knowledge_base_id` 作为普通 `ValueError` 抛出，绕过 AI 标准错误处理形成 500。
- 已修复：聊天编辑器在知识库问答模式加载并要求选择用户知识库，未选择时禁用发送，发送路径再做一次防御校验；请求模型要求非 Wiki grounded chat 携带知识库 ID；服务层缺失配置返回 422，不存在/越权返回 404。
- 在线 Embedding 评估：`qwen3.7-text-embedding` 技术可接入，但当前 RAG 上传/查询硬编码 `OllamaEmbeddings`，不能只替换模型名。嵌入配置必须固定在知识库级；禁止同库不同文件混用模型/维度，更换需全库重建。建议后续新增在线 Adapter、知识库级 connection-scoped model key/维度/版本快照、批处理/重试/费用提示和重建索引流程后，再开放建库选择。
- 验收：后端 `38 passed`、compileall 通过；前端 `28 passed`、typecheck、lint、build 通过。未调用真实在线 Embedding。

## 回归修复：删除会话触发错误边界（2026-08-12）
- 状态：completed
- 根因：删除当前会话后，内部导航先更新活动 ID 和 URL；读取旧 `conversation` 查询参数的 effect 在下一次渲染中又将已删除 ID 写回，与列表兜底选择形成竞态并触发全局错误边界。
- 已修复：内部会话导航记录待同步 URL 目标，URL effect 识别并忽略过渡态；删除成功从 QueryClient 最新缓存计算剩余列表，清理消息缓存后原子切换到下一会话或 `/chat` 空状态。
- 验收：前端 `28 passed`、typecheck、lint、build 通过；Playwright `6 passed`，新增“删除最后一个会话后 URL 为 `/chat`、显示空状态且无错误边界”真实交互回归。

## P1 审查项修复（2026-08-13）

- SEC-001：知识库目录改用不可变 ID，所有存储路径执行根目录 containment 校验；越界旧路径拒绝删除。
- BUG-001：服务端从已授权会话装配最近历史，客户端只提交当前轮；重新生成移除旧回答与重复问题。
- DATA-001：上传使用 pending SQL row + file_id chunk 元数据；失败回滚 SQL/文件/向量。删除使用隔离文件、向量快照和 SQL 失败恢复。
- PERF-001：RAG/Wiki 阻塞任务使用独立受限 worker；请求使用独立 Session；Wiki HTTP 设置 connect/read timeout。
- DEPLOY-001：移除不存在 `.npmrc` 的 COPY、对齐 pnpm 版本、纳入 `backend/uv.lock`、补全 Compose MySQL 示例变量。
- 专项验证：新增多轮/路径/补偿/超时/部署输入测试，9 passed。
- 完整验收：后端 `46 passed`，`compileall` 通过，`uv lock --check` 通过；前端 `28 passed`，typecheck、lint、生产构建通过；Playwright `6 passed`；运行时 OpenAPI 与 `openapi.json` 一致（28 条路径）。
- 验证限制：当前环境没有 Docker CLI，未执行 `docker compose config/build/up`；未调用真实 Provider、付费 API 或生产数据。

## 回归修复：登录提示、知识库索引与重命名（2026-08-13）

- 登录：`/auth/login` 的安全 401 详情不再被全局“会话失效”文案覆盖；其他受保护接口的 401 仍会清理失效登录态。
- 索引：Chroma 写入前清理复杂/空元数据，并按 `VECTOR_WRITE_BATCH_SIZE`（默认 32）分批嵌入；底层异常写入 traceback，客户端收到 Ollama 连接、模型缺失或通用诊断提示。
- 重命名：新增用户隔离的 `PATCH /rag/knowledge-bases/{id}`，支持修改名称和描述、检测同名冲突；ID 型文件与向量目录不移动。
- 本机诊断：Ollama 可访问，`nomic-embed-text:latest` 已安装，`/api/embed` 返回 768 维向量。未用用户原文件重新上传，避免擅自写入知识库。
- 验收：后端 `49 passed`；前端 `30 passed`，typecheck、lint、生产构建通过；OpenAPI 与运行时一致。
