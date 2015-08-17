#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import json
import logging
logger = logging.getLogger(__name__)

from bottle import Bottle, JSONPlugin, install, route, request, response, run
app = Bottle(autojson=False)
app.install(JSONPlugin(json_dumps=lambda s: json.dumps(s, cls=DatetimeJSONEncoder)))

from twitchcancer.storage import Storage
storage = Storage()

@app.hook('after_request')
def enable_cors():
  response.headers['Access-Control-Allow-Origin'] = '*'
  response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
  response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

# returns cancer level of
@app.route(path="/live", method="GET")
#@app.route(path="/live/<channels>", method="GET")
def cancer():
  result = storage.cancer()

  return {'channels': result}

# returns all-time leaderboards
@app.route(path="/leaderboards", method="GET")
def leaderboards():
  metrics = ['cancer', 'messages', 'cpm']
  intervals = ['minute', 'average', 'total']

  result = {}

  for metric in metrics:
    result[metric] = {}

    for interval in intervals:
      result[metric][interval] = storage.leaderboard(metric, interval)

  return result

# returns the records of a channel
@app.route(path="/channel/<channel>", method="GET")
def channel(channel):
  channel = '#'+channel

  return storage.channel(channel)

class DatetimeJSONEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, datetime.datetime):
      return obj.isoformat()
    return JSONEncoder.default(self, obj)

def history(args):

  run(app, host=args.host, port=int(args.port)) #, debug=(numeric_level==logging.DEBUG)
