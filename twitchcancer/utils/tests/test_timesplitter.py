import datetime
import unittest

from twitchcancer.utils.timesplitter import TimeSplitter


class DeltaComparisonTest(unittest.TestCase):

    # check that 'date' is around 'expected' seconds ago (millisecond precision)
    def assert_seconds_ago(self, date, expected):
        now = datetime.datetime.now(datetime.timezone.utc)
        delta = now - date

        return self.assertAlmostEqual(delta.total_seconds(), expected, places=3)


# TimeSplitter.now()
class TestTimeSplitterNow(DeltaComparisonTest):

    # check that the now is around now
    def test_default(self):
        self.assert_seconds_ago(TimeSplitter.now(), 0)


# TimeSplitter.last_minute()
class TestTimeSplitterLastMinute(DeltaComparisonTest):

    # check that the last minute is around a minute ago
    def test_default(self):
        self.assert_seconds_ago(TimeSplitter.last_minute(), 60)


# TimeSplitter.last_day()
class TestTimeSplitterLastDay(DeltaComparisonTest):

    # check that the last day is around a day ago
    def test_default(self):
        self.assert_seconds_ago(TimeSplitter.last_day(), 60 * 60 * 24)


# TimeSplitter.last_month()
class TestTimeSplitterLastMonth(DeltaComparisonTest):

    # check that the last day is around 30 days ago
    def test_default(self):
        self.assert_seconds_ago(TimeSplitter.last_month(), 30 * 60 * 60 * 24)


# TimeSplitter.day()
class TestTimeSplitterDay(unittest.TestCase):

    # check that a day is rounded down correctly
    def test_default(self):
        result = TimeSplitter.day(datetime.datetime(2015, 2, 20, 12, 20, 30))
        expected = datetime.datetime(2015, 2, 20, 0, 0, 0)

        self.assertEqual(result, expected)


# TimeSplitter.month()
class TestTimeSplitterMonth(unittest.TestCase):

    # check that a day is rounded down correctly
    def test_default(self):
        result = TimeSplitter.month(datetime.datetime(2015, 2, 20, 12, 20, 30))
        expected = datetime.datetime(2015, 2, 1, 0, 0, 0)

        self.assertEqual(result, expected)
