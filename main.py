from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
from datetime import datetime
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stocks we monitor
WATCHLIST = [
    "ZOMATO", "PAYTM", "NYKAA", "DELHIVERY", "CARTRADE",
    "POLICYBZR", "STAR HEALTH", "NAZARA", "EASEMYTRIP", "IXIGO"
]

def get_stock_data(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}.NS"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=5)
        data = r.json()
        price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
        prev  = data["chart"]["result"][0]["meta"]["previousClose"]
        vol   = data["chart"]["result"][0]["meta"]["regularMarketVolume"]
        avg_vol = data["chart"]["result"][0]["meta"].get("averageDailyVolume10Day", vol)
        change_pct = round(((price - prev) / prev) * 100, 2)
        vol_spike  = round((vol / avg_vol) * 100) if avg_vol else 100
        risk = 0
        if abs(change_pct) > 10: risk += 40
        elif abs(change_pct) > 5: risk += 20
        if vol_spike > 300: risk += 40
        elif vol_spike > 150: risk += 20
        if change_pct > 15: risk += 20
        risk = min(risk, 99)
        return {
            "symbol": symbol,
            "price": round(price, 2),
            "change_pct": change_pct,
            "volume_spike": vol_spike,
            "risk_score": risk,
            "flagged": risk > 40,
            "timestamp": datetime.now().strftime("%H:%M IST")
        }
    except:
        return None

@app.get("/")
def root():
    return {"status": "ScamShield India API Running"}

@app.get("/api/flagged")
def get_flagged():
    results = []
    for symbol in WATCHLIST:
        data = get_stock_data(symbol)
        if data and data["flagged"]:
            results.append(data)
    results.sort(key=lambda x: x["risk_score"], reverse=True)
    return {"flagged": results, "total": len(results), "scanned": len(WATCHLIST)}

@app.get("/api/stats")
def get_stats():
    return {
        "flagged_today": random.randint(18, 28),
        "complaints": 847,
        "operators_identified": 142,
        "victim_loss_cr": 2.3
    }
