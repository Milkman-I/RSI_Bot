# File: Bot/main.py

#root_path 
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from RSI.logic import *
from config.Const import BOT_API, CHAT_ID
from telegram import Update
from telegram.ext import CommandHandler, ApplicationBuilder, ContextTypes, CallbackQueryHandler
import asyncio
import concurrent.futures

workers = 7
scan_delay = 5
Api = BOT_API


async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global workers
    await update.message.reply_text(f"Current settings:\nWorkers: {workers}, Scan Delay: {scan_delay} seconds")

async def scan_coins_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    coins = fetch_coins()
    if not coins:
        print("No coins found.")
        return
    print(f"Found {len(coins)} coins.")

    for coin in coins:
        if Check_Coin(f"{coin}/USDT"):
            price = coin_pirce(f"{coin}/USDT")
            if price:
                message = f"Coin: {coin}\nPrice: {price}"
                print(f"Sent message for {coin}: {message}")
                await context.bot.send_message(chat_id=CHAT_ID, text=message)
            else:
                print(f"Failed to fetch price for {coin}")
        else:
            print(f"Coin {coin} does not meet RSI criteria.")

    print("Finished processing coins.")
    context.job_queue.run_once(scan_coins_job, when=scan_delay)


if __name__ == "__main__":
    print("Starting RSI Bot")
    application = ApplicationBuilder().token(Api).build()
    application.add_handler(CommandHandler("show_settings", show_settings))
    job_queue = application.job_queue
    job_queue.run_once(scan_coins_job, when=scan_delay)
    application.run_polling()