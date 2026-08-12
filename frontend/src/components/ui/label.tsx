import * as LabelPrimitive from "@radix-ui/react-label";
import type { ComponentProps } from "react";

import { cn } from "@/utils/cn";

function Label({ className, ...props }: ComponentProps<typeof LabelPrimitive.Root>) {
  return (
    <LabelPrimitive.Root
      className={cn("text-sm font-medium leading-none text-foreground", className)}
      {...props}
    />
  );
}

export { Label };
