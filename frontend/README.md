# OmniSage Frontend

需要 Node 20.19+ 或 22.12+、pnpm 11。

```powershell
pnpm install
Copy-Item .env.example .env.local
pnpm dev
pnpm generate:api
pnpm typecheck
pnpm lint
pnpm test
pnpm build
pnpm exec playwright test
```

`generate:api` 默认读取仓库根 `openapi.json`，也可用 `VITE_OPENAPI_URL` 指向运行中的 FastAPI。开发环境变量为 `VITE_API_BASE_URL`、`VITE_DEV_PROXY_TARGET`、`VITE_REQUEST_TIMEOUT_MS`、`VITE_UPLOAD_TIMEOUT_MS`、`VITE_CHAT_TIMEOUT_MS`。

设置页管理 Ollama、DeepSeek、百炼连接，可测试连接、刷新模型并查看 Key 掩码；百炼表单包含地域、Workspace 和可选模型白名单。白名单为空时刷新全部远端候选，填写后只显示指定模型；目录展示任务类型与输入输出模态。聊天模型按 Provider/Connection 分组，仅显示可用 text Chat 模型。Reasoning、effort 和 Agent 由 ModelDescriptor capability 驱动；切换模型会清理不兼容参数。stale 模型会标注“缓存已过期”。TanStack Query 管理连接与模型服务端状态，Zustand 不复制目录且 localStorage 不保存 Key。

当前没有图片/音频上传、TTS、在线 Embedding/Rerank 选择或视觉调用入口。模型目录为空时先在设置页创建连接并刷新；连接读取失败不会覆盖正在编辑的表单。

设置页支持独立轮换 Key（不会读取旧值）、展示模型 source/stale/task/capability/授权待验证状态，以及为百炼补充模型显式声明能力。reasoning 与 answer 在 SSE 中分流；推理文本仅在当前流中折叠展示，不写入会话历史。2026-08-12 实测 typecheck、lint、生产 build 通过，Vitest `25 passed`，Playwright `5 passed`（含 390px 移动端无横向溢出）。
