import unittest
from unittest.mock import patch, MagicMock

from twitchcancer.storage.readonlystorage import ReadOnlyStorage


# ReadOnlyStorage.*()
class TestReadOnlyStorageNotImplemented(unittest.TestCase):

    # check that we don't answer calls we can't answer
    @patch('twitchcancer.storage.readonlystorage.ReadOnlyStorage.__init__', return_value=None)
    def test_not_implemented(self, init):
        r = ReadOnlyStorage()

        self.assertRaises(NotImplementedError, lambda: r.record())
        self.assertRaises(NotImplementedError, lambda: r.store(None, None))


# ReadOnlyStorage.cancer()
class TestReadOnlyStorageCancer(unittest.TestCase):

    # check that we request cancer from a live message store
    @patch('twitchcancer.storage.readonlystorage.ReadOnlyStorage.__init__', return_value=None)
    def test_request(self, init):
        r = ReadOnlyStorage()
        r.socket = MagicMock()
        r.socket.recv_pyobj = MagicMock(return_value="data")
        r.poller = MagicMock()

        result = r.cancer()

        self.assertEqual(result, "data")

    # check that we gracefully fail if the message store doesn't reply
    @patch('twitchcancer.storage.readonlystorage.ReadOnlyStorage.__init__', return_value=None)
    @patch('twitchcancer.storage.readonlystorage.ReadOnlyStorage._disconnect')
    @patch('twitchcancer.storage.readonlystorage.ReadOnlyStorage._connect')
    def test_fail(self, connect, disconnect, init):
        r = ReadOnlyStorage()
        r.socket = MagicMock()
        r.poller = MagicMock()
        r.poller.poll = MagicMock(return_value=False)

        result = r.cancer()

        self.assertEqual(result, [])
        self.assertEqual(connect.call_count, 1)
        self.assertEqual(disconnect.call_count, 1)


# ReadOnlyStorage.leaderboards()
class TestReadOnlyStorageLeaderboards(unittest.TestCase):

    # check that we transmit the call to a store
    @patch('twitchcancer.storage.readonlystorage.ReadOnlyStorage.__init__', return_value=None)
    def test_default(self, init):
        r = ReadOnlyStorage()
        r._store = MagicMock()
        r._store.leaderboards = MagicMock(return_value="data")

        result = r.leaderboards("foo")

        self.assertEqual(result, "data")
        r._store.leaderboards.assert_called_once_with("foo")


# ReadOnlyStorage.leaderboard()
class TestReadOnlyStorageLeaderboard(unittest.TestCase):

    # check that we transmit the call to a store
    @patch('twitchcancer.storage.readonlystorage.ReadOnlyStorage.__init__', return_value=None)
    def test_default(self, init):
        r = ReadOnlyStorage()
        r._store = MagicMock()
        r._store.leaderboard = MagicMock(return_value="data")

        result = r.leaderboard("foo")

        self.assertEqual(result, "data")
        self.assertEqual(r._store.leaderboard.call_count, 1)


# ReadOnlyStorage.channel()
class TestReadOnlyStorageChannel(unittest.TestCase):

    # check that we transmit the call to a store
    @patch('twitchcancer.storage.readonlystorage.ReadOnlyStorage.__init__', return_value=None)
    def test_default(self, init):
        r = ReadOnlyStorage()
        r._store = MagicMock()
        r._store.channel = MagicMock(return_value="data")

        result = r.channel("channel")

        self.assertEqual(result, "data")
        r._store.channel.assert_called_once_with("channel")


# ReadOnlyStorage.status()
class TestReadOnlyStorageStatus(unittest.TestCase):

    # check that we return historical stats and live status correctly
    @patch('twitchcancer.storage.readonlystorage.ReadOnlyStorage.__init__', return_value=None)
    def test_default(self, init):
        r = ReadOnlyStorage()
        r._store = MagicMock()
        r._store.status = MagicMock(return_value={
            'channels': 1,
            'messages': 2,
            'cancer': 3,
        })
        r.cancer = MagicMock(return_value=[
            {
                'messages': 1,
                'cancer': 2
            },
            {
                'messages': 3,
                'cancer': 4
            },
        ])

        expected = {
            'total': {
                'channels': 1,
                'messages': 2,
                'cancer': 3,
            },
            'live': {
                'channels': 2,
                'messages': 4,
                'cancer': 6,
            }
        }

        result = r.status()

        self.assertEqual(result, expected)

    # check that we gracefully fail if we don't get live data
    @patch('twitchcancer.storage.readonlystorage.ReadOnlyStorage.__init__', return_value=None)
    @patch('twitchcancer.storage.readonlystorage.ReadOnlyStorage.cancer', return_value=[])
    def test_fail(self, cancer, init):
        r = ReadOnlyStorage()
        r._store = MagicMock()
        r._store.status = MagicMock(return_value={
            'channels': 1,
            'messages': 2,
            'cancer': 3,
        })

        expected = {
            'total': {
                'channels': 1,
                'messages': 2,
                'cancer': 3,
            },
            'live': {
                'channels': 0,
                'messages': 0,
                'cancer': 0,
            }
        }

        result = r.status()

        self.assertEqual(result, expected)


# ReadOnlyStorage.search()
class TestReadOnlyStorageSearch(unittest.TestCase):

    # check that we transmit the call to a store
    @patch('twitchcancer.storage.readonlystorage.ReadOnlyStorage.__init__', return_value=None)
    def test_default(self, init):
        r = ReadOnlyStorage()
        r._store = MagicMock()
        r._store.search = MagicMock(return_value="data")

        result = r.search("foo")

        self.assertEqual(result, "data")
        self.assertEqual(r._store.search.call_count, 1)


# ReadOnlyStorage._connect()
class TestReadOnlyStorageConnect(unittest.TestCase):
    pass


# ReadOnlyStorage._disconnect()
class TestReadOnlyStorageDisconnect(unittest.TestCase):
    pass
