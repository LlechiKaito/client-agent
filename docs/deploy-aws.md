# AWS Lambda デプロイ手順

## 前提

- AWS CLI + SAM CLI がインストール済み
- AWS アカウントの認証情報が設定済み

## アーキテクチャ

```
LINE Webhook → Lambda Function URL → FastAPI (Mangum)
                                       ├─ reply("考え中...")
                                       ├─ Claude API
                                       ├─ GAS WebApp
                                       └─ LINE push(結果)

Frontend → S3 Static Website Hosting
```

## デプロイ手順

### 1. ビルド

```bash
sam build
```

### 2. デプロイ（初回）

```bash
sam deploy --guided
```

パラメータの入力を求められます:

| パラメータ | 説明 | 例 |
|-----------|------|---|
| AppEnv | 環境名 | production |
| FrontendUrl | フロントエンドURL | (デプロイ後のS3 URL) |
| LineChannelSecret | LINE チャネルシークレット | |
| LineChannelAccessToken | LINE チャネルアクセストークン | |
| AnthropicApiKey | Anthropic API キー | |
| GasWebappUrl | GAS WebApp URL (LINE ログ) | |
| GasMailWebappUrl | GAS WebApp URL (Gmail) | |

### 3. フロントエンドデプロイ

```bash
cd frontend
npm run build
aws s3 sync dist/ s3://<FrontendBucketName> --delete
```

### 4. LINE Webhook URL 設定

Outputs の `WebhookUrl` を LINE Developers Console の Webhook URL に設定する。

### 5. 更新デプロイ

```bash
sam build && sam deploy
```

## コスト目安

| リソース | 月額 |
|---------|------|
| Lambda | $0 (Free Tier: 100万リクエスト/月) |
| S3 | ~$0.01 |
| **合計** | **~$0/月** |

## ローカル開発

Lambda 対応後もローカル開発は従来通り:

```bash
docker compose up -d
```

SAM でローカルテストも可能:

```bash
sam local start-api
```
