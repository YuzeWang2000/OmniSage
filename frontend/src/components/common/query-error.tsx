import { RefreshCcw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { StatusMessage } from "@/components/common/status-message";

export function QueryError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="space-y-3">
      <StatusMessage tone="error">{message}</StatusMessage>
      <Button variant="secondary" size="sm" onClick={onRetry}>
        <RefreshCcw className="size-3.5" aria-hidden="true" />
        重试
      </Button>
    </div>
  );
}
