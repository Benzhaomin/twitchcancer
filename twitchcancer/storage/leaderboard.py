#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twitchcancer.utils.timesplitter import TimeSplitter

# use LeaderboardBuilder to create instances
class Leaderboard:

  def __init__(self, horizon, metric, interval):
    self.horizon = horizon
    self.metric = metric
    self.interval = interval

  def __str__(self):
    return ".".join([self.horizon, self.metric, self.interval])

  def __eq__(self, other):
    return self.horizon == other.horizon \
      and self.metric == other.metric \
      and self.interval == other.interval

  def __neq__(self, other):
    return self.horizon != other.horizon \
      or self.metric != other.metric \
      or self.interval != other.interval

  def __hash__(self):
    return hash(str(self))

  # return the first date that should be in this leaderboard
  def start_date(self):
    if self.horizon == "monthly":
      return TimeSplitter.month(TimeSplitter.now())
    elif self.horizon == "daily":
      return TimeSplitter.day(TimeSplitter.now())
    else:
      return None

class LeaderboardBuilder:

  _horizons = [
    'daily',
    'monthly',
    'all',
  ]

  _metrics = [
    'cancer',
    'messages',
    'cpm',
  ]

  _intervals = [
    'minute',
    'total',
    'average',
  ]

  # builds a list of existing leaderboards
  @classmethod
  def build(cls, horizon=None, metric=None, interval=None):

    # limit horizons
    horizons = cls._default_values(horizon, cls._horizons)

    # limit metrics
    metrics = cls._default_values(metric, cls._metrics)

    # limit intervals
    intervals = cls._default_values(interval, cls._intervals)

    result = set()

    for horizon in horizons:
      for metric in metrics:
        for interval in intervals:
          # never build a cpm average
          if metric == "cpm" and interval == "average":
            continue

          result.add(Leaderboard(horizon=horizon, metric=metric, interval=interval))

    return result

  # builds a leaderboard from its name
  @classmethod
  def from_name(cls, name):
    if not cls._is_valid(name):
      return None

    (horizon, metric, interval) = name.split(".")
    return Leaderboard(horizon, metric, interval)

  # checks that a leaderboard exists
  @classmethod
  def _is_valid(cls, name):
    try:
      (horizon, metric, interval) = name.split(".")

      # check the horizon
      if horizon not in cls._horizons:
        return False

      # check the metric
      if metric not in cls._metrics:
        return False

      # check the interval
      if interval not in cls._intervals:
        return False

      # we don't do cpm average
      if metric == "cpm" and interval == "average":
        return False
    except KeyError:
      return False
    except TypeError:
      return False
    except ValueError:
      return False
    except AttributeError:
      return False

    return True

  # returns
  @classmethod
  def _default_values(cls, value, source):
    if value is not None:
      # return a single value if its valid
      if value in source:
        return [value]
      # stop everything if the value is invalid
      else:
        return []
    else:
      # default to the full list of possible values
      return source
