import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { PageLoading } from "@/components/common/page-loading";
import { AppShell } from "@/layouts/app-shell";
import { ProtectedRoute } from "@/routes/protected-route";
import { PublicOnlyRoute } from "@/routes/public-only-route";

const LoginPage = lazy(() => import("@/pages/LoginPage"));
const DashboardPage = lazy(() => import("@/pages/DashboardPage"));
const ChatPage = lazy(() => import("@/pages/ChatPage"));
const KnowledgePage = lazy(() => import("@/pages/KnowledgePage"));
const SearchPage = lazy(() => import("@/pages/SearchPage"));
const SettingsPage = lazy(() => import("@/pages/SettingsPage"));

export default function App() {
  return (
    <Suspense fallback={<PageLoading />}>
      <Routes>
        <Route element={<PublicOnlyRoute />}>
          <Route path="/login" element={<LoginPage />} />
        </Route>
        <Route element={<ProtectedRoute />}>
          <Route element={<AppShell />}>
            <Route index element={<DashboardPage />} />
            <Route path="chat" element={<ChatPage />} />
            <Route path="knowledge" element={<KnowledgePage />} />
            <Route path="search" element={<SearchPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
}
