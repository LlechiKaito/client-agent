ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"

ANTHROPIC_MAX_TOKENS = 1024

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
