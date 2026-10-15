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

    def test_prints_iso_datetime_to_seconds_and_newline(self):
        now = datetime(2026, 10, 9, 14, 30, 45, 999999, tzinfo=timezone.utc)
        output = io.StringIO()
        with redirect_stdout(output):
            result = print_current_date(now)
        self.assertIsNone(result)
        self.assertEqual(output.getvalue(), "2026-10-09T14:30:45+00:00\n")

    def test_prints_injected_date_at_midnight_utc(self):
        output = io.StringIO()
        with redirect_stdout(output):
            result = print_current_date(date(2026, 10, 9))
        self.assertIsNone(result)
        self.assertEqual(output.getvalue(), "2026-10-09T00:00:00+00:00\n")

    def test_print_default_uses_utc(self):
        fixed = datetime(2026, 10, 9, 14, 30, 45, 123456, tzinfo=timezone.utc)
        output = io.StringIO()
        with patch("demo_date.datetime", wraps=datetime) as clock:
            clock.now.return_value = fixed
            with redirect_stdout(output):
                print_current_date()
        clock.now.assert_called_once_with(timezone.utc)
        self.assertEqual(output.getvalue(), "2026-10-09T14:30:45+00:00\n")

    def test_prints_naive_datetime_as_utc(self):
        output = io.StringIO()
        with redirect_stdout(output):
            print_current_date(datetime(2026, 10, 9, 14, 30, 45))
        self.assertEqual(output.getvalue(), "2026-10-09T14:30:45+00:00\n")

    def test_prints_aware_datetime_in_utc(self):
        cases = (
            (
                datetime(2026, 1, 1, 1, 2, 3, tzinfo=timezone(timedelta(hours=3))),
                "2025-12-31T22:02:03+00:00\n",
            ),
            (
                datetime(2026, 12, 31, 23, 2, 3, tzinfo=timezone(timedelta(hours=-3))),
                "2027-01-01T02:02:03+00:00\n",
            ),
        )
        for now, expected in cases:
            with self.subTest(now=now):
                output = io.StringIO()
                with redirect_stdout(output):
                    print_current_date(now)
                self.assertEqual(output.getvalue(), expected)

    def test_rejects_invalid_input(self):
        for function in (current_date, print_current_date):
            with self.subTest(function=function.__name__):
                with self.assertRaisesRegex(
                    TypeError, "now must be a datetime, date, or None"
                ):
                    function("2026-10-09")


if __name__ == "__main__":
    unittest.main()
