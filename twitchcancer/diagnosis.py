#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
logger = logging.getLogger('twitchcancer.logger')

from twitchcancer.symptom.symptoms import *

class Diagnosis:
  
  def __init__(self):
    super().__init__()
    
    self.symptoms = [MinimumWordCount(), MinimumMessageLength(), MaximumMessageLength(), CapsRatio(), EmoteCount(), EmoteRatio()]
  
  # returns a list of Symptoms exhibited by the message
  def diagnose(self, message):
    return [s for s in self.symptoms if s.exhibited_by(message)]

  # run a full diagnosis of a source
  def full_diagnosis(self, source):
    count = 0
    sane = []
    ill = []
  
    for message in source:
      count += 1
      symptoms = self.diagnose(message)
      
      if len(symptoms) == 0 :
        sane.append(message)
        logger.info('[diagnosis] sane: %s', message.strip())
      else:
        ill.append(message)
        logger.info('[diagnosis] ill (%s): %s', ', '.join(map(str, symptoms)), message.strip())
    
    print("messages {total}, sane {sane}, ill {ill} ".format(total=count, sane=len(sane), ill=len(ill)))
    print("health {health:.2f}% ".format(health=100*len(sane)/count))

from twitchcancer.source.log import Log
from twitchcancer.source.twitch import Twitch

if __name__ == "__main__":  
  logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
  
  #with open(os.path.join(os.path.dirname(__file__), '../tests/destiny.log')) as destiny:
  #  source = Log(destiny.readlines())
  source = Twitch('#gamesdonequick')
  
  Diagnosis().full_diagnosis(source)
