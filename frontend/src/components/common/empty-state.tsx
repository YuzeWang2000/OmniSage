import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: ReactNode;
  compact?: boolean;
}

export function EmptyState({ icon: Icon, title, description, action, compact }: EmptyStateProps) {
  return (
    <div className={`grid place-items-center text-center ${compact ? "px-4 py-8" : "px-5 py-14"}`}>
      <span className="grid size-10 place-items-center rounded-xl bg-[#eef2f1] text-primary">
        <Icon className="size-5" aria-hidden="true" />
      </span>
      <h3 className="mt-4 text-sm font-semibold">{title}</h3>
      <p className="mt-1 max-w-sm text-xs leading-5 text-muted">{description}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
