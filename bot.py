import os
os.system("pip install pytz")
import logging
import os
import pytz
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackContext,
)
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

# ======================
# 基本設定
# ======================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")  # Render 環境變數中設定 BOT_TOKEN
SHEET_NAME = "Telegram 回報系統 (每週報告版)"

# ======================
# Google Sheets 連線
# ======================
SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPES)
client = gspread.authorize(creds)

try:
    sheet = client.open(SHEET_NAME).worksheet("回報紀錄")
    logger.info(f"✅ 已找到試算表: {SHEET_NAME}")
except gspread.exceptions.WorksheetNotFound:
    logger.info("📄 未找到工作表，建立中...")
    spreadsheet = client.open(SHEET_NAME)
    sheet = spreadsheet.add_worksheet(title="回報紀錄", rows="1000", cols="20")
    sheet.append_row(["時間", "用戶", "回報內容"])
    logger.info("✅ 已建立新的工作表。")

# ======================
# Telegram Bot 功能
# ======================
ASK_FEEDBACK = range(1)

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("👋 請輸入您要回報的內容：")
    return ASK_FEEDBACK

async def get_feedback(update: Update, context: CallbackContext):
    feedback = update.message.text
    user = update.message.from_user
    timestamp = datetime.now(pytz.timezone("Asia/Taipei")).strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([timestamp, user.username, feedback])
    await update.message.reply_text("✅ 已收到您的回報，感謝！")
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("❌ 已取消回報。")
    return ConversationHandler.END

# ======================
# 定時任務：每週報告
# ======================
def send_weekly_report():
    logger.info("🕒 產生每週報告中...")
    # 這裡可以加入自動彙整報告的邏輯
    # 例如抓本週的回報數、寄出摘要等
    logger.info("✅ 每週報告執行完成")

# ======================
# Flask 伺服器（保持 Render 醒著）
# ======================
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Telegram Feedback Bot is running on Render!"

# ======================
# 主程序入口
# ======================
if __name__ == "__main__":
    scheduler = BackgroundScheduler(timezone="Asia/Taipei")
    scheduler.add_job(send_weekly_report, "cron", day_of_week="mon", hour=9, minute=0)
    scheduler.start()

    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={ASK_FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_feedback)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)

    logger.info("🤖 Bot running... weekly report every Monday 09:00 (Asia/Taipei)")

    # 同時執行 Flask（for Render）與 Telegram Bot
    import threading

    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))).start()
    application.run_polling()

