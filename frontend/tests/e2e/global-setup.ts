import { createServer, type ViteDevServer } from "vite";

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
