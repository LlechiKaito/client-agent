# client-agent

LINE Secretary Bot - AI-powered conversational assistant.

## Tech Stack

- **Backend**: Python / FastAPI (DDD + Clean Architecture)
- **Frontend**: TypeScript / React / Vite / Tailwind CSS
- **Tests**: pytest / httpx / Playwright

## Quick Start

```bash
docker compose up
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/health

## Development

### Backend

```bash
cd backend
pip install . ".[dev]"
cd src && uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Tests

```bash
# Unit + Integration
pytest tests/unit tests/integration -v

# E2E (requires running servers)
cd tests/e2e
npx playwright test
```

## AWS Deploy

### 前提

- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) インストール済み
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) インストール済み
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

#### 1. ビルド

```bash
sam build
```

#### 2. デプロイ（初回は `--guided`）

```bash
sam deploy --guided
```

対話形式でパラメータを入力:

| パラメータ | 説明 |
|-----------|------|
| Stack Name | CloudFormation スタック名（例: `client-agent`） |
| AppName | アプリ名タグ（例: `client-agent`） |
| AppEnv | 環境名（例: `production`） |
| FrontendUrl | デプロイ後に S3 URL を設定（初回は仮値で OK） |
| LineChannelSecret | LINE チャネルシークレット |
| LineChannelAccessToken | LINE チャネルアクセストークン |
| AnthropicApiKey | Anthropic API キー |
| GasWebappUrl | GAS WebApp URL（LINE ログ） |
| GasMailWebappUrl | GAS WebApp URL（Gmail） |

#### 3. フロントエンドデプロイ

```bash
cd frontend && npm run build
aws s3 sync dist/ s3://<FrontendBucketName> --delete
```

`FrontendBucketName` は `sam deploy` の Outputs に表示される。

#### 4. LINE Webhook URL 設定

Outputs の `WebhookUrl` を [LINE Developers Console](https://developers.line.biz/) の Webhook URL に設定。

#### 5. 更新デプロイ

```bash
sam build && sam deploy
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

tests/
├── unit/             # Unit tests (pytest)
├── integration/      # Integration tests (httpx)
└── e2e/              # E2E tests (Playwright)
```
