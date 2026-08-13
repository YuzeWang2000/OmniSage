import { expect, test } from "@playwright/test";

import { installMockApi, seedAuthenticatedSession } from "./mock-api";

test("登录、工作台和退出流程", async ({ page }) => {
  await installMockApi(page);
  await page.goto("/");
  await page.getByLabel("用户名").fill("e2e-user");
  await page.getByLabel("密码").fill(crypto.randomUUID());
  await page.getByRole("button", { name: "登录" }).click();
  await expect(page).toHaveURL("/");
  await expect(page.getByRole("heading", { name: "你好，e2e-user" })).toBeVisible();
  await page.getByRole("button", { name: "打开用户菜单" }).click();
  await page.getByRole("menuitem", { name: "退出登录" }).click();
  await expect(page).toHaveURL(/\/login$/);
});

test("连接范围模型与标准 SSE 聊天", async ({ page }) => {
  await installMockApi(page);
  await seedAuthenticatedSession(page);
  await page.goto("/chat");
  await expect(page.getByRole("heading", { name: "产品手册问答" })).toBeVisible();
  await expect(page.getByLabel("模型")).toHaveValue("ollama::local::qwen-local");
  await page.getByRole("textbox", { name: "消息" }).fill("请解释 RAG");
  await page.getByRole("button", { name: "发送消息" }).click();
  await expect(page.getByText("测试回答").first()).toBeVisible();
  await expect(page.getByText("已根据可信来源完成回答。")).toBeVisible();
});

test("删除最后一个会话后安全进入空会话状态", async ({ page }) => {
  await installMockApi(page);
  await seedAuthenticatedSession(page);
  await page.goto("/chat?conversation=41");
  await expect(page.getByRole("heading", { name: "产品手册问答" })).toBeVisible();
  await page.getByRole("button", { name: "删除对话：产品手册问答" }).click();
  await page.getByRole("button", { name: "确认删除" }).click();
  await expect(page).toHaveURL(/\/chat$/);
  await expect(page.getByText("还没有对话")).toBeVisible();
  await expect(page.getByRole("heading", { name: "页面遇到问题" })).toHaveCount(0);
});

test("供应商连接表单不回显完整密钥", async ({ page }) => {
  await installMockApi(page);
  await seedAuthenticatedSession(page);
  await page.goto("/settings");
  await page.getByLabel("供应商").selectOption("deepseek");
  await page.getByLabel("连接名称").fill("E2E DeepSeek");
  const rawKey = `sk-${crypto.randomUUID()}`;
  await page.getByLabel("API Key").fill(rawKey);
  await page.getByRole("button", { name: "添加连接" }).click();
  await expect(page.getByText("E2E DeepSeek")).toBeVisible();
  await expect(page.getByText("sk-••••ret")).toBeVisible();
  await expect(page.getByText(rawKey)).toHaveCount(0);
});

test("可以停止仍在进行的标准事件流", async ({ page }) => {
  await installMockApi(page);
  let releaseResponse: (() => void) | undefined;
  await page.route("**/api/chat/stream", async (route) => {
    await new Promise<void>((resolve) => { releaseResponse = resolve; });
    try {
      await route.fulfill({ status: 200, contentType: "text/event-stream", body: 'data: {"type":"done"}\n\n' });
    } catch { /* browser cancellation is expected */ }
  });
  await seedAuthenticatedSession(page);
  await page.goto("/chat");
  await page.getByRole("textbox", { name: "消息" }).fill("请停止生成");
  await page.getByRole("button", { name: "发送消息" }).click();
  await expect.poll(() => Boolean(releaseResponse)).toBe(true);
  await page.getByRole("button", { name: "停止生成" }).click();
  await expect(page.getByText("已停止生成。")).toBeVisible();
  releaseResponse?.();
});
