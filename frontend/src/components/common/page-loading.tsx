import { LoaderCircle } from "lucide-react";

export function PageLoading({ label = "正在加载" }: { label?: string }) {
  return (
    <div className="grid min-h-screen place-items-center bg-background px-6" role="status">
      <div className="flex items-center gap-3 text-sm text-muted">
        <LoaderCircle className="size-5 animate-spin" aria-hidden="true" />
        <span>{label}</span>
      </div>
    </div>
  );
}
