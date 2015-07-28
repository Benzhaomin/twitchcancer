#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
logger = logging.getLogger('twitchcancer.logger')

from twitchcancer.rules import *

class Cure:
  
  def __init__(self):
    super().__init__()
    
    self.rules = [MinimumWordCount(), MinimumMessageLength(), MaximumMessageLength(), CapsRatio(), EmoteCount(), EmoteRatio()]
  
  # tells whether a message looks sane based on all sorts of factors
  def is_sane(self, message):
    
    # check if any of our rules are broken
    for rule in self.rules:
      if rule.broken(message):
        logger.debug('[cure] message %s broke the %s rule', message.strip(), rule)
        return False
    
    # all good, we have a sane message
    return True

if __name__ == "__main__":  
  logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
  
  s = Cure()
  
  count = 0
  sane = []
  dirty = []
  
  # get channel name
  with open(os.path.join(os.path.dirname(__file__), '../tests/dota2ti.log')) as destiny:
    for line in destiny:
      count += 1
      
      if s.is_sane(line):
        sane.append(line)
        print(line.strip())
      else:
        dirty.append(line)

  print("total lines {total}, sane {sane}, dirty {dirty} ".format(total=count, sane=len(sane), dirty=len(dirty)))
  print("quality {quality:.2f}% ".format(quality=100*len(sane)/count))
