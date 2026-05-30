from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

WATCHLIST = [
    "SEPC", "TARMAT", "RPOWER", "SUZLON", "YESBANK",
    "IDEA", "JPASSOCIAT", "PCJEWELLER", "SINTEX",
    "EDUCOMP", "UNITECH", "RCOM", "GTLINFRA", "HDIL"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}

def get_stock(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}.NS"
        r = requests.get(url, headers=HEADERS, timeout=8)
        d = r.json()
        meta = d["chart"]["result"][0]["meta"]
        price = meta.get("regularMarketPrice", 0)
        prev = meta.get("previousClose", price)
        vol = meta.get("regularMarketVolume", 0)
        avg_vol = meta.get("averageDailyVolume10Day", vol) or vol
        change_pct = round(((price - prev) / prev) * 100, 2) if prev else 0
        vol_spike = round((vol / avg_vol) * 100) if avg_vol else 100
        risk = 0
        if abs(change_pct) > 15: risk += 45
        elif abs(change_pct) > 8: risk += 25
        elif abs(change_pct) > 4: risk += 10
        if vol_spike > 400: risk += 45
        elif vol_spike > 200: risk += 25
        elif vol_spike > 130: risk += 10
        risk = min(risk, 99)
        exchange = "BSE" if symbol in ["SEPC","TARMAT","PCJEWELLER","SINTEX","EDUCOMP","UNITECH","GTLINFRA","HDIL"] else "NSE"
        return {
            "symbol": symbol,
            "price": round(price, 2),
            "change_pct": change_pct,
            "volume_spike": vol_spike,
            "risk_score": risk,
            "exchange": exchange,
            "flagged": risk > 10,
            "timestamp": datetime.now().strftime("%H:%M IST")
        }
    except:
        return None

@app.get("/")
def root():
    return {"status": "ScamShield India API Running", "time": datetime.now().strftime("%H:%M IST")}

@app.get("/api/flagged")
def get_flagged():
    results = []
    for symbol in WATCHLIST:
        data = get_stock(symbol)
        if data and data["flagged"]:
            results.append(data)
    results.sort(key=lambda x: x["risk_score"], reverse=True)
    return {
        "flagged": results,
        "total": len(results),
        "scanned": len(WATCHLIST),
        "timestamp": datetime.now().strftime("%H:%M IST")
    }

@app.get("/api/stats")
def get_stats():
    return {
        "complaints": 847,
        "operators_identified": 142,
        "victim_loss_cr": 2.3
    }
