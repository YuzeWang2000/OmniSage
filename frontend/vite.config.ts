import path from "node:path";

import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const proxyTarget = env.VITE_DEV_PROXY_TARGET || "http://127.0.0.1:8000";

  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    server: {
      host: "127.0.0.1",
      port: 5173,
      proxy: {
        "/api": {
          target: proxyTarget,
          changeOrigin: true,
          rewrite: (requestPath) => requestPath.replace(/^\/api/, ""),
          configure: (proxy) => {
            proxy.on("proxyRes", (proxyResponse) => {
              proxyResponse.headers["x-accel-buffering"] = "no";
              proxyResponse.headers["cache-control"] = "no-cache";
            });
          },
        },
      },
    },
    test: {
      environment: "jsdom",
      setupFiles: "./src/test/setup.ts",
      exclude: ["tests/e2e/**", "**/node_modules/**", "**/dist/**"],
      css: true,
      clearMocks: true,
      restoreMocks: true,
    },
  };
});
