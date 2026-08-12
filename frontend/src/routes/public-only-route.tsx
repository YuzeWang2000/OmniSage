import { Navigate, Outlet } from "react-router-dom";

import { useAuthStore } from "@/stores/auth-store";

export function PublicOnlyRoute() {
  const token = useAuthStore((state) => state.token);
  const user = useAuthStore((state) => state.user);
  return token && user ? <Navigate to="/" replace /> : <Outlet />;
}
