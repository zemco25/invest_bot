
from fastapi import FastAPI, Request
import requests
import yfinance as yf
import os

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "secret-path")

portfolio = {}
balance = 100.0

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.post(f"/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    global balance

    if text == "/start":
        send_message(chat_id, "👋 Привет! Я твой ИИ-ассистент по инвестициям. Напиши /recommend, чтобы получить советы.")
    elif text == "/recommend":
        send_message(chat_id, "📈 Рекомендую рассмотреть: PLTR, SOFI, F — хорошие недорогие акции с потенциалом роста.")
    elif text.startswith("/analyze "):
        ticker = text.split(" ", 1)[1].strip().upper()
        stock = yf.Ticker(ticker)
        info = stock.info
        price = info.get("currentPrice", "N/A")
        pe = info.get("trailingPE", "N/A")
        send_message(chat_id, f"📊 {ticker}:\nЦена: {price}\nP/E: {pe}")
    elif text.startswith("/add "):
        try:
            _, ticker, amount = text.split()
            amount = float(amount)
            ticker = ticker.upper()
            if amount > balance:
                send_message(chat_id, f"❌ Недостаточно средств. Баланс: ${balance:.2f}")
            else:
                portfolio[ticker] = portfolio.get(ticker, 0) + amount
                balance -= amount
                send_message(chat_id, f"✅ Добавлено: {ticker} на ${amount:.2f}")
        except:
            send_message(chat_id, "⚠️ Формат: /add TICKER СУММА")
    elif text == "/portfolio":
        if not portfolio:
            send_message(chat_id, f"💼 Портфель пуст. Баланс: ${balance:.2f}")
        else:
            summary = "\n".join([f"{k}: ${v:.2f}" for k, v in portfolio.items()])
            send_message(chat_id, f"💼 Портфель:\n{summary}\nОстаток: ${balance:.2f}")
    else:
        send_message(chat_id, "🤖 Неизвестная команда. Используй /start, /recommend, /add, /portfolio, /analyze")
    return {"ok": True}
