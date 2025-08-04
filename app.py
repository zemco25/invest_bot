
from fastapi import FastAPI, Request
import requests
import yfinance as yf
import os
import asyncio

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # Telegram chat_id пользователя

portfolio = {
    "AAPL": {"amount": 50.0, "buy_price": 180.0},
    "TSLA": {"amount": 30.0, "buy_price": 250.0}
}

async def price_watcher():
    await asyncio.sleep(10)
    while True:
        for ticker, data in portfolio.items():
            stock = yf.Ticker(ticker)
            info = stock.info
            current = info.get("currentPrice")
            if not current:
                continue
            buy_price = data["buy_price"]
            change_pct = ((current - buy_price) / buy_price) * 100

            if change_pct >= 10:
                send_message(CHAT_ID, f"📈 {ticker} вырос на {change_pct:.2f}% — можно продать")
            elif change_pct <= -8:
                send_message(CHAT_ID, f"📉 {ticker} упал на {abs(change_pct):.2f}% — возможно стоит продать")
        await asyncio.sleep(3600)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(price_watcher())

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    print(f"chat_id: {chat_id}")
    
    if text == "/start":
        send_message(chat_id, "👋 Бот активен. Я буду присылать уведомления, когда акции изменяются на ±10%")
 return {"ok": True}
