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
    return self.points(message) > 0

  def points(self, message):
    return 0

# message must have a minimum of {count} words
class MinimumWordCount(Symptom):

  def __init__(self, count=2):
    super().__init__()

    self.count = count

  # every word missing = 1 point
  def points(self, message):
    missing = self.count - len(message.split())
    if missing > 0:
      return missing
    return 0

# message must be a least {length} long
class MinimumMessageLength(Symptom):

  def __init__(self, length=2):
    super().__init__()

    self.length = length

  # first character missing = 1 point, then every 3 characters missing = 1 point
  def points(self, message):
    missing = self.length - len(message)
    if missing > 0:
      return 1 + int(missing / 3)
    return 0

# message must be a least {length} long
class MaximumMessageLength(Symptom):

  def __init__(self, length=80):
    super().__init__()

    self.length = length

  # first character over the limit = 1 point, then every 5 characters = 1 point
  def points(self, message):
    over = len(message) - self.length
    if over > 0:
      return 1 + int(over / 5)
    return 0

# message must have a {ratio} of caps to characters maximum
class CapsRatio(Symptom):

  def __init__(self, ratio=0.2):
    super().__init__()

    self.ratio = ratio

  # over the limit = 1 point, then every 0.5 ratio over the limit = 1 point
  def points(self, message):
    ratio = sum(map(str.isupper, message)) / len(message)
    over = ratio - self.ratio
    if over > 0:
      return 1 + int(over / 0.5)
    return 0

# message can have {count} emotes maximum
class EmoteCount(Symptom):

  def __init__(self, count=1):
    super().__init__()

    self._count = count

  # class variable: load a list of all the emotes
  with open(os.path.join(os.path.dirname(__file__), 'emotes.txt')) as emotes_file:
    emotes = set(emotes_file.read().splitlines())

  @classmethod
  def count(cls, message):
    return len([word for word in message.split() if word in EmoteCount.emotes])

  # over the limit = 1 point, then every 2 emotes = 1 point
  def points(self, message):
    over = self.count(message) - self._count
    if over > 0:
      return 1 + int(over / 2)
    return 0

# message must have a {ratio} of emotes vs words maximum
class EmoteRatio(Symptom):

  def __init__(self, ratio=0.49):
    super().__init__()

    self.ratio = ratio

  # over the limit = 1 point, then every 0.5 ratio over the limit = 1 point
  def points(self, message):
    ratio = EmoteCount.count(message) / len(message.split())
    over = ratio - self.ratio
    if over > 0:
      return 1 + int(over / 0.5)
    return 0

# applies emote count and emote ratio in the same call to avoid counting emotes twice
class EmoteCountAndRatio(Symptom):

  def __init__(self, count=1, ratio=0.49):
    super().__init__()

    self._count = count
    self.ratio = ratio

  # over the limit = 1 point, then every 0.5 ratio over the limit = 1 point
  def points(self, message):
    emotes_count = EmoteCount.count(message)
    points = 0

    # EmoteCount.points()
    over = emotes_count - self._count
    if over > 0:
      points += 1 + int(over / 2)

    # EmoteRatio.points()
    ratio = emotes_count / len(message.split())
    over = ratio - self.ratio
    if over > 0:
      points += 1 + int(over / 0.5)

    return points

# message can't contain any of the banned phrases
class BannedPhrase(Symptom):

  def __init__(self):
    super().__init__()

  # class variable: load a list of all the banned phrases
  with open(os.path.join(os.path.dirname(__file__), 'banned.txt')) as banned_file:
    banned = set(map(str.lower, banned_file.read().splitlines()))

  # one occurence of a banned phrase = 1 point
  def points(self, message):
    points = 0
    message = message.lower()
    for phrase in BannedPhrase.banned:
      if phrase in message: # optimization
        points += message.count(phrase)
    return points

import re

# message can't be a single word echoing too often
class EchoingRatio(Symptom):

  def __init__(self, ratio=0.7):
    super().__init__()

    self.ratio = ratio

  # one duplicate word = 1 point
  def points(self, message):
    words = message.split()
    words_count = len(words)

    # a single word isn't echoing itself
    if words_count == 1:
      return 0

    ratio = len(set(words)) / words_count
    over = self.ratio - ratio
    if over > 0:
      return 1 + int(over / 0.3)
    return 0
