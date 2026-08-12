import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { LoaderCircle } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useLocation, useNavigate } from "react-router-dom";
import { z } from "zod";

import { login, register } from "@/api/auth";
import { ApiError } from "@/api/client";
import { StatusMessage } from "@/components/common/status-message";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuthStore } from "@/stores/auth-store";

type AuthMode = "login" | "register";

const loginSchema = z.object({
  username: z.string().trim().min(1, "请输入用户名"),
  password: z.string().min(1, "请输入密码"),
  confirmPassword: z.string().optional(),
});

const registerSchema = loginSchema.superRefine((value, context) => {
  if (value.password !== value.confirmPassword) {
    context.addIssue({
      code: "custom",
      path: ["confirmPassword"],
      message: "两次输入的密码不一致",
    });
  }
  if (new TextEncoder().encode(value.password).length > 72) {
    context.addIssue({
      code: "custom",
      path: ["password"],
      message: "密码不能超过 72 个 UTF-8 字节",
    });
  }
});

type AuthFormValues = z.infer<typeof loginSchema>;

export function AuthForm() {
  const [mode, setMode] = useState<AuthMode>("login");
  const [notice, setNotice] = useState<string | null>(null);
  const setAuthenticated = useAuthStore((state) => state.setAuthenticated);
  const navigate = useNavigate();
  const location = useLocation();
  const form = useForm<AuthFormValues>({
    resolver: zodResolver(mode === "login" ? loginSchema : registerSchema),
    defaultValues: { username: "", password: "", confirmPassword: "" },
  });

  const mutation = useMutation({
    mutationFn: async (values: AuthFormValues) => {
      if (mode === "register") {
        await register({ username: values.username.trim(), password: values.password });
        return null;
      }
      return login({ username: values.username.trim(), password: values.password });
    },
    onSuccess: (response) => {
      if (!response) {
        setMode("login");
        setNotice("注册成功，请使用新账户登录");
        form.reset({ username: form.getValues("username"), password: "", confirmPassword: "" });
        return;
      }

      setAuthenticated(response.access_token, {
        user_id: response.user_id,
        username: response.username,
      });
      const from = new URLSearchParams(location.search).get("from");
      navigate(from?.startsWith("/") ? from : "/", { replace: true });
    },
  });

  const switchMode = () => {
    setMode((current) => (current === "login" ? "register" : "login"));
    setNotice(null);
    mutation.reset();
    form.reset();
  };

  const errorMessage = mutation.error
    ? mutation.error instanceof ApiError
      ? mutation.error.message
      : "操作失败，请稍后重试"
    : null;

  return (
    <div className="w-full">
      <div className="mb-7">
        <p className="text-sm font-semibold tracking-wide text-primary">OMNISAGE</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-[-0.03em]">
          {mode === "login" ? "欢迎回来" : "创建账户"}
        </h1>
        <p className="mt-2 text-sm leading-6 text-muted">
          {mode === "login" ? "登录后继续你的知识工作。" : "注册后即可创建知识库并开始问答。"}
        </p>
      </div>

      <form className="space-y-4" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}>
        <div className="space-y-2">
          <Label htmlFor="username">用户名</Label>
          <Input
            id="username"
            autoComplete="username"
            aria-invalid={Boolean(form.formState.errors.username)}
            {...form.register("username")}
          />
          {form.formState.errors.username && (
            <p className="text-xs text-danger">{form.formState.errors.username.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="password">密码</Label>
          <Input
            id="password"
            type="password"
            autoComplete={mode === "login" ? "current-password" : "new-password"}
            aria-invalid={Boolean(form.formState.errors.password)}
            {...form.register("password")}
          />
          {form.formState.errors.password && (
            <p className="text-xs text-danger">{form.formState.errors.password.message}</p>
          )}
        </div>

        {mode === "register" && (
          <div className="space-y-2">
            <Label htmlFor="confirm-password">确认密码</Label>
            <Input
              id="confirm-password"
              type="password"
              autoComplete="new-password"
              aria-invalid={Boolean(form.formState.errors.confirmPassword)}
              {...form.register("confirmPassword")}
            />
            {form.formState.errors.confirmPassword && (
              <p className="text-xs text-danger">{form.formState.errors.confirmPassword.message}</p>
            )}
          </div>
        )}

        {notice && <StatusMessage tone="success">{notice}</StatusMessage>}
        {errorMessage && <StatusMessage tone="error">{errorMessage}</StatusMessage>}

        <Button className="w-full" type="submit" disabled={mutation.isPending}>
          {mutation.isPending && (
            <LoaderCircle className="size-4 animate-spin" aria-hidden="true" />
          )}
          {mutation.isPending ? "正在提交" : mode === "login" ? "登录" : "注册"}
        </Button>
      </form>

      <Button className="mt-3 w-full" type="button" variant="ghost" onClick={switchMode}>
        {mode === "login" ? "没有账户？创建一个" : "已有账户？返回登录"}
      </Button>
    </div>
  );
}
