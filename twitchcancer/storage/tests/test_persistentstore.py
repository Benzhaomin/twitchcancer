import datetime
import pymongo
import unittest
from unittest.mock import patch, MagicMock

from twitchcancer.config import Config
from twitchcancer.storage.persistentstore import PersistentStore


# PersistentStore using a test database
class TestingDatabasePersistentStore(PersistentStore):
    def __init__(self, db):
        self.db = db

        self._collections = {
            'all': self.db.leaderboard,
            'monthly': self.db.monthly_leaderboard,
            'daily': self.db.daily_leaderboard,
        }


# sets up and tears down a mongodb database to run tests on
class TestPersistentStoreUsingDB(unittest.TestCase):
    database_name = "twitchcancer_tests"

    def setUp(self):
        try:
            self.client = pymongo.MongoClient(
                host=Config.get('record.mongodb.host'),
                port=int(Config.get('record.mongodb.port')),
                connectTimeoutMS=100,
                serverSelectionTimeoutMS=100)
            self.client.server_info()
            self.db = self.client[self.database_name]
        except pymongo.errors.ServerSelectionTimeoutError:
            raise unittest.SkipTest("couldn't connect to a test database at mongodb://localhost:27017/")

    def tearDown(self):
        if self.db:
            self.client.drop_database(self.database_name)

    def get_test_store(self):
        store = TestingDatabasePersistentStore(self.db)

        for collection in store._collections.values():
            collection.drop()

        return store


# sets up a mock database
class TestPersistentStoreUsingMock(unittest.TestCase):

    @patch('twitchcancer.storage.persistentstore.PersistentStore.__init__', return_value=None)
    def setUp(self, init):
        self.store = PersistentStore()
        self.store.db = MagicMock()


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
class TestPersistentStoreLeaderboards(TestPersistentStoreUsingMock):

    # check that we get a summary of all the leaderboards
    @patch('twitchcancer.storage.persistentstore.PersistentStore._get_leaderboard', return_value=[])
    def test_all_leaderboards(self, get_leaderboard):
        result = self.store.leaderboards()

        expected = {
            'all.cancer.minute': [],
            'all.cancer.average': [],
            'all.cancer.total': [],

            'all.messages.minute': [],
            'all.messages.average': [],
            'all.messages.total': [],

            'all.cpm.minute': [],
            'all.cpm.total': [],
        }

        self.assertEqual(result, expected)
        self.assertEqual(get_leaderboard.call_count, 8)


# PersistentStore.leaderboard()
class TestPersistentStoreLeaderboard(TestPersistentStoreUsingMock):

    # check that an unknown leaderboard is empty
    @patch('twitchcancer.storage.persistentstore.PersistentStore._get_leaderboard')
    def test_unknown_leaderboard(self, get_leaderboard):
        result = self.store.leaderboard("foo")

        self.assertEqual(result, [])
        self.assertFalse(get_leaderboard.called)

    # check that an known leaderboard is correctly requested from _get_leaderboard
    @patch('twitchcancer.storage.persistentstore.PersistentStore._get_leaderboard', return_value="foo")
    def test_known_leaderboard(self, get_leaderboard):
        result = self.store.leaderboard('all.cancer.total')

        self.assertEqual(result, "foo")


# PersistentStore.update_leaderboard()
# PersistentStore._build_leaderboard_update_query()
# PersistentStore._history_to_leaderboard()
# PersistentStore.leaderboard()
# PersistentStore._get_leaderboard()
class TestPersistentStoreLeaderboardUsingDB(TestPersistentStoreUsingDB):

    # check that adding and querying for a leaderboard works correctly
    def test_daily(self):
        p = self.get_test_store()

        channel = "channel"
        yesterday = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0) - datetime.timedelta(days=1)
        today = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)

        # not part of today's leaderboard
        p.update_leaderboard({'date': yesterday, 'channel': channel, 'cancer': 30, 'messages': 40})

        # should be the one and only record
        p.update_leaderboard({'date': today, 'channel': channel, 'cancer': 5, 'messages': 50})

        yesterday = yesterday.replace(tzinfo=None)
        today = today.replace(tzinfo=None)
        start_date = start_date.replace(tzinfo=None)

        expected = [{'channel': channel, 'date': today, 'value': '5'}]

        actual = p.leaderboard("daily.cancer.minute")

        self.assertEqual(actual, expected)

    # check that older records aren't picked up
    def test_daily_no_result(self):
        p = self.get_test_store()

        channel = "channel"
        yesterday = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0) - datetime.timedelta(days=1)

        # not part of today's leaderboard
        p.update_leaderboard({'date': yesterday, 'channel': channel, 'cancer': 30, 'messages': 40})

        expected = []
        actual = p.leaderboard("daily.cancer.minute")

        self.assertEqual(actual, expected)


# PersistentStore._get_leaderboard()
class TestPersistentStoreGetLeaderboard(unittest.TestCase):
    pass


# PersistentStore.update_leaderboard()
# PersistentStore._build_leaderboard_update_query()
# PersistentStore._history_to_leaderboard()
# PersistentStore.leaderboards()
# PersistentStore._get_leaderboard()
class TestPersistentStoreLeaderboardsUsingDB(TestPersistentStoreUsingDB):

    # check that adding and querying for the all leaderboard works correctly
    def test_all(self):
        p = self.get_test_store()

        channel = "channel"
        now1 = datetime.datetime(2015, 9, 1).replace(microsecond=0)
        now2 = now1 + datetime.timedelta(days=10)

        p.update_leaderboard({'date': now1, 'channel': channel, 'cancer': 30, 'messages': 40})
        p.update_leaderboard({'date': now2, 'channel': channel, 'cancer': 5, 'messages': 50})

        expected = {
            'all.cancer.minute': [{'channel': channel, 'date': now1, 'value': '30'}],
            'all.cancer.average': [{'channel': channel, 'date': now1, 'value': '17.5'}],
            'all.cancer.total': [{'channel': channel, 'date': now1, 'value': '35'}],

            'all.messages.minute': [{'channel': channel, 'date': now2, 'value': '50'}],
            'all.messages.average': [{'channel': channel, 'date': now1, 'value': '45.0'}],
            'all.messages.total': [{'channel': channel, 'date': now1, 'value': '90'}],

            'all.cpm.minute': [{'channel': channel, 'date': now1, 'value': '0.75'}],
            'all.cpm.total': [{'channel': channel, 'date': now1, 'value': str(35 / 90)}],
        }

        actual = p.leaderboards()

        # lay all sub-dict out to ease debugging when one fails
        def compare(this, that, key):
            self.assertEqual(this[key], that[key])

        compare(actual, expected, 'all.cancer.minute')
        compare(actual, expected, 'all.cancer.average')
        compare(actual, expected, 'all.cancer.total')
        compare(actual, expected, 'all.messages.minute')
        compare(actual, expected, 'all.messages.average')
        compare(actual, expected, 'all.messages.total')
        compare(actual, expected, 'all.cpm.minute')
        compare(actual, expected, 'all.cpm.total')

    # check that adding and querying for leaderboards works correctly
    def test_monthly(self):
        p = self.get_test_store()

        channel = "channel"
        now1 = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=34)
        now2 = datetime.datetime.now(datetime.timezone.utc).replace(hour=1, microsecond=0)
        start_date = now2.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # not part of this month's leaderboard
        p.update_leaderboard({'date': now1, 'channel': channel, 'cancer': 30, 'messages': 40})

        # should be the one and only record
        p.update_leaderboard({'date': now2, 'channel': channel, 'cancer': 5, 'messages': 50})

        now1 = now1.replace(tzinfo=None)
        now2 = now2.replace(tzinfo=None)
        start_date = start_date.replace(tzinfo=None)

        expected = {
            'monthly.cancer.minute': [{'channel': channel, 'date': now2, 'value': '5'}],
            'monthly.cancer.average': [{'channel': channel, 'date': start_date, 'value': '5'}],
            'monthly.cancer.total': [{'channel': channel, 'date': start_date, 'value': '5'}],

            'monthly.messages.minute': [{'channel': channel, 'date': now2, 'value': '50'}],
            'monthly.messages.average': [{'channel': channel, 'date': start_date, 'value': '50'}],
            'monthly.messages.total': [{'channel': channel, 'date': start_date, 'value': '50'}],

            'monthly.cpm.minute': [{'channel': channel, 'date': now2, 'value': str(5 / 50)}],
            'monthly.cpm.total': [{'channel': channel, 'date': start_date, 'value': str(5 / 50)}],
        }

        actual = p.leaderboards("monthly")

        # lay all sub-dict out to ease debugging when one fails
        def compare(this, that, key):
            self.assertEqual(this[key], that[key])

        compare(actual, expected, 'monthly.cancer.minute')
        compare(actual, expected, 'monthly.cancer.average')
        compare(actual, expected, 'monthly.cancer.total')
        compare(actual, expected, 'monthly.messages.minute')
        compare(actual, expected, 'monthly.messages.average')
        compare(actual, expected, 'monthly.messages.total')
        compare(actual, expected, 'monthly.cpm.minute')
        compare(actual, expected, 'monthly.cpm.total')

    # check that adding and querying for leaderboards works correctly
    def test_daily(self):
        p = self.get_test_store()

        channel = "channel"
        now1 = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0) - datetime.timedelta(days=1)
        now2 = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
        start_date = now2.replace(hour=0, minute=0, second=0, microsecond=0)

        # not part of this month's leaderboard
        p.update_leaderboard({'date': now1, 'channel': channel, 'cancer': 30, 'messages': 40})

        # should be the one and only record
        p.update_leaderboard({'date': now2, 'channel': channel, 'cancer': 5, 'messages': 50})

        now1 = now1.replace(tzinfo=None)
        now2 = now2.replace(tzinfo=None)
        start_date = start_date.replace(tzinfo=None)

        expected = {
            'daily.cancer.minute': [{'channel': channel, 'date': now2, 'value': '5'}],
            'daily.cancer.average': [{'channel': channel, 'date': start_date, 'value': '5'}],
            'daily.cancer.total': [{'channel': channel, 'date': start_date, 'value': '5'}],

            'daily.messages.minute': [{'channel': channel, 'date': now2, 'value': '50'}],
            'daily.messages.average': [{'channel': channel, 'date': start_date, 'value': '50'}],
            'daily.messages.total': [{'channel': channel, 'date': start_date, 'value': '50'}],

            'daily.cpm.minute': [{'channel': channel, 'date': now2, 'value': str(5 / 50)}],
            'daily.cpm.total': [{'channel': channel, 'date': start_date, 'value': str(5 / 50)}],
        }

        actual = p.leaderboards("daily")

        # lay all sub-dict out to ease debugging when one fails
        def compare(this, that, key):
            self.assertEqual(this[key], that[key])

        compare(actual, expected, 'daily.cancer.minute')
        compare(actual, expected, 'daily.cancer.average')
        compare(actual, expected, 'daily.cancer.total')
        compare(actual, expected, 'daily.messages.minute')
        compare(actual, expected, 'daily.messages.average')
        compare(actual, expected, 'daily.messages.total')
        compare(actual, expected, 'daily.cpm.minute')
        compare(actual, expected, 'daily.cpm.total')


# PersistentStore._leaderboard_rank()
class TestPersistentStoreLeaderboardRank(unittest.TestCase):
    pass


# PersistentStore.channel()
class TestPersistentStoreChannel(unittest.TestCase):
    pass


# PersistentStore._leaderboard_rank()
# PersistentStore.channel()
class TestPersistentStoreChannelUsingDB(TestPersistentStoreUsingDB):

    # check that adding records and querying for channel stats works correctly
    def test_using_db(self):
        p = self.get_test_store()

        channel = "channel"
        old = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0) - datetime.timedelta(days=31)
        month = datetime.datetime.now(datetime.timezone.utc).replace(day=1, microsecond=0)
        today = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)

        p.update_leaderboard({'date': old, 'channel': channel, 'cancer': 8, 'messages': 2})
        p.update_leaderboard({'date': month, 'channel': channel, 'cancer': 4, 'messages': 4})
        p.update_leaderboard({'date': today, 'channel': channel, 'cancer': 2, 'messages': 8})

        old = old.replace(tzinfo=None)
        month = month.replace(tzinfo=None)
        today = today.replace(tzinfo=None)

        expected = {
            'channel': channel,
            'all': {
                'minute': {
                    'cancer': {'value': 8, 'date': old, 'rank': 1},
                    'messages': {'value': 8, 'date': today, 'rank': 1},
                    'cpm': {'value': 8 / 2, 'date': old, 'rank': 1},
                },
                'total': {
                    'cancer': {'value': 14, 'rank': 1},
                    'messages': {'value': 14, 'rank': 1},
                    'cpm': {'value': 1.0, 'rank': 1},
                    'duration': {'value': 3 * 60, 'rank': 1},
                    'since': old
                },
                'average': {
                    'cancer': {'value': 14 / 3, 'rank': 1},
                    'messages': {'value': 14 / 3, 'rank': 1},
                    'cpm': {'value': (8 / 2 + 4 / 4 + 2 / 8) / 3, 'rank': 1}
                }
            },
            'monthly': {
                'minute': {
                    'cancer': {'value': 4, 'date': month, 'rank': 1},
                    'messages': {'value': 8, 'date': today, 'rank': 1},
                    'cpm': {'value': 1.0, 'date': month, 'rank': 1},
                },
                'total': {
                    'cancer': {'value': 6, 'rank': 1},
                    'messages': {'value': 12, 'rank': 1},
                    'cpm': {'value': 6 / 12, 'rank': 1},
                    'duration': {'value': 2 * 60, 'rank': 1},
                    'since': month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                },
                'average': {
                    'cancer': {'value': 6 / 2, 'rank': 1},
                    'messages': {'value': 12 / 2, 'rank': 1},
                    'cpm': {'value': (1 + 2 / 8) / 2, 'rank': 1}
                }
            },
            'daily': {
                'minute': {
                    'cancer': {'value': 2, 'date': today, 'rank': 1},
                    'messages': {'value': 8, 'date': today, 'rank': 1},
                    'cpm': {'value': 2 / 8, 'date': today, 'rank': 1},
                },
                'total': {
                    'cancer': {'value': 2, 'rank': 1},
                    'messages': {'value': 8, 'rank': 1},
                    'cpm': {'value': 2 / 8, 'rank': 1},
                    'duration': {'value': 60, 'rank': 1},
                    'since': today.replace(hour=0, minute=0, second=0, microsecond=0)
                },
                'average': {
                    'cancer': {'value': 2, 'rank': 1},
                    'messages': {'value': 8, 'rank': 1},
                    'cpm': {'value': 2 / 8, 'rank': 1}
                }
            }
        }

        actual = p.channel(channel)

        # lay all sub-dict out to ease debugging when one fails
        def compare(this, that, key1, key2):
            self.assertEqual(this[key1][key2], that[key1][key2])

        self.assertEqual(actual['channel'], expected['channel'])
        compare(actual, expected, 'all', 'minute')
        compare(actual, expected, 'all', 'average')
        compare(actual, expected, 'all', 'total')
        compare(actual, expected, 'monthly', 'minute')
        compare(actual, expected, 'monthly', 'average')
        compare(actual, expected, 'monthly', 'total')
        compare(actual, expected, 'daily', 'minute')
        compare(actual, expected, 'daily', 'average')
        compare(actual, expected, 'daily', 'total')


# PersistentStore.status()
class TestPersistentStoreStatus(unittest.TestCase):
    pass


# PersistentStore.status()
class TestPersistentStoreStatusUsingDB(TestPersistentStoreUsingDB):

    # check that adding records and querying for the overall status works correctly
    def test_using_db(self):
        p = self.get_test_store()

        channel = "channel"
        old = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=31)
        month = datetime.datetime.now(datetime.timezone.utc).replace(day=1)
        today = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)

        p.update_leaderboard({'date': old, 'channel': channel, 'cancer': 3, 'messages': 10})
        p.update_leaderboard({'date': month, 'channel': channel, 'cancer': 5, 'messages': 20})
        p.update_leaderboard({'date': today, 'channel': channel, 'cancer': 10, 'messages': 30})

        expected = {
            'all': {
                'channels': 1,
                'messages': 60,
                'cancer': 18
            },
            'monthly': {
                'channels': 1,
                'messages': 50,
                'cancer': 15
            },
            'daily': {
                'channels': 1,
                'messages': 30,
                'cancer': 10
            },
        }

        actual = p.status()

        self.assertEqual(actual, expected)


# PersistentStore.search()
class TestPersistentStoreSearch(TestPersistentStoreUsingMock):
    pass


# PersistentStore.search()
class TestPersistentStoreSearchUsingDB(TestPersistentStoreUsingDB):

    # check that searching for channels works correctly
    def test_using_db(self):
        p = self.get_test_store()

        channel = "foobar"
        now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)

        p.update_leaderboard({'date': now, 'channel': channel, 'cancer': 30, 'messages': 40})

        expected = [channel]

        self.assertEqual(p.search('foo'), expected)
        self.assertEqual(p.search('Foo'), expected)
        self.assertEqual(p.search('oo'), expected)
        self.assertEqual(p.search('barfoo'), [])
        self.assertEqual(p.search(None), [])
