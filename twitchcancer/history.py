#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging
logger = logging.getLogger('twitchcancer.logger')

from bson.code import Code
from pymongo import MongoClient
client = MongoClient()
db = client.twitchcancer

from bottle import Bottle, route, request, response, run
app = Bottle()

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

  #messages = [{m['date'].timestamp(): m['cancer']} for m in db.messages.find()]
  #for m in messages:
  #  print(m)
  #return {}

  query = {"channel": '#'+channel}

  map_js = Code("function() {"
                "  var coeff = 1000 * 60 * " + str(interval) + "; "
                "  var roundTime = new Date(Math.floor(this.date.getTime() / coeff) * coeff);"
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

  result = db.messages.map_reduce(map_js, reduce_js, "intervalled", query=query)

  history = [{str(m['_id']): m['value']} for m in result.find()]

  return {'history': history}

def history(args):
  run(app, host=args.host, port=int(args.port)) #, debug=(numeric_level==logging.DEBUG)
