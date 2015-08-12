#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging
logger = logging.getLogger('twitchcancer.logger')

from bottle import Bottle, route, request, response, run
app = Bottle()

from twitchcancer.storage import Storage
storage = Storage()

@app.hook('after_request')
def enable_cors():
  response.headers['Access-Control-Allow-Origin'] = '*'
  response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
  response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

@app.route(path="/history/<channel>", method="GET")
# curl http://localhost:8080/history/forsenlol
# curl http://localhost:8080/history/forsenlol?interval=60
def message(channel):
  try:
    interval = int(request.query.interval)
  except:
    interval = 5

  query = {"channel": '#'+channel}

  history = storage.history({'query': query, 'interval': interval})

  return {'history': history}

# returns cancer level of
@app.route(path="/cancer/<channels>", method="GET")
def cancer(channels):
  try:
    horizon = int(request.query.horizon)
  except:
    horizon = 60

  stats = []

  for channel in channels.split('|'):
    query = {
      "channel": '#'+channel,
      "date": { "$gt" : datetime.datetime.utcnow() - datetime.timedelta(minutes=horizon) }
    }
    history = storage.history({'query': query, 'interval': horizon})

    # compute a global cancer level on the period
    try:
      cancer = sum([list(x.values())[0]['cancer'] for x in history]) / sum([list(x.values())[0]['total'] for x in history])
    except ZeroDivisionError:
      cancer = 0

    stats.append({channel: cancer})

  return {'channels': stats}

def history(args):
  run(app, host=args.host, port=int(args.port)) #, debug=(numeric_level==logging.DEBUG)
