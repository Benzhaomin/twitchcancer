#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import unittest
from unittest.mock import patch, MagicMock

from twitchcancer.config import Config
from twitchcancer.storage.persistentstore import PersistentStore

# PersistentStore.__init__()
class TestPersistentStoreInit(unittest.TestCase):
  pass

# PersistentStore.update_leaderboard()
class TestPersistentStoreUpdateLeaderboard(unittest.TestCase):
  pass

# PersistentStore._build_leaderboard_update_query()
class TestPersistentStoreBuildLeaderboardUpdateQuery(unittest.TestCase):
  pass

# PersistentStore._history_to_leaderboard()
class TestPersistentStoreHistoryToLeaderboard(unittest.TestCase):
  pass

# PersistentStore.leaderboards()
class TestPersistentStoreLeaderboards(unittest.TestCase):
  pass

# PersistentStore.leaderboard()
class TestPersistentStoreLeaderboard(unittest.TestCase):
  pass

# PersistentStore.update_leaderboard()
# PersistentStore._build_leaderboard_update_query()
# PersistentStore._history_to_leaderboard()
# PersistentStore.leaderboards()
# PersistentStore.leaderboard()
class TestPersistentStoreLeaderboardComprehensive(unittest.TestCase):

  def setUp(self):
    Config.config['record']['mongodb']['database'] = "twitchcancer_tests"

  # check that adding and querying for leaderboards works correctly
  def test_comprehensive(self):
  # uncomment to disable
  #def dont_test_comprehensive():
    p = PersistentStore()
    p.db.leaderboard.drop()

    channel = "channel"
    now1 = datetime.datetime.now().replace(microsecond=0)
    now2 = now1 + datetime.timedelta(seconds=60)

    p.update_leaderboard({'date': now1, 'channel': channel, 'cancer': 30, 'messages': 40 })
    p.update_leaderboard({'date': now2, 'channel': channel, 'cancer': 5, 'messages': 50 })

    expected = {
      'cancer': {
        'minute':   [{ 'channel': channel, 'date': now1, 'value': '30' }],
        'average':  [{ 'channel': channel, 'date': now1, 'value': '17.5' }],
        'total':    [{ 'channel': channel, 'date': now1, 'value': '35' }],
      },
      'messages': {
        'minute':   [{ 'channel': channel, 'date': now2, 'value': '50'}],
        'average':  [{ 'channel': channel, 'date': now1, 'value': '45.0' }],
        'total':    [{ 'channel': channel, 'date': now1, 'value': '90' }],
      },
      'cpm': {
        'minute':   [{ 'channel': channel, 'date': now1, 'value': '0.75' }],
        'average':  [{ 'channel': channel, 'date': now1, 'value': str((0.75+0.1)/2) }],
        'total':    [{ 'channel': channel, 'date': now1, 'value': str(35/90) }],
      }
    }

    actual = p.leaderboards()

    # lay all sub-dict out to ease debugging when one fails
    def compare(this, that, key1, key2):
      self.assertEqual(this[key1][key2], that[key1][key2])

    compare(actual, expected, 'cancer', 'minute')
    compare(actual, expected, 'cancer', 'average')
    compare(actual, expected, 'cancer', 'total')
    compare(actual, expected, 'messages', 'minute')
    compare(actual, expected, 'messages', 'average')
    compare(actual, expected, 'messages', 'total')
    compare(actual, expected, 'cpm', 'minute')
    compare(actual, expected, 'cpm', 'average')
    compare(actual, expected, 'cpm', 'total')

  def tearDown(self):
    p = PersistentStore()
    p.db.leaderboard.drop()

# PersistentStore._leaderboard_rank()
class TestPersistentStoreLeaderboardRank(unittest.TestCase):
  pass

# PersistentStore._leaderboard_rank()
# PersistentStore.channel()
class TestPersistentStoreChannel(unittest.TestCase):

  def setUp(self):
    Config.config['record']['mongodb']['database'] = "twitchcancer_tests"

  # check that adding records and querying for channel stats works correctly
  def test_comprehensive(self):
    p = PersistentStore()
    p.db.leaderboard.drop()

    channel = "channel"
    now1 = datetime.datetime.now().replace(microsecond=0)
    now2 = now1 + datetime.timedelta(seconds=60)

    p.update_leaderboard({'date': now1, 'channel': channel, 'cancer': 30, 'messages': 40 })
    p.update_leaderboard({'date': now2, 'channel': channel, 'cancer': 5, 'messages': 50 })

    expected = {
      'channel': channel,

      'minute': {
        'cancer':     { 'value': 30, 'date': now1, 'rank': 1 },
        'messages':   { 'value': 50, 'date': now2, 'rank': 1 },
        'cpm':        { 'value': 0.75, 'date': now1, 'rank': 1 },
      },
      'total': {
        'cancer':     { 'value': 35, 'rank': 1 },
        'messages':   { 'value': 90, 'rank': 1 },
        'cpm':        { 'value': 35/90, 'rank': 1 },
        'duration':   { 'value': 2, 'rank': 1 },
        'since':      now1
      },
      'average': {
        'cancer':     { 'value': 17.5, 'rank': 1 },
        'messages':   { 'value': 45.0, 'rank': 1 },
        'cpm':        { 'value': (0.75+0.1)/2, 'rank': 1 }
      }
    }

    actual = p.channel(channel)

    # lay all sub-dict out to ease debugging when one fails
    def compare(this, that, key1, key2):
      self.assertEqual(this[key1][key2], that[key1][key2])

    self.assertEqual(actual['channel'], expected['channel'])
    compare(actual, expected, 'minute', 'cancer')
    compare(actual, expected, 'average', 'cancer')
    compare(actual, expected, 'total', 'cancer')
    compare(actual, expected, 'minute', 'messages')
    compare(actual, expected, 'average', 'messages')
    compare(actual, expected, 'total', 'messages')
    compare(actual, expected, 'minute', 'cpm')
    compare(actual, expected, 'average', 'cpm')
    compare(actual, expected, 'total', 'cpm')

  def tearDown(self):
    p = PersistentStore()
    p.db.leaderboard.drop()

# PersistentStore.status()
class TestPersistentStoreStatus(unittest.TestCase):

  def setUp(self):
    Config.config['record']['mongodb']['database'] = "twitchcancer_tests"

  # check that adding records and querying for the overall status works correctly
  def test_comprehensive(self):
    p = PersistentStore()
    p.db.leaderboard.drop()

    channel = "channel"
    now1 = datetime.datetime.now().replace(microsecond=0)
    now2 = now1 + datetime.timedelta(seconds=60)

    p.update_leaderboard({'date': now1, 'channel': channel, 'cancer': 30, 'messages': 40 })
    p.update_leaderboard({'date': now2, 'channel': channel, 'cancer': 5, 'messages': 50 })

    expected = { '_id': 'null', 'channels': 1, 'messages': 90, 'cancer': 35 }
    actual = p.status()

    self.assertEqual(actual, expected)

  def tearDown(self):
    p = PersistentStore()
    p.db.leaderboard.drop()
