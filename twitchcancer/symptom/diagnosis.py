#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from twitchcancer.symptom.symptoms import *

class Diagnosis:

  def __init__(self):
    super().__init__()

    self.symptoms = [MinimumWordCount(), MinimumMessageLength(), MaximumMessageLength(), CapsRatio(), EmoteCountAndRatio(), BannedPhrase(), EchoingRatio()]

  # tries to find cancer, stops at the first symptom
  def cancer(self, message):
    m = Symptom.precompute(message)

    for s in self.symptoms:
      if s.exhibited_by(m):
        return True
    return False

  # returns a list of Symptoms exhibited by the message
  def diagnose(self, message):
    m = Symptom.precompute(message)

    return [s for s in self.symptoms if s.exhibited_by(m)]

  # returns the total of cancer points of the message
  def points(self, message):
    points = 0

    # pre-compute
    m = Symptom.precompute(message)

    for s in self.symptoms:
      points += s.points(m)

    if points > 200:
      if points > 1000:
        logger.info('very high score (%s) on %s', points, message)
      else:
        logger.debug('high score (%s) on %s', points, message)

    return points

'''
import yappi

def profile(message):
  d = Diagnosis()
  messages = [message+str(n) for n in range(10000)]

  yappi.start()

  for m in messages:
    d.points(m)

  yappi.get_func_stats().print_all()
  yappi.get_thread_stats().print_all()

  yappi.stop()

if __name__ == "__main__":

  profile("clean message")
  profile("Kappa Kappa Kappa Kappa Kappa Kappa")
  profile("DASD ASD ASDASDONAS DONASD{J NAS{D JNAS{DNJ A{SDNJ AISBDH IASHBD HASBD HASD{BHAS {DASBDBAS {DHBA")

'''
