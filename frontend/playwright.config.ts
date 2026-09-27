import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "e2e",
  timeout: 30000,
  use: {
    baseURL: "http://127.0.0.1:8767",
    viewport: { width: 768, height: 1100 },
  },
  projects: [
    { name: "chromium", use: { browserName: "chromium" } },
    { name: "firefox", use: { browserName: "firefox" } },
    { name: "webkit", use: { browserName: "webkit" } },
  ],
  webServer: {
    command: "python3 demo/server.py",
    url: "http://127.0.0.1:8767/frontend/demo/",
    reuseExistingServer: false,
  },
  reporter: [["list"], ["json", { outputFile: "test-results/results.json" }]],
});
