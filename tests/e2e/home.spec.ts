import { test, expect } from "@playwright/test";

test.describe("Home Page", () => {
  test("should display the page title", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toHaveText("Client Agent");
  });

  test("should show health status when API is available", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator('[data-testid="health-status"]')).toBeVisible({
      timeout: 10000,
    });
    await expect(page.locator('[data-testid="health-status"]')).toHaveText(
      "healthy",
    );
  });

  test("should show 404 page for unknown routes", async ({ page }) => {
    await page.goto("/unknown-route");
    await expect(page.locator("h1")).toHaveText("404");
  });
});
