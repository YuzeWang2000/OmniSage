import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { useQuery } from "@tanstack/react-query";
import { ChevronDown, LogOut, Menu, UserRound } from "lucide-react";
import { useLocation } from "react-router-dom";

import { getHealth } from "@/api/system";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { clearClientSession } from "@/lib/session";
import { useAuthStore } from "@/stores/auth-store";
import { useUiStore } from "@/stores/ui-store";

const pageNames: Record<string, string> = {
  "/": "工作台",
  "/chat": "智能对话",
  "/knowledge": "知识库",
  "/search": "搜索",
  "/settings": "设置",
};

export function TopBar() {
  const location = useLocation();
  const user = useAuthStore((state) => state.user);
  const openMobileNavigation = useUiStore((state) => state.setMobileNavigationOpen);
  const health = useQuery({
    queryKey: ["system", "health"],
    queryFn: ({ signal }) => getHealth(signal),
    staleTime: 20_000,
    refetchInterval: 30_000,
    retry: 1,
  });
  const online = health.data?.status === "ok";

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between gap-4 border-b bg-background/95 px-4 backdrop-blur sm:px-6 lg:ml-64 lg:px-8">
      <div className="flex min-w-0 items-center gap-3">
        <Button
          variant="ghost"
          size="icon"
          className="shrink-0 lg:hidden"
          aria-label="打开导航"
          onClick={() => openMobileNavigation(true)}
        >
          <Menu className="size-5" aria-hidden="true" />
        </Button>
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold sm:text-base">
            {pageNames[location.pathname] || "OmniSage"}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2 sm:gap-3">
        <Badge tone={online ? "success" : health.isPending ? "neutral" : "danger"}>
          <span
            className={`size-1.5 rounded-full ${online ? "bg-[#12b76a]" : health.isPending ? "bg-[#98a2b3]" : "bg-danger"}`}
            aria-hidden="true"
          />
          <span className="hidden sm:inline">
            {online ? "服务正常" : health.isPending ? "正在连接" : "服务离线"}
          </span>
          <span className="sm:hidden">
            {online ? "在线" : health.isPending ? "连接中" : "离线"}
          </span>
        </Badge>

        <DropdownMenu.Root>
          <DropdownMenu.Trigger asChild>
            <Button variant="ghost" className="max-w-[170px] px-2.5" aria-label="打开用户菜单">
              <span className="grid size-8 shrink-0 place-items-center rounded-full bg-[#e8f2ee] text-xs font-semibold text-primary">
                {user?.username.slice(0, 1).toUpperCase() || "U"}
              </span>
              <span className="hidden truncate text-sm sm:inline">{user?.username}</span>
              <ChevronDown className="hidden size-4 text-muted sm:block" aria-hidden="true" />
            </Button>
          </DropdownMenu.Trigger>
          <DropdownMenu.Portal>
            <DropdownMenu.Content
              align="end"
              sideOffset={8}
              className="z-50 min-w-52 rounded-xl border bg-surface p-1.5 shadow-lg outline-none"
            >
              <DropdownMenu.Label className="px-2.5 py-2">
                <span className="block text-xs text-muted">当前账户</span>
                <span className="mt-0.5 block truncate text-sm font-medium">{user?.username}</span>
              </DropdownMenu.Label>
              <DropdownMenu.Separator className="my-1 h-px bg-border" />
              <DropdownMenu.Item className="flex min-h-10 items-center gap-2 rounded-lg px-2.5 text-sm text-muted outline-none focus:bg-[#eef2f1] focus:text-foreground">
                <UserRound className="size-4" aria-hidden="true" />
                账户 ID {user?.user_id}
              </DropdownMenu.Item>
              <DropdownMenu.Item
                className="flex min-h-10 cursor-pointer items-center gap-2 rounded-lg px-2.5 text-sm text-danger outline-none focus:bg-[#fef3f2]"
                onSelect={() => clearClientSession("manual")}
              >
                <LogOut className="size-4" aria-hidden="true" />
                退出登录
              </DropdownMenu.Item>
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>
      </div>
    </header>
  );
}
