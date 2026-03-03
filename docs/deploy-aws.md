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

機密情報は CDK に渡さず、SSM Parameter Store（SecureString）で管理する。

```bash
# テンプレートから作成し、値を編集
cp infra/ssm-parameters.example.json infra/ssm-parameters.json
# 値を実際のシークレットに書き換える

# 一括登録（jq + AWS CLI が必要）
bash infra/scripts/put-ssm-parameters.sh
```

| SSM パラメータ名 | 説明 | 取得元 |
|-----------------|------|--------|
| `/client-agent/LINE_CHANNEL_SECRET` | LINE チャネルシークレット | LINE Developers Console > チャネル基本設定 |
| `/client-agent/LINE_CHANNEL_ACCESS_TOKEN` | LINE チャネルアクセストークン | LINE Developers Console > Messaging API設定 |
| `/client-agent/ANTHROPIC_API_KEY` | Anthropic API キー | [Anthropic Console](https://console.anthropic.com/) > API Keys |
| `/client-agent/GAS_WEBAPP_URL` | GAS WebApp URL（LINE ログ） | GAS デプロイ URL |
| `/client-agent/GAS_MAIL_WEBAPP_URL` | GAS WebApp URL（Gmail） | GAS デプロイ URL |

> `infra/ssm-parameters.json` は `.gitignore` に含まれるため、シークレットがリポジトリにコミットされることはない。
> スクリプトは `--overwrite` 付きなので、初回も更新時もそのまま実行できる。

CDK は Lambda に `SSM_PREFIX=/client-agent/` のみ環境変数として渡す。
機密情報は Lambda 起動時に SSM から取得される。

### 4. デプロイ

```bash
cd infra && cdk deploy
```

Outputs に `WebhookUrl` が表示される。コンテキストでアプリ名・環境名を指定可能:

```bash
cdk deploy -c app_name=client-agent -c app_env=production
```

### 5. LINE Webhook URL 設定

1. [LINE Developers Console](https://developers.line.biz/) > Messaging API設定
2. **Webhook URL** に `{WebhookUrl}callback` を入力
3. **Webhook の利用** を ON にする
4. **検証** ボタンで疎通を確認

### 6. 更新デプロイ

```bash
# 差分確認
cd infra && cdk diff

# デプロイ
cd infra && cdk deploy
```

> SSM パラメータの値を更新する場合は、`infra/ssm-parameters.json` を編集してスクリプトを再実行する。Lambda の再デプロイは不要。

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
