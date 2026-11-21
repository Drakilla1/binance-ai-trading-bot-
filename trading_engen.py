import os
import time
import logging
from binance.client import Client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("trading_engine")

API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_API_SECRET", "")

SYMBOL = "BTCUSDT"
INTERVAL = Client.KLINE_INTERVAL_1MINUTE
CHECK_INTERVAL = 60

# SAFETY: This bot is in signal-only mode.
# It will NOT place real trades.
DRY_RUN = True


def get_client():
    return Client(API_KEY, API_SECRET)


def get_market_data(client):
    candles = client.get_klines(
        symbol=SYMBOL,
        interval=INTERVAL,
        limit=100
    )

    closes = [float(candle[4]) for candle in candles]
    return closes


def calculate_signal(closes):
    if len(closes) < 50:
        return "WAIT"

    short_average = sum(closes[-9:]) / 9
    long_average = sum(closes[-50:]) / 50

    if short_average > long_average:
        return "BUY SIGNAL"

    elif short_average < long_average:
        return "SELL SIGNAL"

    return "WAIT"


def run_trading_engine():
    logger.info("Binance AI Trading Bot starting...")
    logger.info("Mode: SIGNAL ONLY | No real orders")

    client = get_client()

    while True:
        try:
            closes = get_market_data(client)
            price = closes[-1]

            signal = calculate_signal(closes)

            logger.info(
                "Symbol: %s | Price: %.2f | Signal: %s",
                SYMBOL,
                price,
                signal
            )

            if DRY_RUN:
                logger.info("Dry-run mode enabled. No orders placed.")

            time.sleep(CHECK_INTERVAL)

        except Exception as e:
            logger.error("Trading engine error: %s", e)
            time.sleep(15)
