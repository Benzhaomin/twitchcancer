#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import logging
logger = logging.getLogger('twitchcancer.logger')

import twitchcancer.cure
from twitchcancer.diagnosis import Diagnosis
from twitchcancer.source.twitch import Twitch
from twitchcancer.source.log import Log

# TODO usage:
# diagnose a live channel: main.py --diagnose [#]channel
# diagnose a log: cat log | main.py --diagnose
# cure a live channel: main.py --cure [#]channel
# cure a log: cat log | main.py --cure

def _get_source(args):
  channel = args.channel
  if channel:
    if not channel.startswith('#'):
      channel = '#' + channel
    source = Twitch(channel)
  else:
    source = Log(sys.stdin.readlines())
  
  return source

def diagnose(args):
  source = _get_source(args)
  Diagnosis().full_diagnosis(source)
  
def cure(args):
  source = _get_source(args)
  twitchcancer.cure.cure(source)

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
  
  args = parser.parse_args()
  
  # set logger level
  numeric_level = getattr(logging, args.loglevel.upper(), None)
  if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % loglevel)
  
  logging.basicConfig(level=numeric_level, format='%(asctime)s %(message)s')
  
  # run the selected command
  args.func(args)

  
