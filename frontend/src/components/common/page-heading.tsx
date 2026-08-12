import type { ReactNode } from "react";

interface PageHeadingProps {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: ReactNode;
}

export function PageHeading({ eyebrow, title, description, actions }: PageHeadingProps) {
  return (
    <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div className="min-w-0">
        {eyebrow && (
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-primary">
            {eyebrow}
          </p>
        )}
        <h1 className="mt-1 text-2xl font-semibold tracking-[-0.025em] sm:text-3xl">{title}</h1>
        {description && (
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">{description}</p>
        )}
      </div>
      {actions && <div className="flex shrink-0 flex-wrap gap-2">{actions}</div>}
    </header>
  );
}
