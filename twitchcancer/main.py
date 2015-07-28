#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import urllib.request
import json
import logging
logger = logging.getLogger('twitchcancer.logger')

from twitchcancer.config import config
from twitchcancer.client import Client
from twitchcancer.diagnosis import Diagnosis

diagnosis = Diagnosis()

# we must check the actual server of the channel to support event channels
def get_server_for_channel(channel):
  with urllib.request.urlopen('http://api.twitch.tv/api/channels/{0}/chat_properties'.format(channel)) as response:
     j = json.loads(response.read().decode())
     server_port = j['chat_servers'][0].split(':')
     return (server_port[0], int(server_port[1]))

# do something whenever a public message is received
def on_pubmsg(message):
  if diagnosis.is_sane(message):
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
    
  # find a server for this channel
  config['server'], config['port'] = get_server_for_channel(channel[1:])
  
  c = Client(config)
  c.call_on_pubmsg = on_pubmsg
  c.join(channel)
  c.start()
