import json
import logging
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from binance.client import Client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
log = logging.getLogger("paper_trading")

SYMBOL = "BTCUSDT"
INTERVAL = Client.KLINE_INTERVAL_5MINUTE

STARTING_BALANCE = Decimal("100")
RISK_PER_TRADE = Decimal("0.01")
DAILY_LOSS_LIMIT = Decimal("0.03")
STOP_LOSS = Decimal("0.01")
TAKE_PROFIT = Decimal("0.02")
FEE_RATE = Decimal("0.001")

STATE_FILE = Path("paper_state.json")

# Public market data only. No exchange orders or trading credentials.
client = Client("", "")


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())

    return {
        "balance": str(STARTING_BALANCE),
        "btc": "0",
        "entry": None,
        "day": datetime.now(timezone.utc).date().isoformat(),
        "day_start": str(STARTING_BALANCE),
        "trades": 0
    }


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def ema(values, period):
    if period <= 0 or len(values) < period:
        raise ValueError("EMA requires a positive period and enough values")

    result = values[0]
    alpha = Decimal("2") / Decimal(period + 1)

    for value in values[1:]:
        result = alpha * value + (1 - alpha) * result

    return result


def rsi(values, period=14):
    if period <= 0 or len(values) <= period:
        raise ValueError("RSI requires more values than its positive period")

    changes = [
        values[i] - values[i - 1]
        for i in range(1, len(values))
    ]
    gains = [max(change, Decimal("0")) for change in changes]
    losses = [max(-change, Decimal("0")) for change in changes]

    avg_gain = sum(gains[-period:]) / Decimal(period)
    avg_loss = sum(losses[-period:]) / Decimal(period)

    if avg_gain == 0 and avg_loss == 0:
        return Decimal("50")
    if avg_loss == 0:
        return Decimal("100")
    if avg_gain == 0:
        return Decimal("0")

    rs = avg_gain / avg_loss
    return Decimal("100") - (
        Decimal("100") / (Decimal("1") + rs)
    )


def market_data():
    candles = client.get_klines(
        symbol=SYMBOL,
        interval=INTERVAL,
        limit=60
    )

    # Ignore the currently forming candle.
    closes = [Decimal(c[4]) for c in candles[:-1]]

    if len(closes) < 22:
        raise RuntimeError("Not enough market data")

    return closes, closes[-1]


def run():
    state = load_state()
    closes, price = market_data()

    balance = Decimal(state["balance"])
    btc = Decimal(state["btc"])
    entry = Decimal(state["entry"]) if state["entry"] else None

    today = datetime.now(timezone.utc).date().isoformat()
    if state["day"] != today:
        state["day"] = today
        state["day_start"] = str(balance + btc * price)

    day_start = Decimal(state["day_start"])
    equity = balance + btc * price

    # A zero/negative baseline must halt new entries rather than divide by zero.
    daily_loss = (
        max(Decimal("0"), (day_start - equity) / day_start)
        if day_start > 0 else Decimal("1")
    )
    loss_limit_reached = daily_loss >= DAILY_LOSS_LIMIT

    fast = ema(closes[-30:], 9)
    slow = ema(closes[-30:], 21)
    momentum = rsi(closes)

    log.info(
        "Price=%s EMA9=%s EMA21=%s RSI=%s Equity=%s",
        price, fast, slow, momentum, equity
    )

    # Always process protective exits, even after the daily loss limit is hit.
    if btc > 0 and entry:
        change = (price - entry) / entry

        if change <= -STOP_LOSS or change >= TAKE_PROFIT:
            balance += btc * price * (1 - FEE_RATE)
            log.info("SIMULATED EXIT at %s", price)
            btc = Decimal("0")
            entry = None

    # The daily loss limit blocks new positions, never protective exits.
    if loss_limit_reached:
        log.warning("Daily loss limit reached. No new positions will be opened.")
    elif btc == 0 and fast > slow and momentum > 50:
        risk = equity * RISK_PER_TRADE
        position_value = min(balance, risk / STOP_LOSS)

        if position_value > 0:
            fee = position_value * FEE_RATE
            btc = (position_value - fee) / price
            balance -= position_value
            entry = price
            state["trades"] += 1
            log.info("SIMULATED BUY at %s", price)

    state["balance"] = str(balance)
    state["btc"] = str(btc)
    state["entry"] = str(entry) if entry else None
    save_state(state)

    log.info(
        "Simulation complete. USDT=%s BTC=%s",
        balance, btc
    )


if __name__ == "__main__":
    run()
