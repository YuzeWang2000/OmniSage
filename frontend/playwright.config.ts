import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  globalSetup: "./tests/e2e/global-setup.ts",
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: "http://127.0.0.1:4173",
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      testIgnore: /mobile-overflow\.spec\.ts/,
      use: { ...devices["Desktop Chrome"], browserName: "chromium", channel: "chrome" },
    },
    {
      name: "mobile-390",
      testMatch: /mobile-overflow\.spec\.ts/,
      use: {
        ...devices["iPhone 13"],
        browserName: "chromium",
        channel: "chrome",
        viewport: { width: 390, height: 844 },
      },
    },
  ],
});
