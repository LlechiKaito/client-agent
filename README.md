# client-agent

LINE Secretary Bot - AI-powered conversational assistant.

## Tech Stack

- **Backend**: Python / FastAPI (DDD + Clean Architecture)
- **Frontend**: TypeScript / React / Vite / Tailwind CSS
- **Tests**: pytest / httpx / Playwright

## Setup

### 1. LINE Developers Console で Messaging API チャネルを作成

1. [LINE Developers Console](https://developers.line.biz/) にログイン
2. プロバイダーを作成（または既存を選択）
3. **Messaging API** チャネルを新規作成
4. 「チャネル基本設定」から **チャネルシークレット** をコピー
5. 「Messaging API設定」から **チャネルアクセストークン** を発行してコピー

### 2. 環境変数を設定

`.env.example` をコピーして `.env` を作成し、値を設定する。

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

**backend/.env**

```env
# App
APP_HOST=0.0.0.0
APP_PORT=8000
APP_ENV=development
FRONTEND_URL=http://localhost:5173

# LINE（LINE Developers Console から取得）
LINE_CHANNEL_SECRET=your-channel-secret
LINE_CHANNEL_ACCESS_TOKEN=your-channel-access-token

# Anthropic
ANTHROPIC_API_KEY=your-anthropic-api-key
```

| 変数 | 説明 | 取得元 |
|------|------|--------|
| `APP_HOST` | サーバーバインドアドレス | 固定値 `0.0.0.0` |
| `APP_PORT` | サーバーポート | 固定値 `8000` |
| `APP_ENV` | 環境名 | `development` / `production` |
| `FRONTEND_URL` | フロントエンド URL（CORS 許可対象） | ローカルなら `http://localhost:5173` |
| `LINE_CHANNEL_SECRET` | LINE チャネルシークレット | LINE Developers Console > チャネル基本設定 |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE チャネルアクセストークン（長期） | LINE Developers Console > Messaging API設定 |
| `ANTHROPIC_API_KEY` | Anthropic API キー | [Anthropic Console](https://console.anthropic.com/) > API Keys |

**frontend/.env**

```env
# App
VITE_API_URL=/api
VITE_PROXY_TARGET=http://localhost:8000
```

| 変数 | 説明 |
|------|------|
| `VITE_API_URL` | API のベースパス |
| `VITE_PROXY_TARGET` | 開発時のプロキシ先バックエンド URL |

### 3. Webhook URL を設定

LINE Bot がメッセージを受け取るには、LINE Platform からアクセス可能な HTTPS URL が必要。

**ローカル開発では ngrok を使う:**

```bash
ngrok http 8000
```

表示された HTTPS URL（例: `https://xxxx.ngrok-free.app`）を LINE Developers Console に設定:

1. LINE Developers Console > Messaging API設定
2. **Webhook URL** に `https://xxxx.ngrok-free.app/callback` を入力
3. **Webhook の利用** を ON にする
4. **検証** ボタンで疎通を確認

## Quick Start

### Docker で起動

```bash
docker compose up
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/health
- Webhook: POST http://localhost:8000/callback

### ローカルで起動

**Backend:**

```bash
cd backend
pip install . ".[dev]"
cd src && uvicorn main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

## Usage

1. 上記セットアップ完了後、LINE アプリで Bot を友だち追加（QR コードは LINE Developers Console の Messaging API設定にある）
2. Bot にテキストメッセージを送信
3. Claude（秘書 AI）が生成した返信案が LINE に返される

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | ヘルスチェック |
| POST | `/callback` | LINE Webhook エンドポイント |

## Tests

```bash
# Unit tests
cd backend && python -m pytest ../tests/unit/ -v

# Integration tests
cd backend && python -m pytest ../tests/integration/ -v

# E2E tests (requires running servers)
cd tests/e2e && npx playwright test

# E2E webhook tests (separate config)
cd tests/e2e && npx playwright test --config=playwright.webhook.config.ts
```

## AWS Deploy

### 前提

- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) インストール済み
- [AWS CDK CLI](https://docs.aws.amazon.com/cdk/v2/guide/getting-started.html) インストール済み（`npm install -g aws-cdk`）
- `aws configure` で認証設定済み

### アーキテクチャ

```
LINE → Lambda Function URL (HTTPS) → FastAPI (Mangum)
                                        ├─ LINE API (reply/push)
                                        ├─ Claude API (Anthropic)
                                        └─ GAS WebApp (LINE logs/Gmail)

Frontend → S3 Static Website Hosting
```

全リソースに `App` / `Env` タグが付与されるため、AWS Cost Explorer でアプリ単位のコスト確認が可能。

### 手順

#### 1. CDK セットアップ

```bash
cd infra
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 2. 初回のみ: CDK Bootstrap

```bash
cdk bootstrap
```

#### 3. 設定ファイルを作成

```bash
cp cdk.context.example.json cdk.context.json
```

`cdk.context.json` を編集して値を設定:

| キー | 説明 |
|-----|------|
| `frontend_url` | S3 Website URL（初回は `cdk deploy` 後に Outputs から取得して再デプロイ） |
| `line_channel_secret` | LINE チャネルシークレット |
| `line_channel_access_token` | LINE チャネルアクセストークン |
| `anthropic_api_key` | Anthropic API キー |
| `gas_webapp_url` | GAS WebApp URL（LINE ログ） |
| `gas_mail_webapp_url` | GAS WebApp URL（Gmail） |

#### 4. フロントエンドをビルド

```bash
cd frontend && npm install && npm run build && cd ../infra
```

#### 5. デプロイ

```bash
cdk deploy
```

バックエンド（Lambda）+ フロントエンド（S3）が一括でデプロイされる。

#### 6. LINE Webhook URL 設定

Outputs の `WebhookUrl` を [LINE Developers Console](https://developers.line.biz/) の Webhook URL に設定。

#### 7. 更新デプロイ

```bash
cd infra && cdk deploy
```

### コスト確認

AWS Cost Explorer → **タグ `App: client-agent`** でフィルタすると、このアプリのコストだけ確認できる。

> Cost Explorer でタグを使うには、[Billing] → [Cost allocation tags] で `App` と `Env` を有効化する必要がある。

### コスト目安

| リソース | 月額 |
|---------|------|
| Lambda | $0（Free Tier: 100万リクエスト/月） |
| S3 | ~$0.01 |
| **合計** | **≒ $0/月** |

## Project Structure

```
backend/src/
├── domain/           # Business core (entities, value objects, repositories)
├── application/      # Use cases, DTOs, services
├── infrastructure/   # External implementations (DB, APIs)
├── presentation/     # Controllers, routes, middleware
├── container/        # DI composition root
├── config/           # Environment config
├── constants/        # Magic numbers, HTTP status codes
└── utils/            # Pure utility functions

frontend/src/
├── pages/            # Page components (routing targets)
├── components/       # Reusable UI components
├── services/         # API clients (axios)
├── hooks/            # Logic extraction (React hooks)
├── types/            # Type definitions
├── constants/        # Constants, error messages, API paths
└── utils/            # Utility functions

infra/
├── app.py            # CDK app entry point
└── stacks/           # CDK stack definitions

tests/
├── unit/             # Unit tests (pytest)
├── integration/      # Integration tests (httpx)
└── e2e/              # E2E tests (Playwright)
```
