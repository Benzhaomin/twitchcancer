#!/usr/bin/env python
# -*- coding: utf-8 -*-

import queue
import threading
import logging
logger = logging.getLogger(__name__)

from twitchcancer.chat.irc.ircclient import IRCClient
from twitchcancer.chat.config import config as CONFIG

# connect to a server, messages come in as time goes
class IRC:

  def __init__(self, host, port):
    super().__init__()

    self.host = host
    self.port = port
    self.name = host
    self.messages = None

  # initialize runtime things when we actually need to
  def __lazy_init__(self):
    # queue used to hold messages coming from the producer (IRC client) and going into our consumer
    self.messages = queue.Queue()

    # run network communication in a background thread
    self.client = IRCClient(self._get_irc_config())

    t = threading.Thread(target=self._client_thread, kwargs={'client': self.client})
    t.daemon = True
    t.start()

    logger.debug('started a client thread for %s', self.name);

  # we are iterable
  def __iter__(self):
    return self

  # return the first unread message in the queue or blocks waiting for one
  def __next__(self):
    try:
      return self.messages.get()
    # raised when messages is None, when __init__ ran but not __lazy_init__
    except AttributeError:
      self.__lazy_init__()
      return self.__next__()
    except KeyboardInterrupt:
      raise StopIteration

  # returns the config to use for our IRC client
  def _get_irc_config(self):
    config =  CONFIG

    config['server'] = self.host
    config['port'] = int(self.port)

    return config

  def join(self, channel):
    self.client.join(channel)

  def leave(self, channel):
    self.client.leave(channel)

  def __getattr__(self, attr):
    if attr == "channels":
      return self.client.channels

  # background thread to handle all IRC communication
  def _client_thread(self, client):
    client.call_on_pubmsg = self._on_pubmsg
    client._connect()
    client.start()

  # add messages we received to the queue
  # called from the client thread
  def _on_pubmsg(self, channel, message):
    message = message.strip()
    if len(message) > 0:
      self.messages.put((channel, message))

if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

  source = IRC('#testkappa')

  for m in source:
    print(m)
