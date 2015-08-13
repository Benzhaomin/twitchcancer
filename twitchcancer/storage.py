#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging
logger = logging.getLogger('twitchcancer.logger')

from bson.code import Code
from bson.objectid import ObjectId
from pymongo import MongoClient

# use MongoDB straight up
class Storage:

  def __init__(self):
    super().__init__()

    client = MongoClient()
    self.db = client.twitchcancer

  def store(self, channel, cancer):
    message = {
      'channel': channel,
      'cancer': cancer
    }

    self.db.messages.insert_one(message)
    logger.debug('[storage] inserting %s %s', message['channel'], message['cancer'])

  def history(self, parameters):
    query = parameters['query']
    interval = parameters['interval']

    # apply date comparison using the object ID instead of a date field
    if 'date' in query:
      query['date']['$gt'] = ObjectId.from_datetime(query['date']['$gt'])
      query['_id'] = query['date']
      del query['date']

    map_js = Code("function() {"
                  "  var coeff = 1000 * 60 * " + str(interval) + "; "
                  "  var roundTime = new Date(Math.floor(this._id.getTimestamp() / coeff) * coeff);"
                  "  emit(roundTime, { cancer: (this.cancer ? 1 : 0), total: 1 });"
                  "};")

    reduce_js = Code( "function(key, values) {"
                      "  var result = { cancer: 0, total: 0};"
                      "  values.forEach(function(object) {"
                      "    result.cancer += object.cancer;"
                      "    result.total += object.total;"
                      "  });"
                      "  return result;"
                      "};")

    result = self.db.messages.map_reduce(map_js, reduce_js, "intervalled", query=query)
    logger.debug('[storage] retrieved history for %s with a %s minutes interval', query['channel'], interval)

    return [{str(m['_id']): m['value']} for m in result.find()]
