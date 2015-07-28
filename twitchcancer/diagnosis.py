#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
logger = logging.getLogger('twitchcancer.logger')

from twitchcancer.symptoms import *

class Diagnosis:
  
  def __init__(self):
    super().__init__()
    
    self.symptoms = [MinimumWordCount(), MinimumMessageLength(), MaximumMessageLength(), CapsRatio(), EmoteCount(), EmoteRatio()]
  
  # tells whether a message looks sane based on all sorts of factors
  def is_sane(self, message):
    
    # check if any of our symptoms are exhibited by the message
    for symptom in self.symptoms:
      if symptom.exhibited_by(message):
        logger.debug('[diagnosis] message %s broke the %s symptom', message.strip(), symptom)
        return False
    
    # all good, we have a sane message
    return True

if __name__ == "__main__":  
  logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
  
  d = Diagnosis()
  
  count = 0
  sane = []
  dirty = []
  
  # get channel name
  with open(os.path.join(os.path.dirname(__file__), '../tests/dota2ti.log')) as destiny:
    for line in destiny:
      count += 1
      
      if d.is_sane(line):
        sane.append(line)
        print(line.strip())
      else:
        dirty.append(line)

  print("total lines {total}, sane {sane}, dirty {dirty} ".format(total=count, sane=len(sane), dirty=len(dirty)))
  print("quality {quality:.2f}% ".format(quality=100*len(sane)/count))
