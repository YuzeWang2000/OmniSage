import { Outlet, useLocation } from "react-router-dom";

import { MobileNavigation } from "@/layouts/mobile-navigation";
import { Sidebar } from "@/layouts/sidebar";
import { TopBar } from "@/layouts/top-bar";
import { cn } from "@/utils/cn";

export function AppShell() {
  const location = useLocation();
  const isChat = location.pathname === "/chat";

  return (
    <div className="min-h-screen bg-background">
      <a
        href="#main-content"
        className="fixed left-4 top-3 z-[100] -translate-y-20 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white focus:translate-y-0"
      >
        跳到主要内容
      </a>
      <Sidebar />
      <MobileNavigation />
      <TopBar />
      <main
        id="main-content"
        className={cn(
          "min-w-0 px-4 py-5 sm:px-6 sm:py-7 lg:ml-64 lg:px-8",
          isChat ? "h-[calc(100vh-4rem)] py-0 sm:py-0 lg:px-4" : "",
        )}
      >
        <div
          className={cn("mx-auto w-full min-w-0", isChat ? "h-full max-w-none" : "max-w-[1440px]")}
        >
          <Outlet />
        </div>
      </main>
    </div>
  );
}
