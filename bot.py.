import urllib.request
import json
import time

SYMBOL = "BTCUSDT"
INTERVAL = "1h"

def get_market_data():
    url = (
        "https://api.binance.com/api/v3/klines"
        f"?symbol={SYMBOL}&interval={INTERVAL}&limit=100"
    )

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "TradingBot"}
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode())

def moving_average(values, period):
    return sum(values[-period:]) / period

def analyze_market():
    candles = get_market_data()

    closes = [float(candle[4]) for candle in candles]

    short_ma = moving_average(closes, 20)
    long_ma = moving_average(closes, 50)
    current_price = closes[-1]

    print("=" * 35)
    print("BINANCE AI TRADING BOT")
    print("=" * 35)
    print(f"Pair: {SYMBOL}")
    print(f"Price: ${current_price:,.2f}")
    print(f"MA20: ${short_ma:,.2f}")
    print(f"MA50: ${long_ma:,.2f}")

    if short_ma > long_ma:
        signal = "BUY SIGNAL"
    elif short_ma < long_ma:
        signal = "SELL SIGNAL"
    else:
        signal = "HOLD"

    print(f"Signal: {signal}")
    print("Mode: SAFE / NO REAL TRADES")
    print("=" * 35)

if __name__ == "__main__":
    while True:
        try:
            analyze_market()
        except Exception as error:
            print("Error:", error)

        time.sleep(60)
