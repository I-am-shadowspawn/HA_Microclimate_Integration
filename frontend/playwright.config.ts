import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "e2e",
  timeout: 30000,
  use: {
    baseURL: "http://127.0.0.1:8767",
    viewport: { width: 768, height: 1100 },
  },
  webServer: {
    command: "python3 -m http.server 8767 --bind 127.0.0.1 --directory ..",
    url: "http://127.0.0.1:8767/frontend/demo/",
    reuseExistingServer: false,
  },
  reporter: [["list"], ["json", { outputFile: "test-results/results.json" }]],
});
