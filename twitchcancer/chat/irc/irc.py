#!/usr/bin/env python
# -*- coding: utf-8 -*-

import queue
import threading
import logging
logger = logging.getLogger(__name__)

from twitchcancer.chat.irc.ircclient import IRCClient, IRCConfigurationError, IRCConnectionError
from twitchcancer.config import Config

class ServerConfigurationError(Exception):
  pass

class ServerConnectionError(Exception):
  pass

# provides an iterator over messages received on an IRC server (multi-channel)
class IRC:

  # raises: ServerConfigurationError
  def __init__(self, host, port):
    super().__init__()

    self.host = host
    self.port = int(port)

    # queue used to hold messages coming from the producer (IRC client) and going into our consumer
    self.messages = queue.Queue()

    # thread started on connect only
    self.client_thread = None

    # create an IRCClient for this server
    try:
      self.client = IRCClient({
        'username': Config.get("monitor.chat.username"),
        'password': Config.get("monitor.chat.password"),
        'server': self.host,
        'port': self.port
      })
    except IRCConfigurationError:
      raise ServerConfigurationError("Invalid configuration for {0}:{1}".format(self.host, self.port))

  # raises: ServerConnectionError
  def connect(self):
    try:
      self.client._connect()

      # run network communication in a background thread
      self.client_thread = threading.Thread(target=self._client_thread, kwargs={'client': self.client})
      self.client_thread.daemon = True
      self.client_thread.start()

      logger.debug('started a client thread for %s', self.host);
    except IRCConnectionError:
      raise ServerConnectionError("Failed to connect to {0}:{1}".format(self.host, self.port))

  # we are iterable
  def __iter__(self):
    return self

  # return the first unread message in the queue or block waiting for one
  def __next__(self):
    return self.messages.get()

  # transmit the join call to our IRC client
  def join(self, channel):
    self.client.join(channel)

  # transmit the join call to our IRC client
  def leave(self, channel):
    self.client.leave(channel)

  def __getattr__(self, attr):
    if attr == "channels":
      return self.client.channels

  # background thread to handle all IRC communication
  def _client_thread(self, client):
    client.call_on_pubmsg = self._on_pubmsg
    client.start()

  # put messages we received in the queue
  def _on_pubmsg(self, channel, message):
    message = message.strip()

    if len(message) > 0:
      self.messages.put((channel, message))
    else:
      logger.warning("empty message in %s", channel)

if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

  source = IRC('#testkappa')

  for m in source:
    print(m)
