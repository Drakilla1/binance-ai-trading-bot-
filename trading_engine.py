
import time
import logging
from binance.client import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trading_engine")

# Public market data connection (no trading keys needed)
client = Client()

SYMBOL = "BTCUSDT"
INTERVAL = Client.KLINE_INTERVAL_1HOUR

# PAPER TRADING SETTINGS
STARTING_BALANCE = 100.0
TRADE_AMOUNT = 20.0
STOP_LOSS = 0.02
TAKE_PROFIT = 0.04
FEE_RATE = 0.001

cash = STARTING_BALANCE
btc_position = 0.0
entry_price = 0.0
previous_signal = "HOLD"


def get_market_data():
    candles = client.get_klines(
        symbol=SYMBOL,
        interval=INTERVAL,
        limit=100
    )
    return [float(candle[4]) for candle in candles]


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


def buy(price):
    global cash, btc_position, entry_price

    if btc_position > 0:
        return

    if cash < TRADE_AMOUNT:
        logger.info("Insufficient virtual balance")
        return

    fee = TRADE_AMOUNT * FEE_RATE
    btc_position = (TRADE_AMOUNT - fee) / price
    cash -= TRADE_AMOUNT
    entry_price = price

    logger.info("PAPER BUY: %.8f BTC at %.2f", btc_position, price)


def sell(price, reason):
    global cash, btc_position, entry_price

    if btc_position <= 0:
        return

    proceeds = btc_position * price
    fee = proceeds * FEE_RATE
    net = proceeds - fee

    profit = net - TRADE_AMOUNT

    cash += net

    logger.info(
        "PAPER SELL: price=%.2f reason=%s P/L=%.2f",
        price, reason, profit
    )

    btc_position = 0.0
    entry_price = 0.0


def run_trading_engine():
    global previous_signal

    logger.info("Paper trading engine started")
    logger.info("Starting virtual balance: $%.2f", cash)

    while True:
        try:
            closes = get_market_data()
            price = closes[-1]

            signal = calculate_signal(closes)

            logger.info(
                "Price: %.2f | Signal: %s | Cash: %.2f",
                price, signal, cash
            )

            # Risk management
            if btc_position > 0:
                change = (price - entry_price) / entry_price

                if change <= -STOP_LOSS:
                    sell(price, "STOP LOSS")

                elif change >= TAKE_PROFIT:
                    sell(price, "TAKE PROFIT")

            # Trade only on a signal change
            if signal != previous_signal:

                if signal == "BUY" and btc_position == 0:
                    buy(price)

                elif signal == "SELL" and btc_position > 0:
                    sell(price, "SELL SIGNAL")

            previous_signal = signal

            time.sleep(60)

        except Exception as e:
            logger.error("Engine error: %s", e)
            time.sleep(30)


if __name__ == "__main__":
    run_trading_engine()
