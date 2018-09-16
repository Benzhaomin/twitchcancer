import collections
import logging
import pymongo

from twitchcancer.config import Config
from twitchcancer.storage.leaderboard import Leaderboard, LeaderboardBuilder
from twitchcancer.utils.timesplitter import TimeSplitter

logger = logging.getLogger(__name__)

'''
  Schema

  leaderboard {
    channel: "#channel",
    date: datetime (creation date),
    minute: {
      cancer: {
        'value': cancer points,
        'date': date achieved,
      },
      messages: {
        'value': message count,
        'date': date achieved,
      },
      cpm: {
        'value': cancer per message,
        'date': date achieved,
      },
    },
    total: {
      'cancer': cancer points,
      'messages': message count,
      'cpm': cancer per message,
    },
    average: {
      'duration': amount of minutes recorded,
      'cancer': cancer points,
      'messages': message count,
      'cpm': cancer per message,
    }
  }

  monthly_leaderboard {
    [see leaderboard]
  }

  daily_leaderboard {
    [see leaderboard]
  }
'''


# use MongoDB straight up
class PersistentStore:

    def __init__(self):
        super().__init__()

        client = pymongo.MongoClient(
            host=Config.get('record.mongodb.host'),
            port=int(Config.get('record.mongodb.port'))
        )

        self.db = client[Config.get('record.mongodb.database')]

        # unique index on channel + date
        # self.db.leaderboard.create_index()
        # self.db.monthly_leaderboard.create_index()
        # self.db.daily_leaderboard.create_index()

        # ease access to parallel collections
        self._collections = {
            'all': self.db.leaderboard,
            'monthly': self.db.monthly_leaderboard,
            'daily': self.db.daily_leaderboard,
        }

        logger.info('using mongodb://%s:%s/%s', Config.get('record.mongodb.host'), Config.get('record.mongodb.port'),
                    self.db.name)

    # update leaderboards with the new minute summary of a channel
    def update_leaderboard(self, summary):
        new = self._history_to_leaderboard(summary)

        # update the all-time leaderboard
        self._update_leaderboard('all', new)

        # update the monthly leaderboard
        new['date'] = TimeSplitter.month(summary['date'])
        self._update_leaderboard('monthly', new)

        # update the daily leaderboard
        new['date'] = TimeSplitter.day(summary['date'])
        self._update_leaderboard('daily', new)

    # update a leaderboard collection with the new record
    # @collection
    # @db.write
    def _update_leaderboard(self, name, new):
        collection = self._collections[name]

        find_query = {'channel': new['channel']}

        # the all-time leaderboard doesn't care about dates
        if name != 'all':
            find_query['date'] = new['date']

        # search for an existing leaderboard for that channel
        record = collection.find_one(find_query)

        # just insert new records
        if not record:
            collection.insert_one(new)
            logger.debug('inserted a new leaderboard record for %s', new['channel'])

        # compute update to existing records (new best score, totals, etc)
        else:
            update_query = self._build_leaderboard_update_query(record, new)
            collection.update_one(find_query, update_query)
            logger.debug('updating %s leaderboard with summary %s', new['channel'], new['date'])

    # prepare a mongo update query for a leaderboard document
    def _build_leaderboard_update_query(self, record, new):
        update = {
            '$inc': {
                # increment totals
                'total.cancer': new['minute']['cancer']['value'],
                'total.messages': new['minute']['messages']['value'],

                # add 1 minute to the duration
                'average.duration': 1,

                # update averages with the new weighted value
                'average.cancer': (new['minute']['cancer']['value'] - record['average']['cancer']) / (
                        record['average']['duration'] + 1),
                'average.messages': (new['minute']['messages']['value'] - record['average']['messages']) / (
                        record['average']['duration'] + 1),
                'average.cpm': (new['minute']['cpm']['value'] - record['average']['cpm']) / (
                        record['average']['duration'] + 1),
            },

            '$set': {
                'total.cpm': (record['total']['cancer'] + new['minute']['cancer']['value']) / (
                        record['total']['messages'] + new['minute']['messages']['value']),
            }
        }

        # per minute records
        if new['minute']['cancer']['value'] > record['minute']['cancer']['value']:
            update['$set']['minute.cancer.value'] = new['minute']['cancer']['value']
            update['$set']['minute.cancer.date'] = new['minute']['cancer']['date']

            # logger.debug('new cancer pb for %s, %s, was %s',
            # new['_id'], new['minute']['cancer'], record['minute']['cancer'])

        if new['minute']['messages']['value'] > record['minute']['messages']['value']:
            update['$set']['minute.messages.value'] = new['minute']['messages']['value']
            update['$set']['minute.messages.date'] = new['minute']['messages']['date']

            # logger.debug('new messages pb for %s, %s, was %s',
            # new['_id'], new['minute']['messages'], record['minute']['messages'])

        if new['minute']['cpm']['value'] > record['minute']['cpm']['value']:
            update['$set']['minute.cpm.value'] = new['minute']['cpm']['value']
            update['$set']['minute.cpm.date'] = new['minute']['cpm']['date']

            # logger.debug('new cpm pb for %s, %s, was %s',
            # new['_id'], new['minute']['cpm'], record['minute']['cpm'])

        return update

    # transforms an history record into a db.leaderboard record
    def _history_to_leaderboard(self, summary):
        (date, channel, cancer, messages) = (
            summary['date'], summary['channel'], summary['cancer'], summary['messages'])

        return {
            'channel': channel,
            'date': date,
            'minute': {
                'cancer': {
                    'value': cancer,
                    'date': date,
                },
                'messages': {
                    'value': messages,
                    'date': date,
                },
                'cpm': {
                    'value': cancer / messages,
                    'date': date,
                },
            },
            'total': {
                'cancer': cancer,
                'messages': messages,
                'cpm': cancer / messages,
            },
            'average': {
                'duration': 1,
                'cancer': cancer,
                'messages': messages,
                'cpm': cancer / messages,
            }
        }

    # returns all leaderboards
    def leaderboards(self, horizon="all"):
        result = collections.defaultdict(lambda: {})

        # retrieve each leaderboard for this horizon
        for leaderboard in LeaderboardBuilder.build(horizon=horizon):
            result[str(leaderboard)] = self._get_leaderboard(leaderboard)

        return result

    # returns one of the full leaderboards
    def leaderboard(self, name):
        leaderboard = LeaderboardBuilder.from_name(name)

        if not leaderboard:
            return []

        return self._get_leaderboard(leaderboard, 100)

    # returns one of the leaderboards
    # @db.read
    def _get_leaderboard(self, leaderboard, limit=10):
        collection = self._collections[leaderboard.horizon]

        # only look at records since the beginning of the leaderboard
        date = leaderboard.start_date()

        if date:
            query = {'date': {'$gte': date}}
        else:
            query = {}

        if leaderboard.interval == 'minute':
            # sort the leaderboard by interval and field
            sort = [("{0}.{1}.{2}".format(leaderboard.interval, leaderboard.metric, 'value'), pymongo.DESCENDING)]
            result = collection.find(query).sort(sort).limit(limit)

            return [{
                'channel': r["channel"],
                'date': r["minute"][leaderboard.metric]["date"],
                'value': str(r["minute"][leaderboard.metric]["value"]),
            } for r in result]

        elif leaderboard.interval == 'total':
            # sort the leaderboard by interval and field
            sort = [("{0}.{1}".format(leaderboard.interval, leaderboard.metric), pymongo.DESCENDING)]
            result = collection.find(query).sort(sort).limit(limit)

            return [{
                'channel': r["channel"],
                'date': r["date"],
                'value': str(r["total"][leaderboard.metric]),
            } for r in result]

        elif leaderboard.interval == 'average':
            # sort the leaderboard by interval and field
            sort = [("{0}.{1}".format(leaderboard.interval, leaderboard.metric), pymongo.DESCENDING)]
            result = collection.find(query).sort(sort).limit(limit)

            return [{
                'channel': r["channel"],
                'date': r["date"],
                'value': str(r["average"][leaderboard.metric]),
            } for r in result]

    # returns the rank of the value of a field
    # eg. minute.cancer = 1200 => rank = 3
    # @db.read
    # @collection
    def _leaderboard_rank(self, collection, field, value, date):
        query = {field: {'$gte': value}}

        if date is not None:
            query['date'] = {'$gte': date}

        return collection.count_documents(query)

    # returns the personal records of a particular channel
    # @db.read
    def channel(self, channel):
        return {
            'channel': channel,
            'all': self._channel(self._collections['all'], channel),
            'monthly': self._channel(self._collections['monthly'], channel,
                                     Leaderboard('monthly', None, None).start_date()),
            'daily': self._channel(self._collections['daily'], channel, Leaderboard('daily', None, None).start_date()),
        }

    # returns personnal records of a channel on one of the leaderboards
    def _channel(self, collection, channel, date=None):
        query = {'channel': channel}

        if date is not None:
            query['date'] = {'$gte': date}

        record = collection.find_one(query)

        if not record:
            return {}

        return {
            # best minute stats
            'minute': {
                'cancer': {
                    'value': record['minute']['cancer']['value'],
                    'date': record['minute']['cancer']['date'],
                    'rank': self._leaderboard_rank(collection, 'minute.cancer.value',
                                                   record['minute']['cancer']['value'], date)
                },
                'messages': {
                    'value': record['minute']['messages']['value'],
                    'date': record['minute']['messages']['date'],
                    'rank': self._leaderboard_rank(collection, 'minute.messages.value',
                                                   record['minute']['messages']['value'], date)
                },
                'cpm': {
                    'value': record['minute']['cpm']['value'],
                    'date': record['minute']['cpm']['date'],
                    'rank': self._leaderboard_rank(collection, 'minute.cpm.value', record['minute']['cpm']['value'],
                                                   date)
                },
            },

            # total stats
            'total': {
                'cancer': {
                    'value': record['total']['cancer'],
                    'rank': self._leaderboard_rank(collection, 'total.cancer', record['total']['cancer'], date)
                },
                'messages': {
                    'value': record['total']['messages'],
                    'rank': self._leaderboard_rank(collection, 'total.messages', record['total']['messages'], date)
                },
                'cpm': {
                    'value': record['total']['cpm'],
                    'rank': self._leaderboard_rank(collection, 'total.cpm', record['total']['cpm'], date)
                },
                'duration': {
                    'value': int(record['average']['duration']) * 60,  # minutes to seconds
                    'rank': self._leaderboard_rank(collection, 'average.duration', record['average']['duration'], date)
                },
                'since': record['date'],
            },

            # average stats
            'average': {
                'cancer': {
                    'value': record['average']['cancer'],
                    'rank': self._leaderboard_rank(collection, 'average.cancer', record['average']['cancer'], date)
                },
                'messages': {
                    'value': record['average']['messages'],
                    'rank': self._leaderboard_rank(collection, 'average.messages', record['average']['messages'], date)
                },
                'cpm': {
                    'value': record['average']['cpm'],
                    'rank': self._leaderboard_rank(collection, 'average.cpm', record['average']['cpm'], date)
                },
            },
        }

    # returns stats about the database
    def status(self):
        return {
            'all': self._status(self._collections['all']),
            'monthly': self._status(self._collections['monthly'], Leaderboard('monthly', None, None).start_date()),
            'daily': self._status(self._collections['daily'], Leaderboard('daily', None, None).start_date()),
        }

    # returns the status of a single collection, after a date if set
    # @db.read
    def _status(self, collection, date=None):
        query = []

        if date:
            query.append({
                '$match': {
                    'date': {'$gte': date},
                }
            })

        query.append({
            '$group': {
                '_id': 'null',
                'channels': {'$sum': 1},
                'messages': {'$sum': '$total.messages'},
                'cancer': {'$sum': '$total.cancer'}
            }
        })

        result = [r for r in collection.aggregate(query)]

        if result:
            result = result.pop()
            del result['_id']
            return result
        else:
            return {}

    # returns all the channels that look like name
    # @db.read
    def search(self, name):
        if not name:
            return []

        return [r['channel'] for r in self._collections['all'].find({
            'channel': {"$regex": '.*' + name.lower() + '.*'}
        })]
