import requests, json, os, feedparser, time

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
FINNHUB_TOKEN = os.environ["FINNHUB_TOKEN"]

SEEN_FILE = "seen.json"

STOCK_KEYWORDS = ["fed","rate","earnings","sec","merger","acquisition",
                   "ipo","bankruptcy","lawsuit","guidance","downgrade","upgrade"]

CRYPTO_KEYWORDS = ["hack","exploit","sec","etf","regulation","ban","crash",
                    "surge","approval","lawsuit","bankrupt","liquidation","fed"]

CRYPTO_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
]

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
        r = requests.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"
        }, timeout=15)
        if r.status_code != 200:
            print("telegram send failed:", r.status_code, r.text[:300])
    except Exception as e:
        print("telegram error", e)

def fetch_crypto_news():
    items = []
    for feed_url in CRYPTO_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:20]:
                items.append(entry)
        except Exception as e:
            print("crypto feed error", feed_url, e)
    return items

def fetch_stock_news():
    url = f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_TOKEN}"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            print("stock http error:", r.status_code, r.text[:300])
            return []
        data = r.json()
        if not isinstance(data, list):
            print("stock unexpected response:", str(data)[:300])
            return []
        return data
    except Exception as e:
        print("stock error", e)
        return []

def main():
    seen = load_seen()
    new_seen = set(seen)

    for entry in fetch_crypto_news():
        link = entry.get("link", "")
        title = entry.get("title", "")
        uid = f"c{link}"
        headline_lower = title.lower()
        if uid not in seen and any(k in headline_lower for k in CRYPTO_KEYWORDS):
            send_telegram(f"\U0001FA99 <b>Crypto News</b>\n{title}\n{link}")
            new_seen.add(uid)

    for item in fetch_stock_news():
        if not isinstance(item, dict):
            continue
        uid = f"s{item.get('id')}"
        headline = (item.get("headline") or "").lower()
        if uid not in seen and any(k in headline for k in STOCK_KEYWORDS):
            send_telegram(f"\U0001F4C8 <b>Stock News</b>\n{item.get('headline','')}\n{item.get('url','')}")
            new_seen.add(uid)

    save_seen(new_seen)

if __name__ == "__main__":
    main()
