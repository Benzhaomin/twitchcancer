#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import irc.client
import logging
import itertools
logger = logging.getLogger('sanitwitcher.logger')
# http://api.twitch.tv/api/channels/{channel}/chat_properties

class Client(irc.client.SimpleIRCClient):
  
  def __init__(self, config):
    irc.client.SimpleIRCClient.__init__(self)
    
    self.config = config
    self.channel = None
    
  def join(self, channel):
    # leave the previous channel if any
    if self.channel:
      self.connection.part(self.channel)
      
    # save the new active channel
    self.channel = channel
    
    # connect if necessary (and auto-join on welcome)
    if not self.connection.is_connected():
      try:
        self.connect(self.config['server'], self.config['port'], self.config['username'], self.config['password'])
      except irc.client.ServerConnectionError as x:
          print(x)
          sys.exit(1)
    # already connected, just join
    else:
      self.connection.join(self.channel)

  def on_welcome(self, connection, event):
    if irc.client.is_channel(self.channel):
      logger.info('[chat]: welcome, joining %s', self.channel)
      connection.join(self.channel)
    else:
      logger.info('[chat]: welcome but channel %s bot found', self.channel)
      sys.exit(1)
  
  def on_join(self, connection, event):
    logger.info('[chat]: joined %s', self.channel)

  def on_pubmsg(self, connection, event):
    logger.info('[chat]: read %s', event.arguments)
    
    # forward the message to a callback if any
    do_nothing = lambda msg: None
    method = getattr(self, "call_on_pubmsg", do_nothing)
    method(event.arguments[0])
  
  def on_disconnect(self, connection, event):
    sys.exit(0)

def debug_on_msg(msg):
  print(msg)

if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
  
  config = {
    'server': 'irc.ca.us.mibbit.net',
    'port': 6667,
    'username': 'testpython',
    'password': None,
  }
  c = Client(config)
  c.call_on_pubmsg = debug_on_msg
  c.join('#testkappa')
  c.start()
