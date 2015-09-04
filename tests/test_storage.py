#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import MagicMock

from twitchcancer.storage.storage import Storage

# Storage.cancer()
class TestStorageCancer(unittest.TestCase):

  # check that we transmit calls to a concrete implementation
  def test_transmit(self):
    s = Storage()
    s.storage = MagicMock()
    s.storage.cancer = MagicMock()

    s.cancer()

    self.assertEqual(s.storage.cancer.call_count, 1)

# Storage.leaderboards()
class TestStorageLeaderboards(unittest.TestCase):

  # check that we transmit calls to a concrete implementation
  def test_transmit(self):
    s = Storage()
    s.storage = MagicMock()
    s.storage.leaderboards = MagicMock()

    s.leaderboards()

    self.assertEqual(s.storage.leaderboards.call_count, 1)

# Storage.leaderboard()
class TestStorageLeaderboard(unittest.TestCase):

  # check that we transmit calls to a concrete implementation
  def test_transmit(self):
    s = Storage()
    s.storage = MagicMock()
    s.storage.leaderboard = MagicMock()
    leaderboard = "foo"

    s.leaderboard(leaderboard)

    s.storage.leaderboard.assert_called_once_with(leaderboard)

# Storage.channel()
class TestStorageChannel(unittest.TestCase):

  # check that we transmit calls to a concrete implementation
  def test_transmit(self):
    s = Storage()
    s.storage = MagicMock()
    s.storage.channel = MagicMock()

    channel = "forsenlol"
    s.channel(channel)

    s.storage.channel.assert_called_once_with(channel)

# Storage.status()
class TestStorageStatus(unittest.TestCase):

  # check that we transmit calls to a concrete implementation
  def test_transmit(self):
    s = Storage()
    s.storage = MagicMock()
    s.storage.status = MagicMock()

    s.status()

    self.assertEqual(s.storage.status.call_count, 1)

# Storage.store()
class TestStorageStore(unittest.TestCase):

  # check that we transmit calls to a concrete implementation
  def test_transmit(self):
    s = Storage()
    s.storage = MagicMock()
    s.storage.store = MagicMock()

    channel = "forsenlol"
    message = "message"
    s.store(channel, message)

    s.storage.store.assert_called_once_with(channel, message)

# Storage.record()
class TestStorageRecord(unittest.TestCase):

  # check that we transmit calls to a concrete implementation
  def test_transmit(self):
    s = Storage()
    s.storage = MagicMock()
    s.storage.record = MagicMock()

    s.record()

    self.assertEqual(s.storage.record.call_count, 1)
