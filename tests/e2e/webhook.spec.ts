import { test, expect } from "@playwright/test";
import * as crypto from "crypto";

const BACKEND_URL = "http://localhost:8000";
const E2E_CHANNEL_SECRET = "test-e2e-secret";

function generateSignature(body: string, secret: string): string {
  const hmac = crypto.createHmac("sha256", secret);
  hmac.update(body);
  return hmac.digest("base64");
}

function buildWebhookBody(events: object[]): string {
  return JSON.stringify({ destination: "U1234567890", events });
}

test.describe("LINE Webhook Endpoint", () => {
  test("should return 400 when signature is invalid", async ({ request }) => {
    const body = buildWebhookBody([]);

    const response = await request.post(`${BACKEND_URL}/callback`, {
      data: body,
      headers: {
        "Content-Type": "application/json",
        "X-Line-Signature": "invalid-signature",
      },
    });

    expect(response.status()).toBe(400);
    const json = await response.json();
    expect(json.is_success).toBe(false);
    expect(json.code).toBe("INVALID_SIGNATURE");
  });

  test("should return 200 with valid signature and empty events", async ({
    request,
  }) => {
    const channelSecret = E2E_CHANNEL_SECRET;
    const body = buildWebhookBody([]);
    const signature = generateSignature(body, channelSecret);

    const response = await request.post(`${BACKEND_URL}/callback`, {
      data: body,
      headers: {
        "Content-Type": "application/json",
        "X-Line-Signature": signature,
      },
    });

    expect(response.status()).toBe(200);
  });
});
