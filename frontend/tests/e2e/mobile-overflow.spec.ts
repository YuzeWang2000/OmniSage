import { expect, test } from "@playwright/test";

import { installMockApi, seedAuthenticatedSession } from "./mock-api";

test("390px 下主要页面、导航和弹窗均无横向溢出", async ({ page }) => {
  await installMockApi(page);
  await seedAuthenticatedSession(page);
  const consoleErrors: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });

  for (const path of ["/", "/chat", "/knowledge", "/search", "/settings"]) {
    await page.goto(path);
    await expect(page.locator("main").first()).toBeVisible();
    const dimensions = await page.evaluate(() => ({
      viewport: window.innerWidth,
      document: document.documentElement.scrollWidth,
      body: document.body.scrollWidth,
    }));
    expect(dimensions.document).toBeLessThanOrEqual(dimensions.viewport);
    expect(dimensions.body).toBeLessThanOrEqual(dimensions.viewport);
  }

  await page.goto("/");
  await page.getByRole("button", { name: "打开导航" }).click();
  const drawer = page.getByRole("dialog", { name: "主导航" });
  await expect(drawer).toBeVisible();
  const drawerBounds = await drawer.boundingBox();
  expect(drawerBounds).not.toBeNull();
  expect(drawerBounds!.x).toBeGreaterThanOrEqual(0);
  expect(drawerBounds!.x + drawerBounds!.width).toBeLessThanOrEqual(390);
  await page.getByRole("button", { name: "关闭导航" }).click();

  await page.goto("/knowledge");
  await page.getByRole("button", { name: "创建知识库" }).first().click();
  const dialog = page.getByRole("dialog", { name: "创建知识库" });
  const dialogBounds = await dialog.boundingBox();
  expect(dialogBounds).not.toBeNull();
  expect(dialogBounds!.x).toBeGreaterThanOrEqual(0);
  expect(dialogBounds!.x + dialogBounds!.width).toBeLessThanOrEqual(390);
  expect(dialogBounds!.y).toBeGreaterThanOrEqual(0);
  expect(dialogBounds!.y + dialogBounds!.height).toBeLessThanOrEqual(844);
  expect(consoleErrors).toEqual([]);
});
