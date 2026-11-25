
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("paper_trading")

STARTING_BALANCE = 100.0
TRADING_PAIR = "BTC/USDT"
FEE_RATE = 0.001
TRADE_SIZE = 0.95
SIMULATION_STEPS = 60


def run_trading_engine():
    print("================================")
    print("BTC/USDT PAPER TRADING BOT")
    print("================================")

    balance = STARTING_BALANCE
    btc_held = 0.0
    prices = [90000.0]
    random.seed(42)

    print("Mode: SIMULATION ONLY")
    print("Starting balance:", balance, "USDT")
    print("Trading pair:", TRADING_PAIR)

    for step in range(SIMULATION_STEPS):
        change = random.uniform(-0.008, 0.008)
        price = prices[-1] * (1 + change)
        prices.append(price)

        if len(prices) < 6:
            continue

        short_average = sum(prices[-3:]) / 3
        long_average = sum(prices[-6:]) / 6

        if short_average > long_average and btc_held == 0:
            investment = balance * TRADE_SIZE
            fee = investment * FEE_RATE
            btc_held = (investment - fee) / price
            balance -= investment

            logger.info(
                "SIMULATED BUY: %.8f BTC at %.2f USDT",
                btc_held, price
            )

        elif short_average < long_average and btc_held > 0:
            proceeds = btc_held * price
            fee = proceeds * FEE_RATE
            balance += proceeds - fee
            btc_held = 0.0

            logger.info(
                "SIMULATED SELL at %.2f USDT", price
            )

    final_price = prices[-1]
    portfolio_value = balance + (btc_held * final_price)

    print("--------------------------------")
    print("SIMULATION COMPLETE")
    print("Final simulated price:", round(final_price, 2))
    print("Remaining USDT:", round(balance, 2))
    print("BTC held:", round(btc_held, 8))
    print("Portfolio value:", round(portfolio_value, 2))
    print("Profit/Loss:", round(portfolio_value - STARTING_BALANCE, 2))
    print("REAL TRADES: DISABLED")
    print("================================")


if __name__ == "__main__":
    run_trading_engine()
