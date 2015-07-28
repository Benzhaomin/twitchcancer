#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

# no-op Rule
class Rule:
  
  def __init__(self):
    super().__init__()
  
  def __str__(self):
    return type(self).__name__
  
  # tells whether a message respects the rule
  def broken(self, message):
    return False

# message must have a minimum of {count} words
class MinimumWordCount(Rule):
  
  def __init__(self, count=2):
    super().__init__()

    self.count = count
  
  def broken(self, message):
    return len(message.strip().split()) < self.count
  
# message must be a least {length} long
class MinimumMessageLength(Rule):
  
  def __init__(self, length=2):
    super().__init__()

    self.length = length
  
  def broken(self, message):
    return len(message.strip()) < self.length

# message must be a least {length} long
class MaximumMessageLength(Rule):
  
  def __init__(self, length=160):
    super().__init__()

    self.length = length
  
  def broken(self, message):
    return len(message.strip()) >= self.length

# message must have a {ratio} of caps to characters maximum
class CapsRatio(Rule):
  
  def __init__(self, ratio=0.2):
    super().__init__()

    self.ratio = ratio
  
  def broken(self, message):
    ratio = len([c for c in message.strip() if c.isupper()]) / len(message.strip())

    return ratio > self.ratio
    
# message can have {count} emotes maximum
class EmoteCount(Rule):
 
  def __init__(self, count=3):
    super().__init__()

    self._count = count
  
  # class variable: load a list of all the emotes
  with open(os.path.join(os.path.dirname(__file__), 'emotes.txt')) as emotes_file:
    emotes = emotes_file.read().splitlines() 
  
  @classmethod
  def count(cls, message):
    return len([word for word in message.strip().split() if word in EmoteCount.emotes])

  def broken(self, message):    
    return self.count(message) > self._count

# message must have a {ratio} of emotes vs words maximum
class EmoteRatio(Rule):
  
  def __init__(self, ratio=0.5):
    super().__init__()

    self.ratio = ratio
    
  def broken(self, message):
    ratio = EmoteCount.count(message) / len(message.strip().split())
    
    return ratio > self.ratio
