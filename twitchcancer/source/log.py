#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('twitchcancer.logger')

from twitchcancer.source.source import Source

# channel log, messages come from a local source as fast as possible
class Log(Source):
  
  def __init__(self, messages):
    super().__init__()
    
    self.messages = messages
  
  def __iter__(self):
    for message in self.messages:
      message = message.strip()
      if len(message) > 0:
        yield message

if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
  
  source = Log(['hey', 'ho', 'here we go'])
  
  for m in source:
    print(m)
