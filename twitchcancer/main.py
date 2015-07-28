#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
logger = logging.getLogger('twitchcancer.logger')

from twitchcancer.cure import Cure
from twitchcancer.diagnosis import Diagnosis

# TODO usage:
# diagnose a live channel: main.py --diagnose [#]channel
# diagnose a log: cat log | main.py --diagnose
# cure a live channel: main.py --cure [#]channel
# cure a log: cat log | main.py --cure
 
if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  
  parser.add_argument('--log', dest='loglevel', default='WARNING',
    help="set the level of messages to display")
  
  args = parser.parse_args()
  
  # set logger level
  numeric_level = getattr(logging, args.loglevel.upper(), None)
  if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % loglevel)
  
  logging.basicConfig(level=numeric_level, format='%(asctime)s %(message)s')
  
  # get channel name
  channel = args.channel
  if not channel.startswith('#'):
    channel = '#' + channel
  
