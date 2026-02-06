import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# اختیاری: اگر خواستی لاگ‌ها به یک چت ادمین ارسال شود
ADMIN_LOG_CHAT_ID = os.getenv("ADMIN_LOG_CHAT_ID", "").strip()  # مثل: -1001234567890

# تنظیمات ضدفلود
FLOOD_WINDOW_SEC = int(os.getenv("FLOOD_WINDOW_SEC", "7"))
FLOOD_MAX_MSG = int(os.getenv("FLOOD_MAX_MSG", "6"))
FLOOD_MUTE_SEC = int(os.getenv("FLOOD_MUTE_SEC", "120"))

# ضدلینک
BLOCK_LINKS = os.getenv("BLOCK_LINKS", "1").strip() == "1"

# ضداسپم ساده
BLOCK_FORWARD_FROM_CHANNELS = os.getenv("BLOCK_FORWARD_FROM_CHANNELS", "1").strip() == "1"

# کپچا/تایید ورود
ENABLE_JOIN_VERIFY = os.getenv("ENABLE_JOIN_VERIFY", "1").strip() == "1"
VERIFY_TIMEOUT_SEC = int(os.getenv("VERIFY_TIMEOUT_SEC", "120"))
