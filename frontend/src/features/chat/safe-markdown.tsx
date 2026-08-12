import { Check, Copy } from "lucide-react";
import { Children, isValidElement, memo, type ReactNode, useState } from "react";
import ReactMarkdown from "react-markdown";
import rehypeSanitize from "rehype-sanitize";
import remarkGfm from "remark-gfm";

import { Button } from "@/components/ui/button";

function nodeText(node: ReactNode): string {
  if (typeof node === "string" || typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(nodeText).join("");
  if (isValidElement<{ children?: ReactNode }>(node)) return nodeText(node.props.children);
  return "";
}

function CodeBlock({ children }: { children?: ReactNode }) {
  const [copied, setCopied] = useState(false);
  const code = nodeText(children).replace(/\n$/, "");

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1_500);
    } catch {
      setCopied(false);
    }
  };

  return (
    <div className="my-4 min-w-0 overflow-hidden rounded-xl border bg-[#101828] text-[#f2f4f7]">
      <div className="flex min-h-10 items-center justify-between border-b border-white/10 px-3">
        <span className="text-[11px] font-medium text-[#98a2b3]">代码</span>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="min-h-8 text-[#d0d5dd] hover:bg-white/10 hover:text-white"
          onClick={() => void copy()}
          aria-label="复制代码"
        >
          {copied ? <Check className="size-3.5" /> : <Copy className="size-3.5" />}
          {copied ? "已复制" : "复制"}
        </Button>
      </div>
      <pre className="max-w-full overflow-x-auto p-4 text-[13px] leading-6">{children}</pre>
    </div>
  );
}

function SafeMarkdownComponent({ content }: { content: string }) {
  return (
    <div className="chat-markdown min-w-0 break-words text-sm leading-7">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeSanitize]}
        components={{
          a: ({ href, children }) => {
            if (!href) return <span>{children}</span>;
            const external = /^https?:\/\//i.test(href);
            return (
              <a
                href={href}
                target={external ? "_blank" : undefined}
                rel={external ? "noopener noreferrer nofollow" : undefined}
              >
                {children}
              </a>
            );
          },
          img: ({ alt }) => (
            <span className="text-xs text-muted">[已隐藏图片：{alt || "无说明"}]</span>
          ),
          pre: ({ children }) => <CodeBlock>{children}</CodeBlock>,
          code: ({ className, children }) => (
            <code className={className}>{Children.toArray(children)}</code>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

export const SafeMarkdown = memo(SafeMarkdownComponent);
