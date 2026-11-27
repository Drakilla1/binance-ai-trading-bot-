import unittest
from decimal import Decimal

from paper_trading import ema, rsi


class IndicatorTests(unittest.TestCase):
    def test_ema_returns_decimal(self):
        values = [Decimal("1"), Decimal("2"), Decimal("3")]
        self.assertIsInstance(ema(values, 2), Decimal)

    def test_ema_rejects_insufficient_data(self):
        with self.assertRaises(ValueError):
            ema([Decimal("1")], 2)

    def test_rsi_flat_market_is_neutral(self):
        values = [Decimal("5")] * 16
        self.assertEqual(rsi(values), Decimal("50"))

    def test_rsi_rising_market_is_100(self):
        values = [Decimal(i) for i in range(16)]
        self.assertEqual(rsi(values), Decimal("100"))

    def test_rsi_falling_market_is_zero(self):
        values = [Decimal(20 - i) for i in range(16)]
        self.assertEqual(rsi(values), Decimal("0"))

    def test_rsi_rejects_insufficient_data(self):
        with self.assertRaises(ValueError):
            rsi([Decimal("1")] * 14)


if __name__ == "__main__":
    unittest.main()
