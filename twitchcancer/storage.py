#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging
logger = logging.getLogger('twitchcancer.logger')

from bson.code import Code
from bson.objectid import ObjectId
from pymongo import MongoClient

import twitchcancer.cron

'''
  Schema

  messages {
    channel: "#channel",
    cancer: cancer points,
  }

  history {
    '_id': {
      date: beginning of the period,
      channel: "#channel",
    },
    'values': {
      cancer: cancer points,
      messages: message count
    }
  }

'''
# use MongoDB straight up
class Storage:

  def __init__(self, cron=False):
    super().__init__()

    client = MongoClient()
    self.db = client.twitchcancer
    self.cron = None

    # archive old messages every minute
    if cron:
      self.cron = twitchcancer.cron.Cron()
      self.cron.add(call=self._archive)
      self.cron.start()

  # consolidate and archive db.messages data into db.history
  def _archive(self):
    now = datetime.datetime.now(datetime.timezone.utc)
    logger.debug('[storage] archive started at %s', now)

    # only archive messages that are too old
    query = { '_id': {'$lte': self._live_message_objectId() } }

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

    # db.messages -> m/r (merge) -> db.history
    self.db.messages.map_reduce(map_js, reduce_js, {'reduce': 'history'}, query=query)

    # delete archived messages
    self.db.messages.delete_many(query)

    logger.debug('[storage] archive finished at %s', datetime.datetime.now(datetime.timezone.utc))

  # returns a JSON data point object from a db.history record
  def _point_from_history(self, history):
    return {
    #  'channel': history['_id']['channel'],
      'date': str(history['_id']['date']),
      'cancer': history['value']['cancer'],
      'messages': int(history['value']['messages'])
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

  # returns the cancer history of a channel
  def history(self, channel):
    query = {"_id.channel": channel}
    result = self.db.history.find(query)

    return [self._point_from_history(p) for p in result]

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

import time

if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG)

  store = Storage(True)
  while True:
    time.sleep(60)
