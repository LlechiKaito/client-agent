import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: ".",
  testMatch: "webhook.spec.ts",
  timeout: 30000,
  retries: 0,
  use: {
    baseURL: "http://localhost:8000",
    headless: true,
  },
  webServer: {
    command:
      "cd ../../backend/src && LINE_CHANNEL_SECRET=test-e2e-secret LINE_CHANNEL_ACCESS_TOKEN=test-e2e-token python3 -m uvicorn main:app --host 0.0.0.0 --port 8000",
    port: 8000,
    reuseExistingServer: false,
  },
});
