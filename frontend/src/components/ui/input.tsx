import type { InputHTMLAttributes } from "react";

import { cn } from "@/utils/cn";

function Input({ className, type = "text", ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      type={type}
      className={cn(
        "flex h-11 w-full rounded-xl border bg-surface px-3.5 text-sm text-foreground shadow-xs outline-none placeholder:text-[#98a2b3] disabled:cursor-not-allowed disabled:opacity-50",
        "focus-visible:border-primary focus-visible:ring-3 focus-visible:ring-primary/15",
        className,
      )}
      {...props}
    />
  );
}

export { Input };
