#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
logger = logging.getLogger('sanitwitcher.logger')

from sanitwitcher.rules import *

class Sanitizer:
  
  def __init__(self):
    super().__init__()
    
    self.rules = [MinimumWordCount(), MinimumMessageLength(), EmoteRatio()]
  
  # tells whether a message looks sane based on all sorts of factors
  def is_sane(self, message):
    
    # check if any of our rules are broken
    for rule in self.rules:
      if rule.broken(message):
        logger.debug('[sanitizer] message %s broke the %s rule', message, rule)
        return False
    
    # all good, we have a sane message
    return True
  
