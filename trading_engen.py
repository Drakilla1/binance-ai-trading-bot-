

import os
import json
import time
import logging
from decimal import Decimal
from collections import deque
from binance.client import Client

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("BTC_BOT")

SYMBOL = "BTCUSDT"
STARTING_BALANCE = Decimal("100")
TRADE_RISK = Decimal("0.01")
STOP_LOSS = Decimal("0.015")
TAKE_PROFIT = Decimal("0.03")
DAILY_LOSS_LIMIT = Decimal("0.05")
FEE_RATE = Decimal("0.001")
STATE_FILE = "paper_state.json"

balance = STARTING_BALANCE
btc = Decimal("0")
entry_price = None
prices = deque(maxlen=30)
trades = []
daily_start_balance = STARTING_BALANCE

def save_state():
    data = {
        "balance": str(balance),
        "btc": str(btc),
        "entry_price": str(entry_price) if entry_price else None,
        "trades": trades,
        "daily_start_balance": str(daily_start_balance)
    }
    with open(STATE_FILE, "w") as file:
        json.dump(data, file, indent=2)

def load_state():
    global balance, btc, entry_price
    global trades, daily_start_balance

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as file:
            data = json.load(file)

        balance = Decimal(data["balance"])
        btc = Decimal(data["btc"])
        entry_price = (
            Decimal(data["entry_price"])
            if data["entry_price"] else None
        )
        trades = data["trades"]
        daily_start_balance = Decimal(
            data["daily_start_balance"]
        )

def get_price(client):
    result = client.get_symbol_ticker(symbol=SYMBOL)
    return Decimal(result["price"])

def run_trading_engine():
    global balance, btc, entry_price

    load_state()
    client = Client()

    log.info("BTC/USDT PAPER BOT STARTED")
    log.info("Balance: %s USDT", balance)

    while True:
        try:
            price = get_price(client)

            equity = balance + btc * price
            daily_loss = max(
                Decimal("0"),
                daily_start_balance - equity
            )

            if daily_loss >= (
                daily_start_balance * DAILY_LOSS_LIMIT
            ):
                log.warning("DAILY LOSS LIMIT REACHED")
                break

            prices.append(price)

            if len(prices) >= 20:
                short_ma = sum(list(prices)[-5:]) / 5
                long_ma = sum(prices) / len(prices)

                if btc == 0 and short_ma > long_ma:
                    allocation = min(
                        balance * TRADE_RISK,
                        balance
                    )

                    fee = allocation * FEE_RATE
                    btc = (allocation - fee) / price
                    balance -= allocation
                    entry_price = price

                    trades.append({
                        "type": "BUY",
                        "price": str(price),
                        "fee": str(fee),
                        "time": time.time()
                    })

                elif btc > 0:
                    change = (price - entry_price) / entry_price

                    if (
                        change <= -STOP_LOSS
                        or change >= TAKE_PROFIT
                    ):
                        proceeds = btc * price
                        fee = proceeds * FEE_RATE
                        balance += proceeds - fee

                        trades.append({
                            "type": "SELL",
                            "price": str(price),
                            "fee": str(fee),
                            "time": time.time()
                        })

                        btc = Decimal("0")
                        entry_price = None

            save_state()

            log.info(
                "Price=%s | Equity=%s | Balance=%s",
                price, equity, balance
            )

            time.sleep(60)

        except Exception:
            log.exception("Paper trading error")
            time.sleep(60)

if __name__ == "__main__":
    run_trading_engine()


