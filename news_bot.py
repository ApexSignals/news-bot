import requests, json, os

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
CRYPTOPANIC_TOKEN = os.environ["CRYPTOPANIC_TOKEN"]
FINNHUB_TOKEN = os.environ["FINNHUB_TOKEN"]

SEEN_FILE = "seen.json"
STOCK_KEYWORDS = ["fed","rate","earnings","sec","merger","acquisition",
                   "ipo","bankruptcy","lawsuit","guidance","downgrade","upgrade"]

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen)[-1000:], f)

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"
        }, timeout=15)
    except Exception as e:
        print("telegram error", e)

def fetch_crypto_news():
    url = f"https://cryptopanic.com/api/v1/posts/?auth_token={CRYPTOPANIC_TOKEN}&filter=important&public=true"
    try:
        return requests.get(url, timeout=15).json().get("results", [])
    except Exception as e:
        print("crypto error", e)
        return []

def fetch_stock_news():
    url = f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_TOKEN}"
    try:
        return requests.get(url, timeout=15).json()
    except Exception as e:
        print("stock error", e)
        return []

def main():
    seen = load_seen()
    new_seen = set(seen)
    for item in fetch_crypto_news():
        uid = f"c{item.get('id')}"
        if uid not in seen:
            send_telegram(f"\U0001FA99 <b>Crypto News</b>\n{item.get('title','')}\n{item.get('url','')}")
            new_seen.add(uid)
    for item in fetch_stock_news():
        uid = f"s{item.get('id')}"
        headline = (item.get("headline") or "").lower()
        if uid not in seen and any(k in headline for k in STOCK_KEYWORDS):
            send_telegram(f"\U0001F4C8 <b>Stock News</b>\n{item.get('headline','')}\n{item.get('url','')}")
            new_seen.add(uid)
    save_seen(new_seen)

if __name__ == "__main__":
    main()
