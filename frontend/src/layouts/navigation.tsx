import { Database, LayoutDashboard, MessageSquareText, Search, Settings } from "lucide-react";
import { NavLink } from "react-router-dom";

import { cn } from "@/utils/cn";

const navigationItems = [
  { label: "工作台", to: "/", icon: LayoutDashboard, end: true },
  { label: "智能对话", to: "/chat", icon: MessageSquareText },
  { label: "知识库", to: "/knowledge", icon: Database },
  { label: "搜索", to: "/search", icon: Search },
  { label: "设置", to: "/settings", icon: Settings },
];

export function Navigation({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav aria-label="主导航" className="space-y-1">
      {navigationItems.map(({ label, to, icon: Icon, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          onClick={onNavigate}
          className={({ isActive }) =>
            cn(
              "group flex min-h-11 items-center gap-3 rounded-xl px-3 text-sm font-medium text-[#667085] transition-colors",
              "hover:bg-[#eef2f1] hover:text-[#25332d]",
              isActive && "bg-[#e8f2ee] text-[#145b4d]",
            )
          }
        >
          <Icon className="size-[18px] shrink-0" strokeWidth={1.9} aria-hidden="true" />
          <span>{label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
