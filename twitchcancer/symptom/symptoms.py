#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

# no-op Symptom
class Symptom:
  
  def __init__(self):
    super().__init__()
  
  def __str__(self):
    return type(self).__name__
  
  # tells whether a message respects the rule
  def exhibited_by(self, message):
    return False

# message must have a minimum of {count} words
class MinimumWordCount(Symptom):
  
  def __init__(self, count=2):
    super().__init__()

    self.count = count
  
  def exhibited_by(self, message):
    return len(message.strip().split()) < self.count
  
# message must be a least {length} long
class MinimumMessageLength(Symptom):
  
  def __init__(self, length=2):
    super().__init__()

    self.length = length
  
  def exhibited_by(self, message):
    return len(message.strip()) < self.length

# message must be a least {length} long
class MaximumMessageLength(Symptom):
  
  def __init__(self, length=160):
    super().__init__()

    self.length = length
  
  def exhibited_by(self, message):
    return len(message.strip()) >= self.length

# message must have a {ratio} of caps to characters maximum
class CapsRatio(Symptom):
  
  def __init__(self, ratio=0.2):
    super().__init__()

    self.ratio = ratio
  
  def exhibited_by(self, message):
    ratio = len([c for c in message.strip() if c.isupper()]) / len(message.strip())

    return ratio > self.ratio
    
# message can have {count} emotes maximum
class EmoteCount(Symptom):
 
  def __init__(self, count=3):
    super().__init__()

    self._count = count
  
  # class variable: load a list of all the emotes
  with open(os.path.join(os.path.dirname(__file__), 'emotes.txt')) as emotes_file:
    emotes = emotes_file.read().splitlines() 
  
  @classmethod
  def count(cls, message):
    return len([word for word in message.strip().split() if word in EmoteCount.emotes])

  def exhibited_by(self, message):    
    return self.count(message) > self._count

# message must have a {ratio} of emotes vs words maximum
class EmoteRatio(Symptom):
  
  def __init__(self, ratio=0.49):
    super().__init__()

    self.ratio = ratio
    
  def exhibited_by(self, message):
    ratio = EmoteCount.count(message) / len(message.strip().split())
    
    return ratio > self.ratio

# message can't contain any of the banned phrases
class BannedPhrase(Symptom):
 
  def __init__(self):
    super().__init__()
  
  # class variable: load a list of all the banned phrases
  with open(os.path.join(os.path.dirname(__file__), 'banned.txt')) as banned_file:
    banned = banned_file.read().splitlines() 
  
  def exhibited_by(self, message):
    for phrase in BannedPhrase.banned:
      if phrase in message:
        return True
    return False

# message can't be a single word echoing too often
class EchoingRatio(Symptom):
 
  def __init__(self, ratio=1):
    super().__init__()
    
    self.ratio = ratio
  
  def exhibited_by(self, message):
    words = message.split()
    
    # a single word can't be echoing
    if len(words) == 1:
      return False
    
    return len(set(words)) / len(words) < self.ratio
