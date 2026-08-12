import { BrainCircuit, Database, Search } from "lucide-react";

import { AuthForm } from "@/features/auth/auth-form";

const capabilities = [
  { icon: BrainCircuit, label: "智能问答", copy: "在连续对话中结合模型、RAG 与 Wiki。" },
  { icon: Database, label: "知识库", copy: "集中上传、索引并管理你的资料。" },
  { icon: Search, label: "可信检索", copy: "查看来源、页码、章节与相关度。" },
];

export default function LoginPage() {
  return (
    <main className="grid min-h-screen grid-cols-1 bg-background lg:grid-cols-[minmax(0,1.15fr)_minmax(420px,0.85fr)]">
      <section className="hidden border-r bg-[#edf4f1] p-12 lg:flex lg:flex-col lg:justify-between">
        <div className="flex items-center gap-3">
          <span className="grid size-10 place-items-center rounded-xl bg-primary text-white">
            O
          </span>
          <span className="text-lg font-semibold">OmniSage</span>
        </div>
        <div className="max-w-xl py-16">
          <p className="text-sm font-semibold text-primary">知识，与答案之间</p>
          <h2 className="mt-5 text-5xl font-semibold leading-[1.08] tracking-[-0.045em] text-[#17251f]">
            让团队知识成为
            <br />
            随时可用的判断力。
          </h2>
          <div className="mt-10 grid gap-4 sm:grid-cols-3">
            {capabilities.map(({ icon: Icon, label, copy }) => (
              <div key={label} className="rounded-2xl border border-[#d6e5de] bg-white/70 p-4">
                <Icon className="size-5 text-primary" aria-hidden="true" />
                <p className="mt-4 text-sm font-semibold">{label}</p>
                <p className="mt-1 text-xs leading-5 text-muted">{copy}</p>
              </div>
            ))}
          </div>
        </div>
        <p className="text-xs text-muted">Private knowledge. Clear answers.</p>
      </section>

      <section className="flex min-h-screen items-center justify-center px-5 py-10 sm:px-10">
        <div className="w-full max-w-md rounded-3xl border bg-surface p-6 shadow-[0_20px_60px_rgba(28,45,38,0.08)] sm:p-9">
          <AuthForm />
        </div>
      </section>
    </main>
  );
}
