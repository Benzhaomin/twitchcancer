#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle
import unittest
from unittest.mock import patch, MagicMock

from twitchcancer.storage.memorystorage import MemoryStorage

# MemoryStorage.*()
class TestMemoryStorageNotImplemented(unittest.TestCase):

  # check that we don't answer calls we can't answer
  @patch('twitchcancer.storage.memorystorage.MemoryStorage.__init__', return_value=None)
  def test_not_implemented(self, init):
    m = MemoryStorage()

    self.assertRaises(NotImplementedError, lambda: m.leaderboards())
    self.assertRaises(NotImplementedError, lambda: m.channel(None))
    self.assertRaises(NotImplementedError, lambda: m.status())

# MemoryStorage.cancer()
class TestMemoryStorageCancer(unittest.TestCase):

  # check that we transmit calls to a store
  @patch('twitchcancer.storage.memorystorage.MemoryStorage.__init__', return_value=None)
  def test_transmit(self, init):
    m = MemoryStorage()
    m._store = MagicMock()

    m.cancer()

    m._store.cancer.assert_called_once_with()

# MemoryStorage.store()
class TestMemoryStorageStore(unittest.TestCase):

  # check that we transmit calls to a store
  @patch('twitchcancer.storage.memorystorage.MemoryStorage.__init__', return_value=None)
  def test_transmit(self, init):
    m = MemoryStorage()
    m._store = MagicMock()

    channel = "forsenlol"
    message = "message"
    m.store(channel, message)

    m._store.store.assert_called_once_with(channel, message)

# MemoryStorage._handle_cancer_request()
class TestMemoryStorageHandleCancerRequest(unittest.TestCase):

  # check that we respond to cancer requests with the current store.cancer() data
  @patch('twitchcancer.storage.memorystorage.MemoryStorage.__init__', return_value=None)
  def test_default(self, init):
    m = MemoryStorage()
    m._store = MagicMock()
    m._store.cancer = MagicMock(return_value="data")
    m.cancer_socket = MagicMock()
    m.cancer_socket.send_pyobj = MagicMock(side_effect=KeyboardInterrupt)

    try:
      m._handle_cancer_request()
    except KeyboardInterrupt:
      # the mock raises an exception to get out of the infinite loop
      pass

    # we should be listening for requests
    m.cancer_socket.recv.assert_called_once_with()

    # we should get data from the store
    m._store.cancer.assert_called_once_with()

    # we should respond to the request with the data we got
    m.cancer_socket.send_pyobj.assert_called_once_with("data")

# MemoryStorage._archive()
class TestMemoryStorageArchive(unittest.TestCase):

  # check that we transform data from the store to the socket correctly
  @patch('twitchcancer.storage.memorystorage.MemoryStorage.__init__', return_value=None)
  def test_formatting(self, init):
    m = MemoryStorage()
    m._store = MagicMock()
    m._store.archive = MagicMock(return_value={
        'foo': {
          'bar': {
            'cancer': 10,
            'messages': 20
          }
        }
    })

    m.pubsub_socket = MagicMock()

    m._archive()

    pickled = m.pubsub_socket.send_multipart.call_args[0][0][1]

    self.assertEqual(pickle.loads(pickled), {
      'date': 'foo',
      'channel': 'bar',
      'cancer': 10,
      'messages': 20
    })

  # check that we publish a leaderboard record for each channel for each minute
  @patch('twitchcancer.storage.memorystorage.MemoryStorage.__init__', return_value=None)
  def test_splitting(self, init):
    m = MemoryStorage()
    m._store = MagicMock()
    m._store.archive = MagicMock(return_value={
      'date1': {'foo': {'cancer': 0, 'messages': 0}, 'bar': {'cancer': 0, 'messages': 0}},
      'date2': {'foo': {'cancer': 0, 'messages': 0}, 'bar': {'cancer': 0, 'messages': 0}},
    })

    m.pubsub_socket = MagicMock()

    m._archive()

    self.assertEqual(m.pubsub_socket.send_multipart.call_count, 4)
