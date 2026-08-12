import type { HTMLAttributes } from "react";

import { cn } from "@/utils/cn";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: "neutral" | "success" | "warning" | "danger";
}

export function Badge({ tone = "neutral", className, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex min-h-6 items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium",
        tone === "neutral" && "border-[#e3e7ed] bg-[#f7f8fa] text-[#475467]",
        tone === "success" && "border-[#abefc6] bg-[#ecfdf3] text-[#067647]",
        tone === "warning" && "border-[#fedf89] bg-[#fffaeb] text-[#b54708]",
        tone === "danger" && "border-[#fecdca] bg-[#fef3f2] text-[#b42318]",
        className,
      )}
      {...props}
    />
  );
}
