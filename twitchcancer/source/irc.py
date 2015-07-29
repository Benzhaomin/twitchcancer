#!/usr/bin/env python
# -*- coding: utf-8 -*-

import queue
import threading
import logging
logger = logging.getLogger('twitchcancer.logger')

from twitchcancer.source.ircconfig import config as CONFIG
from twitchcancer.lib.ircclient import IRCClient
from twitchcancer.source.source import Source

# live channel, messages come in as time goes
class IRC(Source):
  
  def __init__(self, channel):
    super().__init__()
    
    # irc channel to join
    self.channel = channel
    
    # queue used to hold messages coming from the producer (IRC client) and going into our consumer
    self.messages = queue.Queue()
    
    # run network communication in a background thread 
    t = threading.Thread(target=self._client_thread)
    t.daemon = True
    t.start()
  
  # we are iterable
  def __iter__(self):
    return self
  
  # return the first unread message in the queue or blocks waiting for one
  def __next__(self):
    try:
      return self.messages.get()
    except KeyboardInterrupt:
      raise StopIteration 
  
  # returns the config to use for our IRC client
  def _get_irc_config(self):
    return CONFIG
    
  # background thread to handle all IRC communication
  def _client_thread(self):    
    c = IRCClient(self._get_irc_config())
    c.call_on_pubmsg = self._on_pubmsg
    c.join(self.channel)
    c.start()
  
  # add messages we received to the queue
  # called from the client thread
  def _on_pubmsg(self, message):
    message = message.strip()
    if len(message) > 0:
      self.messages.put(message)

if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
  
  source = IRC('#testkappa')
  
  for m in source:
    print(m)
