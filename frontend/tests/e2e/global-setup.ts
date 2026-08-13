import { createServer, type ViteDevServer } from "vite";
import path from "node:path";

const testServerUrl = "http://127.0.0.1:4173";

async function serverIsReady() {
  try {
    const response = await fetch(testServerUrl, { signal: AbortSignal.timeout(1_000) });
    return response.ok;
  } catch {
    return false;
  }
}

export default async function globalSetup() {
  if (await serverIsReady()) return undefined;

  let server: ViteDevServer | null = await createServer({
    mode: "test",
    configFile: false,
    root: process.cwd(),
    plugins: [(await import("@vitejs/plugin-react")).default()],
    resolve: { alias: { "@": path.resolve(process.cwd(), "src") } },
    define: { "import.meta.env.VITE_API_BASE_URL": JSON.stringify("/api") },
    server: {
      host: "127.0.0.1",
      port: 4173,
      strictPort: true,
    },
  });
  await server.listen();

  return async () => {
    const activeServer = server;
    server = null;
    await activeServer?.close();
  };
}
