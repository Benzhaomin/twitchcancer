#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request
import json
import logging
logger = logging.getLogger('twitchcancer.logger')

from twitchcancer.source.irc import IRC

class Twitch(IRC):
  
  def __init__(self, channel):
    super().__init__(channel)

  # use the default config with a custom server/port depending on the channel
  def _get_irc_config(self):
    config = super()._get_irc_config()
    config['server'], config['port'] = self.get_server(self.channel.strip('#'))
    return config

  @classmethod
  # get the actual server of a channel to support event servers
  def get_server(cls, channel):
    with urllib.request.urlopen('http://api.twitch.tv/api/channels/{0}/chat_properties'.format(channel)) as response:
       j = json.loads(response.read().decode())
       server_port = j['chat_servers'][0].split(':')
       return (server_port[0], int(server_port[1]))

if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
  
  source = Twitch('#gamesdonequick')
  
  for m in source:
    pass
