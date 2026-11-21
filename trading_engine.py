
import os
import time
import logging
from binance.client import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trading_engine")

API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_API_SECRET", "")

client = Client(API_KEY, API_SECRET)

SYMBOL = "BTCUSDT"
INTERVAL = Client.KLINE_INTERVAL_1HOUR
TRADE_AMOUNT_USDT = 20
DRY_RUN = True  # Safe mode: no real orders


def get_market_data():
    candles = client.get_klines(
        symbol=SYMBOL,
        interval=INTERVAL,
        limit=100
    )
    closes = [float(candle[4]) for candle in candles]
    return closes


def calculate_signal(closes):
    if len(closes) < 50:
        return "HOLD"

    sma_20 = sum(closes[-20:]) / 20
    sma_50 = sum(closes[-50:]) / 50

    if sma_20 > sma_50:
        return "BUY"
    elif sma_20 < sma_50:
        return "SELL"

    return "HOLD"


def run_trading_engine():
    logger.info("Trading engine started")

    while True:
        try:
            closes = get_market_data()
            signal = calculate_signal(closes)

            logger.info("Signal: %s", signal)

            if signal == "BUY":
                logger.info("BUY signal detected")

            elif signal == "SELL":
                logger.info("SELL signal detected")

            time.sleep(60)

        except Exception as e:
            logger.error("Error: %s", e)
            time.sleep(30)


if __name__ == "__main__":
    run_trading_engine()
