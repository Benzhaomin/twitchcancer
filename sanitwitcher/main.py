#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
logger = logging.getLogger('sanitwitcher.logger')

from sanitwitcher.config import config
from sanitwitcher.client import Client
from sanitwitcher.sanitizer import Sanitizer

sanitizer = Sanitizer()

def on_pubmsg(message):
  if sanitizer.is_sane(message):
    print(message)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  
  parser.add_argument('--log', dest='loglevel', default='WARNING',
    help="set the level of messages to display")
      
  parser.add_argument('channel',
    help='channel to join')
  
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
  
  c = Client(config)
  c.call_on_pubmsg = on_pubmsg
  c.join(channel)
  c.start()

# get channel from the command line
# create a chat object with those settings
# set the sanitizer too
# run the chat
## chat gets messages from the server, filters messages (logger.debug on filtered out messages)


# sanitizer.py learning from chat logs (forsen etc)
