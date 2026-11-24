
import os
import time
import logging
from decimal import Decimal
from binance.client import Client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("trading_engine")

STARTING_BALANCE = Decimal("100")
SYMBOL = "BTCUSDT"
TRADE_RISK = Decimal("0.01")
STOP_LOSS = Decimal("0.015")
TAKE_PROFIT = Decimal("0.03")
MAX_DAILY_LOSS = Decimal("0.05")
PAPER_TRADING = True

def run_trading_engine():
    balance = STARTING_BALANCE
    daily_loss = Decimal("0")

    logger.info("BTC/USDT AI Bot starting")
    logger.info("PAPER TRADING ONLY")
    logger.info("Starting balance: %s USDT", balance)

    api_key = os.getenv("BINANCE_API_KEY", "")
    api_secret = os.getenv("BINANCE_API_SECRET", "")

    if not api_key or not api_secret:
        logger.warning("API credentials not configured")
        logger.info("Paper mode remains active")

    client = None
    if api_key and api_secret:
        client = Client(api_key, api_secret)

    while True:
        try:
            if daily_loss >= balance * MAX_DAILY_LOSS:
                logger.warning("Daily loss limit reached")
                break

            if client:
                ticker = client.get_symbol_ticker(symbol=SYMBOL)
                price = Decimal(ticker["price"])
                logger.info("BTC price: %s USDT", price)

            logger.info(
                "Paper mode active | Balance: %s USDT",
                balance
            )

            time.sleep(60)

        except Exception as error:
            logger.exception("Trading engine error: %s", error)
            time.sleep(60)

if __name__ == "__main__":
    run_trading_engine()


