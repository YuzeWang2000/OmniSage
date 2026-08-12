import * as SwitchPrimitive from "@radix-ui/react-switch";
import type { ComponentProps } from "react";

import { cn } from "@/utils/cn";

export function Switch({ className, ...props }: ComponentProps<typeof SwitchPrimitive.Root>) {
  return (
    <SwitchPrimitive.Root
      className={cn(
        "inline-flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full border border-transparent bg-[#d0d5dd] p-0.5 outline-none transition-colors",
        "data-[state=checked]:bg-primary focus-visible:ring-3 focus-visible:ring-primary/20 disabled:cursor-not-allowed disabled:opacity-50",
        className,
      )}
      {...props}
    >
      <SwitchPrimitive.Thumb className="pointer-events-none block size-5 rounded-full bg-white shadow-sm transition-transform data-[state=checked]:translate-x-5" />
    </SwitchPrimitive.Root>
  );
}
