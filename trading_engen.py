

import time
import logging
from decimal import Decimal
from collections import deque
from binance.client import Client

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("BTC_BOT")

STARTING_BALANCE = Decimal("100")
SYMBOL = "BTCUSDT"
STOP_LOSS = Decimal("0.015")
TAKE_PROFIT = Decimal("0.03")
TRADE_RISK = Decimal("0.01")

balance = STARTING_BALANCE
btc = Decimal("0")
entry_price = None
prices = deque(maxlen=30)

def get_price(client):
    data = client.get_symbol_ticker(symbol=SYMBOL)
    return Decimal(data["price"])

def run_trading_engine():
    global balance, btc, entry_price

    client = Client()
    log.info("BTC/USDT PAPER BOT STARTED")
    log.info("Simulated balance: %s USDT", balance)

    while True:
        try:
            price = get_price(client)
            prices.append(price)

            if len(prices) < 20:
                log.info("Collecting price history: %s", price)
                time.sleep(60)
                continue

            short_ma = sum(list(prices)[-5:]) / 5
            long_ma = sum(prices) / len(prices)

            if btc == 0 and short_ma > long_ma:
                allocation = balance * TRADE_RISK
                btc = allocation / price
                balance -= allocation
                entry_price = price
                log.info("PAPER BUY at %s", price)

            elif btc > 0:
                change = (price - entry_price) / entry_price

                if change <= -STOP_LOSS or change >= TAKE_PROFIT:
                    balance += btc * price
                    log.info("PAPER SELL at %s", price)
                    log.info("Balance: %s USDT", balance)
                    btc = Decimal("0")
                    entry_price = None

            log.info(
                "Price=%s | Balance=%s | BTC=%s",
                price, balance, btc
            )

            time.sleep(60)

        except Exception:
            log.exception("Trading error")
            time.sleep(60)

if __name__ == "__main__":
    run_trading_engine()


