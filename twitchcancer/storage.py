#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging
logger = logging.getLogger('twitchcancer.logger')

from bson.code import Code
from bson.objectid import ObjectId
import pymongo

import twitchcancer.cron

'''
  Schema

  messages {
    channel: "#channel",
    cancer: cancer points,
  }

  map_reduce {
    '_id': {
      date: beginning of the period,
      channel: "#channel",
    },
    'values': {
      cancer: cancer points,
      messages: message count
    }
  }

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
class Storage:

  def __init__(self, cron=False):
    super().__init__()

    client = pymongo.MongoClient()
    self.db = client.twitchcancer
    self.cron = None

    # update leaderboards every minute
    if cron:
      self.cron = twitchcancer.cron.Cron()
      self.cron.add(call=self._archive)
      self.cron.start()

  # update leaderboards from db.messages and ditch old messages
  def _archive(self):
    now = datetime.datetime.now(datetime.timezone.utc)
    logger.debug('[storage] archive started at %s', now)

    # only archive messages that are too old
    query = { '_id': {'$lte': self._live_message_objectId() } }

    # group message by channel+minute
    # map_reduce messages into { '_id': date, channel, 'values': cancer, messages }
    map_js = Code("function() {"
                  "  var coeff = 1000 * 60 * 1; " # group by minute
                  "  var roundTime = new Date(Math.floor(this._id.getTimestamp() / coeff) * coeff);"
                  "  var key = { 'channel': this.channel, 'date': roundTime };"
                  "  emit(key, { cancer: this.cancer, messages: 1 });"
                  "};")

    reduce_js = Code( "function(key, values) {"
                      "  var result = { cancer: 0, messages: 0};"
                      "  values.forEach(function(object) {"
                      "    result.cancer += object.cancer;"
                      "    result.messages += object.messages;"
                      "  });"
                      "  return result;"
                      "};")

    # aggregate old messages into db.history
    self.db.messages.map_reduce(map_js, reduce_js, {'replace': 'history'}, query=query)

    # update leaderboards with this new data
    result = self.db.history.find().sort([("id", pymongo.ASCENDING)])
    for r in result:
      self._update_leaderboard(self._history_to_leaderboard(r))

    # delete old messages
    self.db.messages.delete_many(query)

    logger.debug('[storage] archive finished at %s', datetime.datetime.now(datetime.timezone.utc))

  def _update_leaderboard(self, new):
    find = {'_id': new['_id']}
    record = self.db.leaderboard.find_one(find)

    if not record:
      logger.debug('[storage] inserting new leaderboard record for %s', new['_id'])
      self.db.leaderboard.insert_one(new)
    else:
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

        logger.debug('[storage] new cancer pb for %s, %s, was %s', new['_id'], new['minute']['cancer'], record['minute']['cancer'])

      if new['minute']['messages']['value'] > record['minute']['messages']['value']:
        update['$set']['minute.messages.value'] = new['minute']['messages']['value']
        update['$set']['minute.messages.date'] = new['minute']['messages']['date']

        logger.debug('[storage] new messages pb for %s, %s, was %s', new['_id'], new['minute']['messages'], record['minute']['messages'])

      if new['minute']['cpm']['value'] > record['minute']['cpm']['value']:
        update['$set']['minute.cpm.value'] = new['minute']['cpm']['value']
        update['$set']['minute.cpm.date'] = new['minute']['cpm']['date']

        logger.debug('[storage] new cpm pb for %s, %s, was %s', new['_id'], new['minute']['cpm'], record['minute']['cpm'])

      self.db.leaderboard.update(find, update)

  # transforms a db.history record into a db.leaderboard record, used as a poor-man's map/reduce
  def _history_to_leaderboard(self, r):
    return {
      '_id': r['_id']['channel'],
      'minute': {
        'cancer': {
          'value': r['value']['cancer'],
          'date': r['_id']['date'],
        },
        'messages': {
          'value': r['value']['messages'],
          'date': r['_id']['date'],
        },
        'cpm': {
          'value': r['value']['cancer'] / r['value']['messages'],
          'date': r['_id']['date'],
        },
      },
      'total': {
        'date': r['_id']['date'],
        'cancer': r['value']['cancer'],
        'messages': r['value']['messages'],
        'cpm': r['value']['cancer'] / r['value']['messages'],
      },
      'average': {
        'duration': 1,
        'cancer': r['value']['cancer'],
        'messages': r['value']['messages'],
        'cpm': r['value']['cancer'] / r['value']['messages'],
      }
    }

  # returns a JSON data point from an aggregated db.message record
  def _point_from_aggregate(self, message):
    return {
      'channel': message['_id'],
    #  'date': str(self._live_message_breakpoint()),
      'cancer': message['cancer'],
      'messages': message['messages'],
    }

  # returns the datetime where live and archived messages split
  def _live_message_breakpoint(self):
    # messages are old and ready to be archived after 1 minute
    return datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=1)

  # returns the live message breakpoint as a MongoDB objectId
  def _live_message_objectId(self):
    return ObjectId.from_datetime(self._live_message_breakpoint())

  # store a cancer level for a single message in a channel
  def store(self, channel, cancer):
    message = {
      'channel': channel,
      'cancer': int(cancer)
    }

    self.db.messages.insert_one(message)
    #logger.debug('[storage] inserting %s %s', message['channel'], message['cancer'])

  # returns current cancer levels
  def cancer(self):
    pipeline = [{
      "$match": {
        '_id': {'$gte': self._live_message_objectId() }
      }
    }, {
      "$group": {
        "_id": "$channel",
        "cancer": {"$sum": "$cancer"},
        "messages": {"$sum": 1}
      }
    }, {
      "$sort": {
        "_id": 1
      }
    }]

    result = self.db.messages.aggregate(pipeline)

    return [self._point_from_aggregate(c) for c in result]

  def leaderboard(self, what, per):

    if per == 'minute':
      # sort the leaderboard by interval and field
      sort = [("{0}.{1}.{2}".format(per, what, 'value'), pymongo.DESCENDING)]
      result = self.db.leaderboard.find().sort(sort).limit(10)

      return [{
        'channel': r["_id"],
        'date': str(r["minute"][what]["date"]),
        'value': str(r["minute"][what]["value"]),
      } for r in result]

    elif per == 'total':
      # sort the leaderboard by interval and field
      sort = [("{0}.{1}".format(per, what), pymongo.DESCENDING)]
      result = self.db.leaderboard.find().sort(sort).limit(10)

      return [{
        'channel': r["_id"],
        'date': str(r["total"]["date"]),
        'value': str(r["total"][what]),
      } for r in result]

    elif per == 'average':
      # sort the leaderboard by interval and field
      sort = [("{0}.{1}".format(per, what), pymongo.DESCENDING)]
      result = self.db.leaderboard.find().sort(sort).limit(10)

      return [{
        'channel': r["_id"],
        'date': str(r["total"]["date"]),
        'value': str(r["average"][what]),
      } for r in result]

import time

if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG)

  store = Storage()
  result = store.db.history.find().sort([("id", pymongo.ASCENDING)])
  for r in result:
    store._update_leaderboard(store._history_to_leaderboard(r))
