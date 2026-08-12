import { expect, test } from "@playwright/test";

import { installMockApi, seedAuthenticatedSession } from "./mock-api";

test("登录进入工作台，退出后受保护路由重新要求登录", async ({ page }) => {
  await installMockApi(page);
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "欢迎回来" })).toBeVisible();
  await page.getByLabel("用户名").fill("e2e-user");
  await page.getByLabel("密码").fill(crypto.randomUUID());
  await page.getByRole("button", { name: "登录" }).click();

  await expect(page).toHaveURL("/");
  await expect(page.getByRole("heading", { name: "你好，e2e-user" })).toBeVisible();
  await expect(page.getByText("最近对话")).toBeVisible();

  await page.getByRole("button", { name: "打开用户菜单" }).click();
  await page.getByRole("menuitem", { name: "退出登录" }).click();
  await expect(page).toHaveURL(/\/login$/);

  await page.goto("/settings");
  await expect(page).toHaveURL(/\/login\?from=%2Fsettings$/);
});

test("选择对话、切换 RAG 与 Wiki 并显示流式回答和引用", async ({ page }) => {
  await installMockApi(page);
  await seedAuthenticatedSession(page);
  await page.goto("/chat");

  await expect(page.getByRole("heading", { name: "产品手册问答" })).toBeVisible();
  await expect(page.getByText("可以在搜索页选择知识库并输入关键词。")).toBeVisible();

  const rag = page.getByRole("switch", { name: "启用 RAG" });
  const wiki = page.getByRole("switch", { name: "启用 Wiki" });
  await rag.click();
  await wiki.click();
  await expect(rag).toBeChecked();
  await expect(wiki).toBeChecked();

  await page.getByRole("textbox", { name: "消息" }).fill("请解释 RAG");
  await page.getByRole("button", { name: "发送消息" }).click();

  await expect(page.getByText("查看 1 条引用来源")).toBeVisible();
  await expect(page.getByText("测试回答").first()).toBeVisible();
  await expect(page.getByText("已根据可信来源完成回答。")).toBeVisible();
  await page.getByText("查看 1 条引用来源").click();
  await expect(page.getByText("检索增强生成")).toBeVisible();
  await expect(page.getByText("相关度 96.0%")).toBeVisible();
});

test("可以停止仍在进行的流式回答", async ({ page }) => {
  await installMockApi(page);
  let releaseResponse: (() => void) | undefined;
  await page.route("**/api/chat/stream", async (route) => {
    await new Promise<void>((resolve) => {
      releaseResponse = resolve;
    });
    try {
      await route.fulfill({
        status: 200,
        contentType: "text/event-stream",
        body: 'data: {"done":true}\n\n',
      });
    } catch {
      // Aborting the fetch is the behavior under test; the intercepted route may already be gone.
    }
  });
  await seedAuthenticatedSession(page);
  await page.goto("/chat");

  await page.getByRole("textbox", { name: "消息" }).fill("请停止这次生成");
  await page.getByRole("button", { name: "发送消息" }).click();
  await expect.poll(() => Boolean(releaseResponse)).toBe(true);
  await page.getByRole("button", { name: "停止生成" }).click();
  await expect(page.getByText("已停止生成。")).toBeVisible();
  releaseResponse?.();
});

test("创建知识库、上传文档、执行搜索并安全管理 API Key", async ({ page }) => {
  await installMockApi(page);
  await seedAuthenticatedSession(page);
  await page.goto("/knowledge");

  await page.getByRole("button", { name: "创建知识库" }).first().click();
  await page.getByLabel("名称").fill("E2E 知识库");
  await page.getByLabel("描述（可选）").fill("端到端验收资料");
  await page.getByRole("button", { name: "创建知识库" }).last().click();
  await expect(page.getByRole("heading", { name: "E2E 知识库" })).toBeVisible();

  await page.locator("#knowledge-file").setInputFiles({
    name: "guide.md",
    mimeType: "text/markdown",
    buffer: Buffer.from("# Search\nUse the search workspace."),
  });
  await expect(page.getByText("guide.md")).toBeVisible();
  await expect(page.getByText("已完成", { exact: true })).toBeVisible();

  await page.getByRole("link", { name: "搜索" }).click();
  await page.getByRole("searchbox", { name: "搜索关键词" }).fill("检索增强");
  await page.getByRole("button", { name: "立即搜索" }).click();
  await expect(page.getByText("检索增强生成")).toBeVisible();
  await page.getByRole("button", { name: "查看搜索结果：检索增强生成" }).click();
  await expect(
    page
      .getByRole("dialog", { name: "检索增强生成" })
      .getByText("RAG 将检索到的可信上下文提供给生成模型。"),
  ).toBeVisible();
  await page.getByRole("button", { name: "关闭搜索结果详情" }).click();

  await page.getByRole("link", { name: "设置" }).click();
  await expect(page.getByRole("heading", { name: "设置" })).toBeVisible();
  await page.getByRole("button", { name: "添加", exact: true }).click();
  const rawKey = `sk-${crypto.randomUUID()}`;
  await page.getByLabel("API Key", { exact: true }).fill(rawKey);
  await page.getByLabel("模型名称（可选）").fill("deepseek-chat");
  await page.getByRole("button", { name: "添加密钥" }).click();

  await expect(page.getByText("API Key 已添加")).toBeVisible();
  await expect(page.getByText("•••• •••• ••••")).toBeVisible();
  await expect(page.getByText(rawKey)).toHaveCount(0);
});
