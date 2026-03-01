import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: ".",
  testIgnore: ["webhook.spec.ts"],
  timeout: 30000,
  retries: 0,
  use: {
    baseURL: "http://localhost:5173",
    headless: true,
  },
  webServer: [
    {
      command: "cd ../../backend/src && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000",
      port: 8000,
      reuseExistingServer: true,
    },
    {
      command: "cd ../../frontend && npm run dev",
      port: 5173,
      reuseExistingServer: true,
    },
  ],
});
