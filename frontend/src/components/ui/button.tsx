import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import type { ButtonHTMLAttributes } from "react";

import { cn } from "@/utils/cn";

const buttonVariants = cva(
  "inline-flex min-h-11 items-center justify-center gap-2 rounded-xl px-4 text-sm font-medium transition-colors disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-[#185b4d]",
        secondary: "border bg-surface text-foreground hover:bg-[#f1f4f5]",
        ghost: "text-muted hover:bg-[#edf1f2] hover:text-foreground",
        destructive: "bg-danger text-white hover:bg-[#912018]",
      },
      size: {
        default: "h-11 px-4",
        sm: "h-9 min-h-9 rounded-lg px-3 text-xs",
        icon: "size-11 p-0",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

function Button({ className, variant, size, asChild = false, ...props }: ButtonProps) {
  const Component = asChild ? Slot : "button";
  return <Component className={cn(buttonVariants({ variant, size }), className)} {...props} />;
}

export { Button };
