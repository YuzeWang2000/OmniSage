import { useEffect, useState, type ReactNode } from "react";

import { ApiError } from "@/api/client";
import { getCurrentUser } from "@/api/auth";
import { Button } from "@/components/ui/button";
import { PageLoading } from "@/components/common/page-loading";
import { StatusMessage } from "@/components/common/status-message";
import { useAuthStore } from "@/stores/auth-store";

type BootstrapState = "waiting" | "checking" | "ready" | "error";

export function AuthBootstrap({ children }: { children: ReactNode }) {
  const token = useAuthStore((state) => state.token);
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const setAuthenticated = useAuthStore((state) => state.setAuthenticated);
  const [status, setStatus] = useState<BootstrapState>("waiting");

  useEffect(() => {
    if (!hasHydrated) return;
    if (!token) {
      setStatus("ready");
      return;
    }

    const controller = new AbortController();
    setStatus("checking");
    getCurrentUser(controller.signal)
      .then((user) => {
        setAuthenticated(token, user);
        setStatus("ready");
      })
      .catch((error: unknown) => {
        if (error instanceof ApiError && error.kind === "cancelled") return;
        if (error instanceof ApiError && error.kind === "unauthorized") {
          setStatus("ready");
          return;
        }
        setStatus("error");
      });

    return () => controller.abort();
  }, [hasHydrated, setAuthenticated, token]);

  if (!hasHydrated || status === "waiting" || status === "checking") {
    return <PageLoading label="正在恢复登录状态" />;
  }

  if (status === "error") {
    return (
      <main className="grid min-h-screen place-items-center px-6">
        <section className="w-full max-w-md rounded-2xl border bg-surface p-6 shadow-sm">
          <StatusMessage tone="error">无法验证登录状态，请确认 FastAPI 服务已启动。</StatusMessage>
          <Button className="mt-4 w-full" onClick={() => window.location.reload()}>
            重新连接
          </Button>
        </section>
      </main>
    );
  }

  return children;
}
