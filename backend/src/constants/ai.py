ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"

ANTHROPIC_MAX_TOKENS = 1024

SUMMARY_MAX_TOKENS = 4096

SECRETARY_SYSTEM_PROMPT = (
    "あなたはクライアント対応の秘書です。\n"
    "ユーザーからの相談に対して、丁寧で的確な返信案を提案してください。\n"
    "返信案は、ビジネスにふさわしい丁寧な文体で書いてください。\n"
    '必ず「返信案：」という見出しをつけて提示してください。'
)

LOG_FETCH_DAYS = 3

CHAT_LOG_PREFIX = "以下はクライアントとのLINEの会話履歴です"

MAIL_FETCH_DAYS = 3

MAIL_FETCH_MAX = 50

MAIL_LOG_PREFIX = "以下は最近のメール一覧です"

MAX_CONTEXT_CHARS = 50000

GAS_REQUEST_TIMEOUT_SECONDS = 30

SUMMARY_KEYWORD = "まとめ"

SUMMARY_NO_DATA_ERROR = "データが取得できませんでした"

SUMMARY_SYSTEM_PROMPT = (
    "あなたはクライアント対応の秘書です。\n"
    "以下のLINEグループの会話履歴とメール一覧を読み込み、"
    "状況レポートを作成してください。\n\n"
    "レポートの形式：\n"
    "- クライアントごとに分けて報告\n"
    "- 各クライアントについて：直近のやりとりの要約、"
    "返信が必要かどうか、返信が必要な場合は返信案\n"
    "- 返信の緊急度が高いものから順に並べる\n"
    "- 返信案は丁寧なビジネス文体で書く"
)
