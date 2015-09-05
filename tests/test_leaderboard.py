#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import datetime

from twitchcancer.storage.leaderboard import Leaderboard, LeaderboardBuilder

# Leaderboard.__init__()
class TestLeaderboardInit(unittest.TestCase):

  def test_default(self):
    leaderboard = Leaderboard(horizon="foo", metric="bar", interval="baz")

    self.assertEqual(leaderboard.horizon, "foo")
    self.assertEqual(leaderboard.metric, "bar")
    self.assertEqual(leaderboard.interval, "baz")

# Leaderboard.__str__()
class TestLeaderboardStr(unittest.TestCase):

  def test_default(self):
    leaderboard = Leaderboard(horizon="foo", metric="bar", interval="baz")

    self.assertEqual(str(leaderboard), "foo.bar.baz")

# Leaderboard.__eq__()
class TestLeaderboardEq(unittest.TestCase):

  def test_default(self):
    leaderboard1 = Leaderboard(horizon="foo", metric="bar", interval="baz")
    leaderboard2 = Leaderboard(horizon="foo", metric="bar", interval="baz")
    leaderboard3 = Leaderboard(horizon="baz", metric="bar", interval="foo")

    self.assertTrue(leaderboard1 == leaderboard2)
    self.assertFalse(leaderboard1 == leaderboard3)

# Leaderboard.__neq__()
class TestLeaderboardNeq(unittest.TestCase):

  def test_default(self):
    leaderboard1 = Leaderboard(horizon="foo", metric="bar", interval="baz")
    leaderboard2 = Leaderboard(horizon="foo", metric="bar", interval="baz")
    leaderboard3 = Leaderboard(horizon="baz", metric="bar", interval="foo")

    self.assertFalse(leaderboard1 != leaderboard2)
    self.assertTrue(leaderboard1 != leaderboard3)

# Leaderboard.__hash__()
class TestLeaderboardHash(unittest.TestCase):

  def test_default(self):
    leaderboard1 = Leaderboard(horizon="foo", metric="bar", interval="baz")
    leaderboard2 = Leaderboard(horizon="foo", metric="bar", interval="baz")
    leaderboard3 = Leaderboard(horizon="baz", metric="bar", interval="foo")

    self.assertTrue(hash(leaderboard1) == hash(leaderboard2))
    self.assertFalse(hash(leaderboard1) == hash(leaderboard3))

# Leaderboard.start_date()
class TestLeaderboardStartDate(unittest.TestCase):

  # check that bogus leaderboards get no start date
  def test_bogus(self):
    leaderboard = Leaderboard(horizon="foo", metric="bar", interval="foo")

    self.assertIsNone(leaderboard.start_date())

  # check that the all-time leaderboard gets no start date
  def test_all(self):
    leaderboard = Leaderboard(horizon="all", metric="bar", interval="baz")

    self.assertIsNone(leaderboard.start_date())

  # check that the monthly leaderboard starts on the first day of the current month
  def test_monthly(self):
    leaderboard = Leaderboard(horizon="monthly", metric="bar", interval="baz")

    date = leaderboard.start_date()
    now = datetime.datetime.now(datetime.timezone.utc)

    self.assertEqual(now.month, date.month)
    self.assertEqual(1, date.day)
    self.assertEqual(0, date.hour)
    self.assertEqual(0, date.minute)

  # check that the daiky leaderboard starts on the first day of the current month
  def test_daily(self):
    leaderboard = Leaderboard(horizon="daily", metric="bar", interval="baz")

    date = leaderboard.start_date()
    now = datetime.datetime.now(datetime.timezone.utc)

    self.assertEqual(now.day, date.day)
    self.assertEqual(0, date.hour)
    self.assertEqual(0, date.minute)


# LeaderboardBuilder._is_valid()
class TestLeaderboardBuilderIsValid(unittest.TestCase):

  # check that we handle weird names
  def test_bogus_names(self):
    self.assertFalse(LeaderboardBuilder._is_valid(None))
    self.assertFalse(LeaderboardBuilder._is_valid({}))
    self.assertFalse(LeaderboardBuilder._is_valid([]))
    self.assertFalse(LeaderboardBuilder._is_valid(1))
    self.assertFalse(LeaderboardBuilder._is_valid(""))
    self.assertFalse(LeaderboardBuilder._is_valid("foo"))
    self.assertFalse(LeaderboardBuilder._is_valid("foo.bar.baz"))

  # check that real names go through correctly
  def test_default(self):
    self.assertTrue(LeaderboardBuilder._is_valid("daily.cancer.minute"))
    self.assertFalse(LeaderboardBuilder._is_valid("all.cpm.average"))

# Leaderboard._default_values()
class TestLeaderboardBuilderDefaultValues(unittest.TestCase):

  def setUp(self):
    self.values = LeaderboardBuilder._horizons

  # check that invalid values default to an empty list
  def test_bogus_values(self):
    self.assertEqual(LeaderboardBuilder._default_values([], self.values), [])
    self.assertEqual(LeaderboardBuilder._default_values({}, self.values), [])
    self.assertEqual(LeaderboardBuilder._default_values(1, self.values), [])
    self.assertEqual(LeaderboardBuilder._default_values("", self.values), [])
    self.assertEqual(LeaderboardBuilder._default_values("foo", self.values), [])

  # check that the default is the full list of values itself
  def test_default_values(self):
    self.assertEqual(LeaderboardBuilder._default_values(None, self.values), self.values)

  # check that a valid value is returned, as a list
  def test_default(self):
    self.assertEqual(LeaderboardBuilder._default_values(self.values[0], self.values), [self.values[0]])

# LeaderboardBuilder.build()
class TestLeaderboardBuilderBuild(unittest.TestCase):

  # check that we get the right total of leaderboard (3 cpm.average are banned)
  def test_default(self):
    horizons_count = len(LeaderboardBuilder._horizons)
    metrics_count = len(LeaderboardBuilder._metrics)
    intervals_count = len(LeaderboardBuilder._intervals)

    # all
    self.assertEqual(len(LeaderboardBuilder.build()), horizons_count * metrics_count * intervals_count - 3)

    # all the all-time leaderboards
    self.assertEqual(len(LeaderboardBuilder.build(horizon="all")), metrics_count * intervals_count - 1)

    # all the cancer leaderboards
    self.assertEqual(len(LeaderboardBuilder.build(metric="cancer")), horizons_count * intervals_count)

    # all the minute leaderboards
    self.assertEqual(len(LeaderboardBuilder.build(interval="minute")), horizons_count * metrics_count)

    # all the average leaderboards
    self.assertEqual(len(LeaderboardBuilder.build(interval="average")), horizons_count * metrics_count - 3)

# LeaderboardBuilder.from_name()
class TestLeaderboardBuilderFromName(unittest.TestCase):

  # check that we get the right total of leaderboard (3 cpm.average are banned)
  def test_default(self):
    self.assertIsNone(LeaderboardBuilder.from_name(None))
    self.assertIsNone(LeaderboardBuilder.from_name("foo"))
    self.assertIsNotNone(LeaderboardBuilder.from_name("all.cancer.minute"))
