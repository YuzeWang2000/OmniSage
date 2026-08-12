import {
  AxiosError,
  AxiosHeaders,
  type AxiosAdapter,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from "axios";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ApiError, apiRequest, uploadAdapter } from "@/api/client";
import { restoreDefaultSessionRedirectHandler, setSessionRedirectHandler } from "@/lib/session";
import { useAuthStore } from "@/stores/auth-store";
import { useChatStore } from "@/stores/chat-store";

function rejectedAdapter(status: number, data: unknown): AxiosAdapter {
  return async (config: InternalAxiosRequestConfig) => {
    const response: AxiosResponse = {
      data,
      status,
      statusText: "Unauthorized",
      headers: new AxiosHeaders(),
      config,
    };
    throw new AxiosError("Request failed", "ERR_BAD_REQUEST", config, undefined, response);
  };
}

describe("API 401 handling", () => {
  beforeEach(() => {
    useAuthStore.setState({
      token: "expired-token",
      user: { user_id: 3, username: "sage" },
      hasHydrated: true,
    });
    useChatStore.getState().setActiveConversationId(99);
  });

  afterEach(() => restoreDefaultSessionRedirectHandler());

  it("clears user state and redirects without exposing credentials", async () => {
    const redirect = vi.fn();
    setSessionRedirectHandler(redirect);

    await expect(
      apiRequest({
        method: "GET",
        url: "/private",
        adapter: rejectedAdapter(401, { detail: "expired" }),
      }),
    ).rejects.toMatchObject({ kind: "unauthorized", status: 401 } satisfies Partial<ApiError>);

    expect(useAuthStore.getState().token).toBeNull();
    expect(useAuthStore.getState().user).toBeNull();
    expect(useChatStore.getState().activeConversationId).toBeNull();
    expect(redirect).toHaveBeenCalledWith("session-expired");
  });
});

describe("file uploads", () => {
  it("uses XHR so multipart progress does not become an unsupported fetch stream", () => {
    expect(uploadAdapter).toBe("xhr");
  });
});
