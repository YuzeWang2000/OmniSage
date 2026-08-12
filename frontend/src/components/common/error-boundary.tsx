import { Component, type ReactNode } from "react";
import { RefreshCcw, TriangleAlert } from "lucide-react";

import { Button } from "@/components/ui/button";

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false };

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  componentDidCatch() {
    // Production error reporting can be connected here without logging user content.
  }

  render() {
    if (!this.state.hasError) return this.props.children;

    return (
      <main className="grid min-h-screen place-items-center bg-background px-5 py-10">
        <section className="w-full max-w-md rounded-2xl border bg-surface p-7 text-center shadow-sm">
          <span className="mx-auto grid size-12 place-items-center rounded-full bg-[#fef3f2] text-danger">
            <TriangleAlert className="size-6" aria-hidden="true" />
          </span>
          <h1 className="mt-5 text-xl font-semibold">页面遇到问题</h1>
          <p className="mt-2 text-sm leading-6 text-muted">
            你的数据没有被修改。请刷新页面；如果问题持续，请确认后端服务状态。
          </p>
          <Button className="mt-6 w-full" onClick={() => window.location.reload()}>
            <RefreshCcw className="size-4" aria-hidden="true" />
            刷新页面
          </Button>
        </section>
      </main>
    );
  }
}
