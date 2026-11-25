
import logging
from binance.client import Client

# PAPER TRADING ONLY
SYMBOL = "BTCUSDT"
INTERVAL = Client.KLINE_INTERVAL_15MINUTE
STARTING_BALANCE = 100.0
RISK_PERCENT = 1.0
STOP_LOSS_PERCENT = 1.0
TAKE_PROFIT_PERCENT = 2.0

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s"
)
logger = logging.getLogger("BTC_AI_BOT")


def ema(values, period):
    multiplier = 2 / (period + 1)
    result = values[0]

    for price in values[1:]:
        result = (price * multiplier) + (
            result * (1 - multiplier)
        )

    return result


def calculate_rsi(prices, period=14):
    changes = [
        prices[i] - prices[i - 1]
        for i in range(1, len(prices))
    ]

    gains = [max(change, 0) for change in changes]
    losses = [max(-change, 0) for change in changes]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(gains)):
        avg_gain = (
            avg_gain * (period - 1) + gains[i]
        ) / period
        avg_loss = (
            avg_loss * (period - 1) + losses[i]
        ) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def run_trading_engine():
    logger.info("BTC/USDT PAPER TRADING BOT STARTED")

    try:
        # Public market data only. No trading credentials.
        client = Client()

        candles = client.get_klines(
            symbol=SYMBOL,
            interval=INTERVAL,
            limit=100
        )

        # Exclude the potentially unfinished candle.
        candles = candles[:-1]

        prices = [float(candle[4]) for candle in candles]

        if len(prices) < 51:
            logger.warning("Not enough market data.")
            return

        current_price = prices[-1]

        ema20 = ema(prices[-50:], 20)
        ema50 = ema(prices[-50:], 50)
        rsi = calculate_rsi(prices)

        logger.info("BTC Price: %.2f USDT", current_price)
        logger.info("EMA 20: %.2f", ema20)
        logger.info("EMA 50: %.2f", ema50)
        logger.info("RSI: %.2f", rsi)

        balance = STARTING_BALANCE
        risk_amount = balance * RISK_PERCENT / 100

        stop_loss = current_price * (
            1 - STOP_LOSS_PERCENT / 100
        )

        take_profit = current_price * (
            1 + TAKE_PROFIT_PERCENT / 100
        )

        if (
            ema20 > ema50
            and current_price > ema20
            and 50 < rsi < 70
        ):
            logger.info("BUY SIGNAL DETECTED")
            logger.info("Paper balance: %.2f USDT", balance)
            logger.info("Risk budget: %.2f USDT", risk_amount)
            logger.info("Stop loss: %.2f", stop_loss)
            logger.info("Take profit: %.2f", take_profit)

        elif ema20 < ema50 or rsi < 40:
            logger.info("SELL / EXIT SIGNAL DETECTED")

        else:
            logger.info("HOLD - WAITING FOR A BETTER SIGNAL")

        logger.info("Market analysis completed.")
        logger.info("PAPER TRADING ONLY - NO REAL ORDERS.")

    except Exception:
        logger.exception("Trading engine error")


if __name__ == "__main__":
    run_trading_engine()



