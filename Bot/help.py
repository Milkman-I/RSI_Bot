import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update
from telegram.ext import CommandHandler, ApplicationBuilder, ContextTypes, CallbackQueryHandler
from config.Const import BOT_API, CHAT_ID


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=update.effective_chat.id)

if __name__ == "__main__":
    print("Starting Help Bot")
    application = ApplicationBuilder().token(BOT_API).build()
    application.add_handler(CommandHandler("help", help_command))
    application.run_polling()