#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import itertools
import logging
logger = logging.getLogger(__name__)

import irc.client

class IRCClientLogger(logging.Logger):

  # ignore log
  def log(self, *args, **kwargs):
    pass

  # ignore info
  def info(self, *args, **kwargs):
    pass

  # ignore debug
  def debug(self, *args, **kwargs):
    pass

# monkey-patch irc.client's logger to avoid n (>5) useless calls to the logger per message
irc.client.log = IRCClientLogger(irc.client.log.name)

class IRCClient(irc.client.SimpleIRCClient):

  def __init__(self, config):
    irc.client.SimpleIRCClient.__init__(self)

    self.config = config
    self.autojoin = set()
    self.channels = set()

  def _connect(self):
    if not self.connection.is_connected():
      try:
        self.connect(self.config['server'], self.config['port'], self.config['username'], self.config['password'])
      except irc.client.ServerConnectionError as x:
          print(x)
          sys.exit(1)

  def __str__(self):
    return self.config['server'] + ':' + str(self.config['port'])

  def join(self, channel):
    # connect if necessary (and auto-join on welcome)
    if not self.connection.is_connected():
      logger.debug('%s not connected yet, will join %s later', self, channel)
      self.autojoin.add(channel)
      return

    # make sure the channel exists
    if not irc.client.is_channel(channel):
      logger.warn('channel %s not found on ', channel, self)
      return

    # don't join the same channel twice
    if channel in self.channels:
      return

    # send an IRC JOIN command
    self.connection.join(channel)
    logger.info("joining %s", channel)

    # save the new channel
    self.channels.add(channel)

  def leave(self, channel):
    # just don't do anything if we're not connected
    if not self.connection.is_connected():
      logger.debug('%s not connected yet, no need to leave %s', self, channel)
      return

    # make sure the channel exists
    if not irc.client.is_channel(channel):
      logger.warn('channel %s not found on ', channel, self)
      return

    # send an IRC PART command
    self.connection.part(channel)
    logger.info("leaving %s", channel)

    # save the new channel
    self.channels.remove(channel)

  def on_welcome(self, connection, event):
    logger.debug('welcome, joining %s', self.autojoin)

    for channel in set(self.autojoin):
      self.autojoin.remove(channel)
      self.join(channel)

  def on_join(self, connection, event):
    logger.debug('joined %s', event.target)

  def on_pubmsg(self, connection, event):
    #logger.debug('read %s', connection)
    #logger.debug('read %s', event.arguments)

    # forward the message to a callback if any
    do_nothing = lambda channel, msg: None
    method = getattr(self, "call_on_pubmsg", do_nothing)
    method(event.target, event.arguments[0])

  def on_disconnect(self, connection, event):
    sys.exit(0)

def debug_on_msg(msg):
  print(msg)

if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

  config = {
    'server': 'irc.ca.us.mibbit.net',
    'port': 6667,
    'username': 'testpython',
    'password': None,
  }
  c = IRCClient(config)
  c.call_on_pubmsg = debug_on_msg
  c.join('#testkappa')
  c.join('#testkappa2')
  c._connect()
  c.start()
