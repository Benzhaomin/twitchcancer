#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from twitchcancer.symptom.symptoms import *

messages = {
  'sentence': 'this is a long sentence but not too long',
  'oneemote': 'Kappa',
  'onechar': 'k',
  'oneword': 'Elephant',
  'short': 'lol',
  'emotesandwords': 'THIS Kappa IS Kappa WHAT Kappa I Kappa CALL Kappa MUSIC',
  'longsentence': 'this is a long sentence but so long that it\s too long this is a long sentence but so long that it\s too long this is a long sentence but so long that it\s too long',
  'caps': 'THATS A LOT OF Caps',
}

class TestSymptom(unittest.TestCase):
  
  # twitchcancer.symptom.symptoms.Symptom.__str__()
  # check that we get the class's name in the string representation
  def test_rule_str(self):
    self.assertEqual(str(Symptom()), "Symptom")

  # twitchcancer.symptom.symptoms.Symptom.exhibited_by()
  # check that the no-op Symptom class allows everything
  def test_rule_exhibited_by(self):
    s = Symptom()
    
    for m in messages:
      self.assertFalse(s.exhibited_by(m))

class TestMinimumWordCount(unittest.TestCase):
  
  # twitchcancer.symptom.symptoms.MinimumWordCount.exhibited_by()
  def test_minimum_word_count_exhibited_by(self):
    s = MinimumWordCount()
    
    for k,v in messages.items():
      if k in ["sentence", "emotesandwords", "longsentence", "caps"]:
        self.assertFalse(s.exhibited_by(v))
      else:
        self.assertTrue(s.exhibited_by(v))

class TestMinimumMessageLength(unittest.TestCase):
  
  # twitchcancer.symptom.symptoms.MinimumMessageLength.exhibited_by()
  def test_minimum_message_length_exhibited_by(self):
    s = MinimumMessageLength()
    
    for k,v in messages.items():
      if k == "onechar":
        self.assertTrue(s.exhibited_by(v))
      else:
        self.assertFalse(s.exhibited_by(v))

class TestMaximumMessageLength(unittest.TestCase):
  
  # twitchcancer.symptom.symptoms.MaximumMessageLength.exhibited_by()
  def test_maximum_message_length_exhibited_by(self):
    s = MaximumMessageLength()
    
    for k,v in messages.items():
      if k == "longsentence":
        self.assertTrue(s.exhibited_by(v))
      else:
        self.assertFalse(s.exhibited_by(v))

# message must have a {ratio} of caps to characters maximum
class TestCapsRatio(unittest.TestCase):
  
  # twitchcancer.symptom.symptoms.CapsRatio.exhibited_by()
  def test_caps_ratio_exhibited_by(self):
    s = CapsRatio()
    
    for k,v in messages.items():
      if k in ["caps", "emotesandwords"]:
        self.assertTrue(s.exhibited_by(v))
      else:
        self.assertFalse(s.exhibited_by(v))
  
class TestEmoteCount(unittest.TestCase):
  
  # twitchcancer.symptom.symptoms.EmoteCount.count()
  def test_emote_count_count(self):
    self.assertEqual(EmoteCount.count('Kappa'), 1)
    self.assertEqual(EmoteCount.count('notanemote'), 0) 
    self.assertEqual(EmoteCount.count('Kappa KappaPride Keepo'), 3) 
  
  # twitchcancer.symptom.symptoms.EmoteCount.exhibited_by()
  def test_emote_count_exhibited_by(self):
    s = EmoteCount()
    
    for k,v in messages.items():
      if k == "emotesandwords":
        self.assertTrue(s.exhibited_by(v))
      else:
        self.assertFalse(s.exhibited_by(v))
    
class TestEmoteRatio(unittest.TestCase):
  
  # twitchcancer.symptom.symptoms.EmoteRatio.exhibited_by()
  def test_emote_ratio_exhibited_by(self):
    s = EmoteRatio()
    
    for k,v in messages.items():
      if k == "oneemote":
        self.assertTrue(s.exhibited_by(v))
      else:
        self.assertFalse(s.exhibited_by(v))
