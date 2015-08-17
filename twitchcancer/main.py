#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import logging
logger = logging.getLogger('twitchcancer')

import twitchcancer.cure
import twitchcancer.monitor
import twitchcancer.api.api
from twitchcancer.diagnosis import Diagnosis
from twitchcancer.source.twitch import Twitch
from twitchcancer.source.log import Log

def _get_source(channel):
  if channel:
    source = Twitch(channel)
  else:
    source = Log(sys.stdin.readlines())

  return source

def diagnose(args):
  source = _get_source(args.channel)
  Diagnosis().full_diagnosis(source)

def cure(args):
  source = _get_source(args.channel)
  twitchcancer.cure.cure(source)

def monitor(args):
  sources = [_get_source(channel) for channel in args.channel]
  twitchcancer.monitor.monitor(sources)

def api(args):
  twitchcancer.api.api.run(args)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()

  parser.add_argument('--log', dest='loglevel', default='WARNING',
    help="set the level of messages to display")

  subparsers = parser.add_subparsers()

  parser_diagnose = subparsers.add_parser('diagnose', help='diagnose a chat')
  parser_diagnose.add_argument('channel', nargs='?', help='#channel name', default=None)
  parser_diagnose.set_defaults(func=diagnose)

  parser_cure = subparsers.add_parser('cure', help='cure a chat')
  parser_cure.add_argument('channel', nargs='?', help='#channel name', default=None)
  parser_cure.set_defaults(func=cure)

  parser_monitor = subparsers.add_parser('monitor', help='monitor one or more channels')
  parser_monitor.add_argument('channel', nargs='*', help='#channel names', default=None)
  parser_monitor.set_defaults(func=monitor)

  parser_history = subparsers.add_parser('api', help='runs the API')
  parser_history.add_argument("--host", dest="host", default="localhost", help="hostname or ip address (default: localhost)")
  parser_history.add_argument("--port", dest="port", default=8080, help="port number  (default: 8080)")
  parser_history.set_defaults(func=api)

  args = parser.parse_args()

  # set logger level
  numeric_level = getattr(logging, args.loglevel.upper(), None)
  if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % loglevel)

  logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  logger.setLevel(numeric_level)

  # run the selected command
  args.func(args)
