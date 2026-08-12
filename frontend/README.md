# OmniSage React 前端

这是 OmniSage 的正式 Web 前端，使用 TypeScript、React 和 Vite，通过 HTTP/SSE 连接现有 FastAPI 后端。浏览器端不包含 RAG、模型调用或数据库业务逻辑。

## 环境要求

- Node.js 20.19+ 或 22.12+
- pnpm 11
- 已启动的 OmniSage FastAPI（默认 `http://127.0.0.1:8000`）

## 本地开发

```bash
pnpm install
copy .env.example .env.local
pnpm dev
```

开发地址为 `http://127.0.0.1:5173`。默认情况下，Vite 把 `/api` 代理到 `http://127.0.0.1:8000`，包括不缓冲的 SSE 聊天流。

## 环境变量

| 变量                      | 用途                            | 开发默认值                     |
| ------------------------- | ------------------------------- | ------------------------------ |
| `VITE_API_BASE_URL`       | 浏览器访问的 API 前缀或绝对地址 | 示例为 `http://127.0.0.1:8000` |
| `VITE_DEV_PROXY_TARGET`   | Vite 开发代理目标               | `http://127.0.0.1:8000`        |
| `VITE_REQUEST_TIMEOUT_MS` | 普通请求超时                    | `30000`                        |
| `VITE_UPLOAD_TIMEOUT_MS`  | 文件上传/索引超时               | `180000`                       |
| `VITE_CHAT_TIMEOUT_MS`    | 聊天流超时                      | `120000`                       |

不创建 `.env.local` 时，开发模式会自动使用 `/api` 代理；若采用 `.env.example` 的绝对地址，FastAPI 必须允许当前前端来源。生产构建中的 `VITE_*` 变量会被写入静态资源，不能用于保存密钥。JWT 由集中式会话模块保存在 `sessionStorage`；业务组件不会直接读取或写入 Token。

## 质量命令

```bash
pnpm typecheck
pnpm lint
pnpm test
pnpm build
pnpm exec playwright test
```

Playwright 使用本机 Chrome 的隔离上下文，并在测试进程内启动临时 Vite 服务。API 和 SSE 由可控网络拦截提供，不会调用外部大模型。

## OpenAPI 类型

后端启动后执行：

```bash
pnpm generate:api
```

脚本从 `http://127.0.0.1:8000/openapi.json` 生成 `src/api/schema.d.ts`。提交接口改动时应同步更新该文件。

## 生产构建

```bash
pnpm build
```

输出位于 `dist/`。仓库中的多阶段 `Dockerfile` 使用 Nginx 提供静态资源，并把同源 `/api/` 反向代理到 `backend:8000`；聊天位置已禁用代理缓冲。
