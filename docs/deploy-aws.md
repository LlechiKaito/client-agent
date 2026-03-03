# AWS Lambda デプロイ手順

## 前提

- AWS CLI がインストール済み
- AWS CDK CLI がインストール済み（`npm install -g aws-cdk`）
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

### 1. CDK セットアップ

```bash
cd infra
pip install -r requirements.txt
```

### 2. 初回のみ: CDK Bootstrap

```bash
cdk bootstrap
```

### 3. デプロイ

```bash
cdk deploy
```

コンテキストでアプリ名・環境名を指定可能:

```bash
cdk deploy -c app_name=client-agent -c app_env=production
```

### 4. Lambda 環境変数を設定

デプロイ後、AWS コンソールまたは CLI で Lambda に環境変数を設定:

| 環境変数 | 説明 | 例 |
|---------|------|---|
| `FRONTEND_URL` | フロントエンド URL | (デプロイ後の S3 URL) |
| `LINE_CHANNEL_SECRET` | LINE チャネルシークレット | |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE チャネルアクセストークン | |
| `ANTHROPIC_API_KEY` | Anthropic API キー | |
| `GAS_WEBAPP_URL` | GAS WebApp URL (LINE ログ) | |
| `GAS_MAIL_WEBAPP_URL` | GAS WebApp URL (Gmail) | |

### 5. フロントエンドデプロイ

```bash
cd frontend
npm run build
aws s3 sync dist/ s3://<FrontendBucketName> --delete
```

### 6. LINE Webhook URL 設定

Outputs の `WebhookUrl` を LINE Developers Console の Webhook URL に設定する。

### 7. 更新デプロイ

```bash
cd infra && cdk deploy
```

### 差分確認（デプロイ前）

```bash
cd infra && cdk diff
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
