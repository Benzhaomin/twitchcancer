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
