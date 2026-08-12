import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";

import App from "@/App";
import { ErrorBoundary } from "@/components/common/error-boundary";
import { AuthBootstrap } from "@/features/auth/auth-bootstrap";
import { queryClient } from "@/lib/query-client";
import "@/styles/globals.css";

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("找不到应用挂载节点");
}

createRoot(rootElement).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthBootstrap>
          <ErrorBoundary>
            <App />
          </ErrorBoundary>
        </AuthBootstrap>
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
);
