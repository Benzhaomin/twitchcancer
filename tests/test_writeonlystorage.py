#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle
import unittest
from unittest.mock import patch, MagicMock

from twitchcancer.storage.writeonlystorage import WriteOnlyStorage

# WriteOnlyStorage.*()
class TestWriteOnlyStorageNotImplemented(unittest.TestCase):

  # check that we don't answer calls we can't answer
  @patch('twitchcancer.storage.writeonlystorage.WriteOnlyStorage.__init__', return_value=None)
  def test_not_implemented(self, init):
    w = WriteOnlyStorage()

    self.assertRaises(NotImplementedError, lambda: w.cancer())
    self.assertRaises(NotImplementedError, lambda: w.leaderboard(None))
    self.assertRaises(NotImplementedError, lambda: w.leaderboards(None))
    self.assertRaises(NotImplementedError, lambda: w.channel(None))
    self.assertRaises(NotImplementedError, lambda: w.status())
    self.assertRaises(NotImplementedError, lambda: w.store(None, None))
    self.assertRaises(NotImplementedError, lambda: w.search(None))

# WriteOnlyStorage.record()
class TestWriteOnlyStorageRecord(unittest.TestCase):

  # check that we get data on a socket and forward it to the persistent store
  @patch('twitchcancer.storage.writeonlystorage.WriteOnlyStorage.__init__', return_value=None)
  def test_not_implemented(self, init):
    w = WriteOnlyStorage()
    w._store = MagicMock()
    w._store.update_leaderboard = MagicMock(side_effect=KeyboardInterrupt)
    w.socket = MagicMock()
    w.socket.recv_multipart = MagicMock(return_value=(
      b'topic',
      pickle.dumps({'data':'foo'})
    ))

    try:
      w.record()
    except KeyboardInterrupt:
      # we raised that exception to stop the infinite loop
      pass

    w._store.update_leaderboard.assert_called_once_with({'data': 'foo'})
