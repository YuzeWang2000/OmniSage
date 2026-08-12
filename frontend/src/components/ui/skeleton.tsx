import type { HTMLAttributes } from "react";

import { cn } from "@/utils/cn";

export function Skeleton({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-lg bg-[#e9edef]", className)}
      aria-hidden="true"
      {...props}
    />
  );
}
