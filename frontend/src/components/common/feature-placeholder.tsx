import type { LucideIcon } from "lucide-react";

interface FeaturePlaceholderProps {
  icon: LucideIcon;
  eyebrow: string;
  title: string;
  description: string;
}

export function FeaturePlaceholder({
  icon: Icon,
  eyebrow,
  title,
  description,
}: FeaturePlaceholderProps) {
  return (
    <section className="rounded-2xl border bg-surface p-6 shadow-xs sm:p-8">
      <span className="grid size-10 place-items-center rounded-xl bg-[#eaf4f0] text-primary">
        <Icon className="size-5" aria-hidden="true" />
      </span>
      <p className="mt-5 text-xs font-semibold uppercase tracking-[0.16em] text-primary">
        {eyebrow}
      </p>
      <h1 className="mt-2 text-2xl font-semibold tracking-tight">{title}</h1>
      <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">{description}</p>
    </section>
  );
}
