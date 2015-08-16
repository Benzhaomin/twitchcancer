#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
logger = logging.getLogger(__name__)

from twitchcancer.symptom.symptoms import *

class Diagnosis:

  def __init__(self):
    super().__init__()

    self.symptoms = [MinimumWordCount(), MinimumMessageLength(), MaximumMessageLength(), CapsRatio(), EmoteCount(), EmoteRatio(), BannedPhrase(), EchoingRatio()]

  # tries to find cancer, stops at the first symptom
  def cancer(self, message):
    for s in self.symptoms:
      if s.exhibited_by(message):
        return True
    return False

  # returns a list of Symptoms exhibited by the message
  def diagnose(self, message):
    return [s for s in self.symptoms if s.exhibited_by(message)]

  # returns the total of cancer points of the message
  def points(self, message):
    points = sum([s.points(message) for s in self.symptoms])

    if points > 200:
      if points > 1000:
        logger.info('very high score (%s) on %s', points, message)
      else:
        logger.debug('high score (%s) on %s', points, message)

    return points

  # run a full diagnosis of a source
  def full_diagnosis(self, source):
    sane = 0
    ill = 0

    for message in source:
      symptoms = self.diagnose(message)

      if len(symptoms) == 0 :
        sane += 1
        logger.debug('sane: %s', message.strip())
      else:
        ill += 1
        logger.debug('ill (%s): %s', ', '.join(map(str, symptoms)), message.strip())

    print("messages {total}, sane {sane}, ill {ill} ".format(total=(ill+sane), sane=sane, ill=ill))
    print("health {health:.2f}% ".format(health=100*sane/(ill+sane)))

from twitchcancer.source.log import Log
from twitchcancer.source.twitch import Twitch

if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

  #with open(os.path.join(os.path.dirname(__file__), '../tests/destiny.log')) as destiny:
  #  source = Log(destiny.readlines())
  source = Twitch('#gamesdonequick')

  Diagnosis().full_diagnosis(source)
