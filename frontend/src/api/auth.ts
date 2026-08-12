import { apiRequest } from "@/api/client";
import type { AuthResponse, User, UserCreate, UserLogin } from "@/api/types";

export function login(payload: UserLogin, signal?: AbortSignal) {
  return apiRequest<AuthResponse, UserLogin>({
    method: "POST",
    url: "/auth/login",
    data: payload,
    signal,
    skipAuthFailure: true,
  });
}

export function register(payload: UserCreate, signal?: AbortSignal) {
  return apiRequest<User, UserCreate>({
    method: "POST",
    url: "/auth/register",
    data: payload,
    signal,
    skipAuthFailure: true,
  });
}

export function getCurrentUser(signal?: AbortSignal) {
  return apiRequest<User>({
    method: "GET",
    url: "/auth/me",
    signal,
  });
}
