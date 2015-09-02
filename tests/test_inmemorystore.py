#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import unittest
from unittest.mock import patch, MagicMock

from twitchcancer.storage.inmemorystore import InMemoryStore

# InMemoryStore.__init__()
class TestInMemoryStoreInit(unittest.TestCase):
  pass

# InMemoryStore._live_message_breakpoint()
# InMemoryStore.archive()
class TestInMemoryStoreArchive(unittest.TestCase):

  # check that we simply get an empty dict when no messages were recorded
  def test_no_messages(self):
    m = InMemoryStore()

    self.assertEqual(m.archive(), {})

  # check that archive returns a summary of all messages before the breakpoint
  def test_with_messages(self):
    m = InMemoryStore()

    channel1 = "channel1"
    channel2 = "channel2"
    now1 = datetime.datetime.now(datetime.timezone.utc).replace(second=0, microsecond=0) - datetime.timedelta(seconds=180)
    now2 = datetime.datetime.now(datetime.timezone.utc).replace(second=0, microsecond=0)

    m.messages.append({'date': now1, 'channel': channel1, 'cancer': 10})
    m.messages.append({'date': now1, 'channel': channel1, 'cancer': 20})
    m.messages.append({'date': now1, 'channel': channel2, 'cancer': 50})
    m.messages.append({'date': now2, 'channel': channel2, 'cancer': 1000})

    expected = {now1: {
      channel1: { 'cancer': 30, 'messages': 2 },
      channel2: { 'cancer': 50, 'messages': 1 }
    }}

    actual = m.archive()

    self.assertEqual(actual[now1][channel1], expected[now1][channel1])
    self.assertEqual(actual[now1][channel2], expected[now1][channel2])
    self.assertEqual(len(m.messages), 1)

# InMemoryStore._live_message_breakpoint()
# InMemoryStore.cancer()
class TestInMemoryStoreCancer(unittest.TestCase):

  # check that we simply get an empty list when no messages were recorded
  def test_no_messages(self):
    m = InMemoryStore()

    self.assertEqual(m.cancer(), [])

  # check that cancer returns a summary of all currently live records
  def test_with_messages(self):
    m = InMemoryStore()

    channel = "channel"
    now1 = datetime.datetime.now(datetime.timezone.utc).replace(second=0, microsecond=0) - datetime.timedelta(seconds=180)
    now2 = datetime.datetime.now(datetime.timezone.utc).replace(second=0, microsecond=0)

    m.messages.append({'date': now1, 'channel': channel, 'cancer': 10})
    m.messages.append({'date': now2, 'channel': channel, 'cancer': 1000})
    m.messages.append({'date': now2, 'channel': channel, 'cancer': 1})

    expected = [ {
      'channel': channel,
      'cancer': 1001,
      'messages': 2
    }]

    actual = m.cancer()

    self.assertEqual(actual, expected)

# InMemoryStore.store()
class TestInMemoryStoreStore(unittest.TestCase):

  # check that store does store message
  def test_default(self):
    m = InMemoryStore()
    channel = "channel"
    cancer = 10

    m.store(channel, cancer)

    actual = m.messages.popleft()

    # don't compare the whole dict because we might get the date wrong
    self.assertEqual(actual['channel'], channel)
    self.assertEqual(actual['cancer'], cancer)

# InMemoryStore._live_message_breakpoint()
class TestInMemoryStoreLiveMessageBreakpoint(unittest.TestCase):
  pass
