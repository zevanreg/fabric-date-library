import io
import unittest
from contextlib import redirect_stdout
from datetime import date, datetime, timedelta, timezone
from unittest.mock import patch

from demo_date import current_date, print_current_date


class DateTests(unittest.TestCase):
    def test_default_uses_utc(self):
        fixed = datetime(2026, 10, 9, 0, 15, tzinfo=timezone.utc)
        with patch("demo_date.datetime", wraps=datetime) as clock:
            clock.now.return_value = fixed
            self.assertEqual(current_date(), date(2026, 10, 9))
            clock.now.assert_called_once_with(timezone.utc)

    def test_injected_date(self):
        self.assertEqual(current_date(date(2024, 2, 29)), date(2024, 2, 29))

    def test_naive_datetime_is_utc(self):
        self.assertEqual(current_date(datetime(2026, 1, 1)), date(2026, 1, 1))

    def test_aware_datetime_converts_to_previous_utc_day(self):
        now = datetime(2026, 1, 1, 1, tzinfo=timezone(timedelta(hours=3)))
        self.assertEqual(current_date(now), date(2025, 12, 31))

    def test_aware_datetime_converts_to_next_utc_day(self):
        now = datetime(2026, 12, 31, 23, tzinfo=timezone(timedelta(hours=-3)))
        self.assertEqual(current_date(now), date(2027, 1, 1))

    def test_prints_only_iso_date_and_newline(self):
        output = io.StringIO()
        with redirect_stdout(output):
            result = print_current_date(date(2026, 10, 9))
        self.assertIsNone(result)
        self.assertEqual(output.getvalue(), "2026-10-09\n")

    def test_print_default_uses_current_date(self):
        output = io.StringIO()
        with patch("demo_date.current_date", return_value=date(2026, 10, 9)) as clock:
            with redirect_stdout(output):
                print_current_date()
        clock.assert_called_once_with(None)
        self.assertEqual(output.getvalue(), "2026-10-09\n")

    def test_rejects_invalid_input(self):
        with self.assertRaises(TypeError):
            current_date("2026-10-09")


if __name__ == "__main__":
    unittest.main()
