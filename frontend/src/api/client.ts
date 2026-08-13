import axios, {
  AxiosError,
  type AxiosProgressEvent,
  type AxiosRequestConfig,
  type AxiosResponse,
} from "axios";

import { clearClientSession } from "@/lib/session";
import { useAuthStore } from "@/stores/auth-store";

const DEFAULT_REQUEST_TIMEOUT = 30_000;
export const uploadAdapter = "xhr" as const;
const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? "/api" : ""))
  .trim()
  .replace(/\/$/, "");

const parseTimeout = (value: string | undefined, fallback: number) => {
  const timeout = Number(value);
  return Number.isFinite(timeout) && timeout > 0 ? timeout : fallback;
};

export type ApiErrorKind =
  | "unauthorized"
  | "forbidden"
  | "not-found"
  | "validation"
  | "rate-limit"
  | "timeout"
  | "unavailable"
  | "server"
  | "cancelled"
  | "unknown";

export class ApiError extends Error {
  readonly status?: number;
  readonly kind: ApiErrorKind;
  readonly code?: string;
  readonly fieldErrors?: Record<string, string>;

  constructor(
    message: string,
    options: {
      status?: number;
      kind?: ApiErrorKind;
      code?: string;
      fieldErrors?: Record<string, string>;
      cause?: unknown;
    } = {},
  ) {
    super(message, { cause: options.cause });
    this.name = "ApiError";
    this.status = options.status;
    this.kind = options.kind || "unknown";
    this.code = options.code;
    this.fieldErrors = options.fieldErrors;
  }
}

export interface ApiRequestConfig<D = unknown> extends AxiosRequestConfig<D> {
  skipAuthFailure?: boolean;
}

interface ValidationIssue {
  loc?: Array<string | number>;
  msg?: string;
}

const getValidationErrors = (detail: unknown) => {
  if (!Array.isArray(detail)) return undefined;

  return detail.reduce<Record<string, string>>((errors, issue: ValidationIssue) => {
    if (!issue || typeof issue.msg !== "string") return errors;
    const path = Array.isArray(issue.loc)
      ? issue.loc.filter((part) => part !== "body").join(".")
      : "";
    errors[path || "form"] = issue.msg;
    return errors;
  }, {});
};

const safeDetail = (data: unknown) => {
  if (!data || typeof data !== "object") return undefined;
  const response = data as { detail?: unknown; error?: { message?: unknown } };
  const detail = typeof response.detail === "string"
    ? response.detail
    : response.error && typeof response.error.message === "string"
      ? response.error.message
      : undefined;
  if (typeof detail !== "string") return undefined;
  const clean = detail.replace(/[\r\n\t]+/g, " ").trim();
  return clean.length > 240 ? `${clean.slice(0, 237)}...` : clean;
};

const standardError = (data: unknown) => {
  if (!data || typeof data !== "object") return undefined;
  const value = (data as { error?: unknown }).error;
  if (!value || typeof value !== "object") return undefined;
  const code = (value as { code?: unknown }).code;
  const message = (value as { message?: unknown }).message;
  return {
    code: typeof code === "string" ? code : undefined,
    message: typeof message === "string" ? message : undefined,
  };
};

const apiErrorFromAxios = (error: AxiosError): ApiError => {
  if (axios.isCancel(error) || error.code === "ERR_CANCELED") {
    return new ApiError("请求已取消", { kind: "cancelled", cause: error });
  }

  if (error.code === "ECONNABORTED" || error.code === "ETIMEDOUT") {
    return new ApiError("请求超时，请稍后重试", { kind: "timeout", cause: error });
  }

  const status = error.response?.status;
  const backendError = standardError(error.response?.data);
  const detail = safeDetail(error.response?.data);
  const validation = getValidationErrors(
    error.response?.data && typeof error.response.data === "object"
      ? (error.response.data as { detail?: unknown }).detail
      : undefined,
  );

  switch (status) {
    case 401:
      if (backendError?.code === "CredentialInvalid") {
        return new ApiError(detail || "供应商拒绝了 API Key，请检查密钥和地域", {
          status,
          kind: "forbidden",
          code: backendError.code,
          cause: error,
        });
      }
      return new ApiError("登录状态已失效，请重新登录", {
        status,
        kind: "unauthorized",
        code: backendError?.code,
        cause: error,
      });
    case 424:
      return new ApiError(detail || "供应商凭据或上游依赖不可用", {
        status,
        kind: "forbidden",
        code: backendError?.code,
        cause: error,
      });
    case 403:
      return new ApiError(detail || "你没有权限执行此操作", {
        status,
        kind: "forbidden",
        cause: error,
      });
    case 404:
      return new ApiError(detail || "请求的内容不存在", {
        status,
        kind: "not-found",
        cause: error,
      });
    case 422:
      return new ApiError(detail || "提交内容有误，请检查后重试", {
        status,
        kind: "validation",
        fieldErrors: validation,
        cause: error,
      });
    case 429:
      return new ApiError("请求过于频繁，请稍后再试", {
        status,
        kind: "rate-limit",
        cause: error,
      });
    case 500:
      return new ApiError("服务暂时出现问题，请稍后重试", {
        status,
        kind: "server",
        cause: error,
      });
    case 502:
    case 503:
    case 504:
      return new ApiError("后端服务暂不可用，请确认服务已启动", {
        status,
        kind: "unavailable",
        cause: error,
      });
    default:
      return new ApiError(
        error.response ? detail || "请求失败，请稍后重试" : "无法连接到后端服务",
        { status, kind: error.response ? "unknown" : "unavailable", cause: error },
      );
  }
};

export const apiClient = axios.create({
  baseURL: apiBaseUrl,
  timeout: parseTimeout(import.meta.env.VITE_REQUEST_TIMEOUT_MS, DEFAULT_REQUEST_TIMEOUT),
  adapter: "fetch",
  headers: {
    Accept: "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.set("Authorization", `Bearer ${token}`);
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const apiError = apiErrorFromAxios(error);
    const requestConfig = error.config as ApiRequestConfig | undefined;
    if (
      apiError.status === 401 && apiError.kind === "unauthorized" &&
      !requestConfig?.skipAuthFailure &&
      useAuthStore.getState().token
    ) {
      clearClientSession("session-expired");
    }
    return Promise.reject(apiError);
  },
);

export async function apiRequest<T, D = unknown>(config: ApiRequestConfig<D>) {
  const response = await apiClient.request<T, AxiosResponse<T>, D>(config);
  return response.data;
}

export function uploadRequest<T>(
  config: ApiRequestConfig<FormData> & { onProgress?: (progress: number) => void },
) {
  const { onProgress, ...requestConfig } = config;
  return apiRequest<T, FormData>({
    ...requestConfig,
    // Axios' fetch adapter turns multipart uploads with progress tracking into
    // request streams. Those streams are not supported consistently by all
    // browsers and reverse proxies, where they surface as a generic network
    // error before FastAPI receives the request. XHR has reliable multipart
    // upload progress support in browsers.
    adapter: uploadAdapter,
    timeout: parseTimeout(import.meta.env.VITE_UPLOAD_TIMEOUT_MS, 180_000),
    onUploadProgress: (event: AxiosProgressEvent) => {
      if (!event.total || !onProgress) return;
      onProgress(Math.min(100, Math.round((event.loaded / event.total) * 100)));
    },
  });
}

export { apiBaseUrl };
