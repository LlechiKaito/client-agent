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

Lambda → SSM Parameter Store (SecureString) で機密情報を取得
```

## デプロイ手順

### 1. CDK セットアップ

```bash
cd infra
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 初回のみ: CDK Bootstrap

```bash
cdk bootstrap
```

### 3. SSM Parameter Store に機密情報を登録

機密情報は CDK に渡さず、SSM Parameter Store で管理する。
初回のみ実行。更新時は `--overwrite` フラグを付ける。

```bash
aws ssm put-parameter --name "/client-agent/LINE_CHANNEL_SECRET" --value "your-secret" --type SecureString
aws ssm put-parameter --name "/client-agent/LINE_CHANNEL_ACCESS_TOKEN" --value "your-token" --type SecureString
aws ssm put-parameter --name "/client-agent/ANTHROPIC_API_KEY" --value "your-key" --type SecureString
aws ssm put-parameter --name "/client-agent/GAS_WEBAPP_URL" --value "your-url" --type SecureString
aws ssm put-parameter --name "/client-agent/GAS_MAIL_WEBAPP_URL" --value "your-url" --type SecureString
```

| SSM パラメータ名 | 説明 |
|-----------------|------|
| `/client-agent/LINE_CHANNEL_SECRET` | LINE チャネルシークレット |
| `/client-agent/LINE_CHANNEL_ACCESS_TOKEN` | LINE チャネルアクセストークン |
| `/client-agent/ANTHROPIC_API_KEY` | Anthropic API キー |
| `/client-agent/GAS_WEBAPP_URL` | GAS WebApp URL (LINE ログ) |
| `/client-agent/GAS_MAIL_WEBAPP_URL` | GAS WebApp URL (Gmail) |

### 4. デプロイ

```bash
cdk deploy
```

コンテキストでアプリ名・環境名を指定可能:

```bash
cdk deploy -c app_name=client-agent -c app_env=production
```

CDK は Lambda に `SSM_PREFIX=/client-agent/` のみ環境変数として渡す。
機密情報は Lambda 起動時に SSM から取得される。

### 5. LINE Webhook URL 設定

Outputs の `WebhookUrl` を LINE Developers Console の Webhook URL に設定する。

### 6. 更新デプロイ

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
| SSM Parameter Store | $0 (Standard パラメータは無料) |
| **合計** | **~$0/月** |

## ローカル開発

Lambda 対応後もローカル開発は従来通り `.env` から読み込み:

```bash
docker compose up -d
```
