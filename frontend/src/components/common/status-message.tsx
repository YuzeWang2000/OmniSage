import { AlertCircle, CheckCircle2, Info } from "lucide-react";

import { cn } from "@/utils/cn";

interface StatusMessageProps {
  tone?: "error" | "success" | "info";
  children: React.ReactNode;
  className?: string;
}

export function StatusMessage({ tone = "info", children, className }: StatusMessageProps) {
  const Icon = tone === "error" ? AlertCircle : tone === "success" ? CheckCircle2 : Info;
  return (
    <div
      className={cn(
        "flex items-start gap-2 rounded-xl border px-3.5 py-3 text-sm leading-5",
        tone === "error" && "border-[#fecdca] bg-[#fff6f5] text-[#912018]",
        tone === "success" && "border-[#abefc6] bg-[#ecfdf3] text-[#067647]",
        tone === "info" && "border-[#b2ddff] bg-[#eff8ff] text-[#175cd3]",
        className,
      )}
      role={tone === "error" ? "alert" : "status"}
    >
      <Icon className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
      <span>{children}</span>
    </div>
  );
}
