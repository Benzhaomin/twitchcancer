#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging
logger = logging.getLogger(__name__)

class TimeSplitter:

  # returns the current datetime, TZ-aware (UTC)
  @classmethod
  def now(cls):
    return datetime.datetime.now(datetime.timezone.utc)

  # returns the datetime of one minute ago
  @classmethod
  def last_minute(cls):
    return cls.now() - datetime.timedelta(minutes=1)

  # returns the datetime of one day ago
  @classmethod
  def last_day(cls):
    return cls.now() - datetime.timedelta(days=1)

  # returns the datetime of the beginning of a day
  @classmethod
  def day(cls, datetime):
    return datetime.replace(hour=0, minute=0, second=0, microsecond=0)

  # returns the datetime of one month ago
  @classmethod
  def last_month(cls):
    return cls.now() - datetime.timedelta(days=30)

  # returns the datetime of the beginning of a day
  @classmethod
  def month(cls, datetime):
    return datetime.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
