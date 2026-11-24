
import os
import time
import json
import logging
from datetime import datetime, timezone
from binance.client import Client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s"
)
logger = logging.getLogger("paper_bot")

SYMBOL = "BTCUSDT"
STARTING_BALANCE = 100.0
TRADE_PERCENT = 0.20
STOP_LOSS = 0.015
TAKE_PROFIT = 0.03
CHECK_INTERVAL = 30
STATE_FILE = "paper_state.json"

# Read-only market data connection.
client = Client("", "")

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {
        "balance": STARTING_BALANCE,
        "btc": 0.0,
        "entry": 0.0,
        "trades": 0
    }

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_price():
    ticker = client.get_symbol_ticker(symbol=SYMBOL)
    return float(ticker["price"])

def run_trading_engine():
    state = load_state()
    logger.info("PAPER TRADING STARTED | Balance: %.2f USDT",
                state["balance"])

    while True:
        try:
            price = get_price()
            logger.info("BTC price: %.2f USDT", price)

            if state["btc"] > 0:
                change = (price - state["entry"]) / state["entry"]

                if change <= -STOP_LOSS or change >= TAKE_PROFIT:
                    proceeds = state["btc"] * price
                    state["balance"] += proceeds
                    logger.info(
                        "SIMULATED SELL | Price %.2f | P/L %.2f USDT",
                        price,
                        proceeds - state["btc"] * state["entry"]
                    )
                    state["btc"] = 0.0
                    state["entry"] = 0.0
                    state["trades"] += 1

            elif state["balance"] >= 10:
                # Simple aggressive momentum signal.
                candles = client.get_klines(
                    symbol=SYMBOL,
                    interval=Client.KLINE_INTERVAL_1MINUTE,
                    limit=3
                )
                previous = float(candles[-2][4])
                current = float(candles[-1][4])

                if current > previous:
                    investment = state["balance"] * TRADE_PERCENT
                    state["btc"] = investment / price
                    state["balance"] -= investment
                    state["entry"] = price
                    logger.info(
                        "SIMULATED BUY | BTC %.8f | Price %.2f",
                        state["btc"], price
                    )

            save_state(state)
            time.sleep(CHECK_INTERVAL)

        except Exception:
            logger.exception("Trading cycle error")
            time.sleep(CHECK_INTERVAL)

