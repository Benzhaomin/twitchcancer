#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

# mongodb
import pymongo
from bson.code import Code
from bson.objectid import ObjectId

from twitchcancer.config import Config

'''
  Schema

  leaderboard {
    _id: "#channel",
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
      'date': date of the first record,
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

    logger.info('using mongodb://%s:%s/%s', Config.get('record.mongodb.host'), Config.get('record.mongodb.port'), self.db.name)

  # update db.leaderboard with this minute+channel record
  # @db.write
  def update_leaderboard(self, summary):
    new = self._history_to_leaderboard(summary)
    find_query = {'_id': new['_id']}

    record = self.db.leaderboard.find_one(find_query)

    # just insert new records
    if not record:
      logger.debug('inserting new leaderboard record for %s', new['_id'])
      self.db.leaderboard.insert_one(new)

    # compute update to existing records (new best score, totals, etc)
    else:
      logger.debug('updating %s leaderboard with summary %s', new['_id'], summary['date'])
      update_query = self._build_leaderboard_update_query(record, new)
      self.db.leaderboard.update(find_query, update_query)

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
        'average.cancer': (new['minute']['cancer']['value'] - record['average']['cancer']) / (record['average']['duration'] + 1),
        'average.messages': (new['minute']['messages']['value'] - record['average']['messages']) / (record['average']['duration'] + 1),
        'average.cpm': (new['minute']['cpm']['value'] - record['average']['cpm']) / (record['average']['duration'] + 1),
      },

      '$set': {
        'total.cpm': (record['total']['cancer'] + new['minute']['cancer']['value']) / (record['total']['messages'] + new['minute']['messages']['value']),
      }
    }

    # per minute records
    if new['minute']['cancer']['value'] > record['minute']['cancer']['value']:
      update['$set']['minute.cancer.value'] = new['minute']['cancer']['value']
      update['$set']['minute.cancer.date'] = new['minute']['cancer']['date']

      #logger.debug('new cancer pb for %s, %s, was %s', new['_id'], new['minute']['cancer'], record['minute']['cancer'])

    if new['minute']['messages']['value'] > record['minute']['messages']['value']:
      update['$set']['minute.messages.value'] = new['minute']['messages']['value']
      update['$set']['minute.messages.date'] = new['minute']['messages']['date']

      #logger.debug('new messages pb for %s, %s, was %s', new['_id'], new['minute']['messages'], record['minute']['messages'])

    if new['minute']['cpm']['value'] > record['minute']['cpm']['value']:
      update['$set']['minute.cpm.value'] = new['minute']['cpm']['value']
      update['$set']['minute.cpm.date'] = new['minute']['cpm']['date']

      #logger.debug('new cpm pb for %s, %s, was %s', new['_id'], new['minute']['cpm'], record['minute']['cpm'])

    return update

  # transforms an history record into a db.leaderboard record
  def _history_to_leaderboard(self, summary):
    (date, channel, cancer, messages) = (summary['date'], summary['channel'], summary['cancer'], summary['messages'])

    return {
      '_id': channel,
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
        'date': date,
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
  def leaderboards(self):
    metrics = ['cancer', 'messages', 'cpm']
    intervals = ['minute', 'average', 'total']

    result = {}

    for metric in metrics:
      result[metric] = {}

      for interval in intervals:
        result[metric][interval] = self.leaderboard(metric, interval)

    return result

  # returns one of the leaderboards
  # @db.read
  def leaderboard(self, what, per):

    if per == 'minute':
      # sort the leaderboard by interval and field
      sort = [("{0}.{1}.{2}".format(per, what, 'value'), pymongo.DESCENDING)]
      result = self.db.leaderboard.find().sort(sort).limit(10)

      return [{
        'channel': r["_id"],
        'date': r["minute"][what]["date"],
        'value': str(r["minute"][what]["value"]),
      } for r in result]

    elif per == 'total':
      # sort the leaderboard by interval and field
      sort = [("{0}.{1}".format(per, what), pymongo.DESCENDING)]
      result = self.db.leaderboard.find().sort(sort).limit(10)

      return [{
        'channel': r["_id"],
        'date': r["total"]["date"],
        'value': str(r["total"][what]),
      } for r in result]

    elif per == 'average':
      # sort the leaderboard by interval and field
      sort = [("{0}.{1}".format(per, what), pymongo.DESCENDING)]
      result = self.db.leaderboard.find().sort(sort).limit(10)

      return [{
        'channel': r["_id"],
        'date': r["total"]["date"],
        'value': str(r["average"][what]),
      } for r in result]

  # returns the rank of the value of a field
  # eg. minute.cancer = 1200 => rank = 3
  # @db.read
  def _leaderboard_rank(self, field, value):
    return self.db.leaderboard.find({field: {'$gte': value}}).count()

  # returns the personal records of a particular channel
  # @db.read
  def channel(self, channel):
    result = self.db.leaderboard.find_one({'_id': channel})

    if not result:
      return {}

    result['channel'] = result['_id']

    result['minute']['cancer']['rank'] = self._leaderboard_rank('minute.cancer.value', result['minute']['cancer']['value'])
    result['minute']['messages']['rank'] = self._leaderboard_rank('minute.messages.value', result['minute']['messages']['value'])
    result['minute']['cpm']['rank'] = self._leaderboard_rank('minute.cpm.value', result['minute']['cpm']['value'])

    result['total']['cancer'] = {
      'value': result['total']['cancer'],
      'rank': self._leaderboard_rank('total.cancer', result['total']['cancer'])
    }

    result['total']['messages'] = {
      'value': result['total']['messages'],
      'rank': self._leaderboard_rank('total.messages', result['total']['messages'])
    }

    result['total']['cpm'] = {
      'value': result['total']['cpm'],
      'rank': self._leaderboard_rank('total.cpm', result['total']['cpm'])
    }

    result['average']['cancer'] = {
      'value': result['average']['cancer'],
      'rank': self._leaderboard_rank('average.cancer', result['average']['cancer'])
    }

    result['average']['messages'] = {
      'value': result['average']['messages'],
      'rank': self._leaderboard_rank('average.messages', result['average']['messages'])
    }

    result['average']['cpm'] = {
      'value': result['average']['cpm'],
      'rank': self._leaderboard_rank('average.cpm', result['average']['cpm'])
    }

    return result
