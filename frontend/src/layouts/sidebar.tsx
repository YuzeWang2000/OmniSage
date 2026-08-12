import { Sparkles } from "lucide-react";

import { Navigation } from "@/layouts/navigation";

export function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 border-r bg-[#fbfcfc] p-4 lg:flex lg:flex-col">
      <div className="flex h-14 items-center gap-3 px-2">
        <span className="grid size-9 place-items-center rounded-xl bg-primary text-white shadow-sm">
          <Sparkles className="size-[18px]" aria-hidden="true" />
        </span>
        <div>
          <p className="text-[15px] font-semibold tracking-tight">OmniSage</p>
          <p className="text-[11px] text-muted">Knowledge workspace</p>
        </div>
      </div>
      <div className="mt-5 flex-1">
        <Navigation />
      </div>
      <div className="rounded-xl border bg-surface p-3">
        <p className="text-xs font-medium text-[#344054]">私有知识，清晰答案</p>
        <p className="mt-1 text-[11px] leading-4 text-muted">内容只发送到你配置的 FastAPI 服务。</p>
      </div>
    </aside>
  );
}
