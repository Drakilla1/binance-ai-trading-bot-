
import os
import logging
from decimal import Decimal

from binance.client import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("paper_trading")

API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_API_SECRET", "")

client = Client(API_KEY, API_SECRET)

# PAPER TRADING ONLY
INITIAL_BALANCE = Decimal("100")
QUOTE_BALANCE = INITIAL_BALANCE
BTC_BALANCE = Decimal("0")

SYMBOL = "BTCUSDT"
INTERVAL = Client.KLINE_INTERVAL_5MINUTE

RISK_PER_TRADE = Decimal("0.01")
DAILY_LOSS_LIMIT = Decimal("0.03")

STOP_LOSS = Decimal("0.01")
TAKE_PROFIT = Decimal("0.02")

def get_market_price():
    ticker = client.get_symbol_ticker(symbol=SYMBOL)
    return Decimal(ticker["price"])

def get_signal():
    candles = client.get_klines(
        symbol=SYMBOL,
        interval=INTERVAL,
        limit=30
    )

    closes = [Decimal(c[4]) for c in candles[:-1]]

    if len(closes) < 22:
        return "HOLD"

    ema9 = sum(closes[-9:]) / Decimal("9")
    ema21 = sum(closes[-21:]) / Decimal("21")

    if ema9 > ema21:
        return "BUY"
    elif ema9 < ema21:
        return "SELL"

    return "HOLD"

def run_paper_trading():
    global QUOTE_BALANCE, BTC_BALANCE

    entry_price = None

    logger.info("Starting BTC/USDT paper trading")
    logger.info("Virtual balance: %s USDT", QUOTE_BALANCE)

    price = get_market_price()
    signal = get_signal()

    if signal == "BUY" and BTC_BALANCE == 0:
        risk_amount = QUOTE_BALANCE * RISK_PER_TRADE
        position_value = min(
            QUOTE_BALANCE,
            risk_amount / STOP_LOSS
        )

        if position_value > 0:
            BTC_BALANCE = position_value / price
            QUOTE_BALANCE -= position_value
            entry_price = price

            logger.info("SIMULATED BUY at %s", price)

    elif signal == "SELL" and BTC_BALANCE > 0:
        QUOTE_BALANCE += BTC_BALANCE * price
        BTC_BALANCE = Decimal("0")
        entry_price = None

        logger.info("SIMULATED SELL at %s", price)

    logger.info("Price: %s", price)
    logger.info("USDT balance: %s", QUOTE_BALANCE)
    logger.info("BTC balance: %s", BTC_BALANCE)

if __name__ == "__main__":
    run_paper_trading()

