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

# twitchcancer.symptom.symptoms.MinimumWordCount
class TestMinimumWordCount(unittest.TestCase):

  # exhibited_by()
  def test_minimum_word_count_exhibited_by(self):
    s = MinimumWordCount()

    for k,v in messages.items():
      if k in ["sentence", "emotesandwords", "longsentence", "caps"]:
        self.assertFalse(s.exhibited_by(v))
      else:
        self.assertTrue(s.exhibited_by(v))

  # points()
  def test_minimum_word_count_points(self):
    s1 = MinimumWordCount()
    self.assertEqual(s1.points("sentence"), 1)
    self.assertEqual(s1.points("sentence words"), 0)
    self.assertEqual(s1.points("sentence words words"), 0)

    s2 = MinimumWordCount(3)
    self.assertEqual(s2.points("sentence"), 2)
    self.assertEqual(s2.points("sentence words"), 1)
    self.assertEqual(s2.points("sentence words words"), 0)
    self.assertEqual(s2.points("sentence words words words"), 0)

# twitchcancer.symptom.symptoms.MinimumMessageLength
class TestMinimumMessageLength(unittest.TestCase):

  # exhibited_by()
  def test_minimum_message_length_exhibited_by(self):
    s = MinimumMessageLength()

    for k,v in messages.items():
      if k == "onechar":
        self.assertTrue(s.exhibited_by(v))
      else:
        self.assertFalse(s.exhibited_by(v))

  # points()
  def test_minimum_message_length_points(self):
    s1 = MinimumMessageLength()
    self.assertEqual(s1.points("123456789012345"), 0)
    self.assertEqual(s1.points("1234567890"), 0)
    self.assertEqual(s1.points("12345"), 0)
    self.assertEqual(s1.points("123"), 0)
    self.assertEqual(s1.points("1"), 1)

    s2 = MinimumMessageLength(10)
    self.assertEqual(s2.points("123456789012345"), 0)
    self.assertEqual(s2.points("1234567890"), 0)
    self.assertEqual(s2.points("12345"), 2)
    self.assertEqual(s2.points("123"), 3)
    self.assertEqual(s2.points("1"), 4)

# twitchcancer.symptom.symptoms.MaximumMessageLength
class TestMaximumMessageLength(unittest.TestCase):

  # exhibited_by()
  def test_maximum_message_length_exhibited_by(self):
    s = MaximumMessageLength()

    for k,v in messages.items():
      if k == "longsentence":
        self.assertTrue(s.exhibited_by(v))
      else:
        self.assertFalse(s.exhibited_by(v))

  # points()
  def test_maximum_message_length_points(self):
    s1 = MaximumMessageLength()
    self.assertEqual(s1.points("1234567890"), 0)
    self.assertEqual(s1.points("123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"), 3)

    s2 = MaximumMessageLength(10)
    self.assertEqual(s2.points("1234567890"), 0)
    self.assertEqual(s2.points("1234567890123"), 1)
    self.assertEqual(s2.points("123456789012345"), 2)

# twitchcancer.symptom.symptoms.CapsRatio
class TestCapsRatio(unittest.TestCase):

  # exhibited_by()
  def test_caps_ratio_exhibited_by(self):
    s = CapsRatio()

    for k,v in messages.items():
      if k in ["caps", "emotesandwords"]:
        self.assertTrue(s.exhibited_by(v))
      else:
        self.assertFalse(s.exhibited_by(v))

  # points()
  def test_caps_ratio_points(self):
    s1 = CapsRatio()
    self.assertEqual(s1.points("Foobar"), 0)
    self.assertEqual(s1.points("FooBar"), 1)
    self.assertEqual(s1.points("FOOBAR"), 2)

    s2 = CapsRatio(1)
    self.assertEqual(s2.points("FAHDASH DSAHDHAS"), 0)
    self.assertEqual(s2.points("DASDASDA"), 0)

# twitchcancer.symptom.symptoms.EmoteCount
class TestEmoteCount(unittest.TestCase):

  # count()
  def test_emote_count_count(self):
    self.assertEqual(EmoteCount.count('Kappa'), 1)
    self.assertEqual(EmoteCount.count('notanemote'), 0)
    self.assertEqual(EmoteCount.count('Kappa KappaPride Keepo'), 3)

  # exhibited_by()
  def test_emote_count_exhibited_by(self):
    s = EmoteCount()

    for k,v in messages.items():
      if k == "emotesandwords":
        self.assertTrue(s.exhibited_by(v))
      else:
        self.assertFalse(s.exhibited_by(v))

  # points()
  def test_emote_count_points(self):
    s1 = EmoteCount()
    self.assertEqual(s1.points("Kappa"), 0)
    self.assertEqual(s1.points("Kappa KappaPride"), 1)
    self.assertEqual(s1.points("Kappa KappaPride Keepo"), 2)
    self.assertEqual(s1.points("Kappa KappaPride Keepo Keepo"), 2)
    self.assertEqual(s1.points("Kappa KappaPride Keepo Keepo KappaPride"), 3)

    s2 = EmoteCount(3)
    self.assertEqual(s2.points("Kappa"), 0)
    self.assertEqual(s2.points("Kappa KappaPride Keepo"), 0)
    self.assertEqual(s2.points("Kappa KappaPride Keepo Keepo"), 1)
    self.assertEqual(s2.points("Kappa KappaPride Keepo Keepo KappaPride KappaPride"), 2)

# twitchcancer.symptom.symptoms.EmoteRatio
class TestEmoteRatio(unittest.TestCase):

  # exhibited_by()
  def test_emote_ratio_exhibited_by(self):
    s = EmoteRatio()

    for k,v in messages.items():
      if k == "oneemote":
        self.assertTrue(s.exhibited_by(v))
      else:
        self.assertFalse(s.exhibited_by(v))

  # points()
  def test_emote_ratio_points(self):
    s1 = EmoteRatio()
    self.assertEqual(s1.points("Foo"), 0)
    self.assertEqual(s1.points("Kappa"), 2)
    self.assertEqual(s1.points("Kappa test test"), 0)
    self.assertEqual(s1.points("Kappa KappaPride Keepo"), 2)
    self.assertEqual(s1.points("Kappa KappaPride Keepo Keepo"), 2)
    self.assertEqual(s1.points("Kappa KappaPride Keepo Keepo KappaPride"), 2)

    s2 = EmoteRatio(1)
    self.assertEqual(s2.points("Kappa"), 0)
    self.assertEqual(s2.points("Kappa KappaPride Keepo"), 0)
    self.assertEqual(s2.points("Kappa KappaPride Keepo Keepo"), 0)
    self.assertEqual(s2.points("Kappa KappaPride Keepo Keepo KappaPride KappaPride"), 0)

# twitchcancer.symptom.symptoms.BannedPhrase
class TestBannedPhrase(unittest.TestCase):

  # exhibited_by()
  def test_banned_phrase_exhibited_by(self):
    s = BannedPhrase()

    self.assertFalse(s.exhibited_by("Darude"))
    self.assertTrue(s.exhibited_by("Darude Sandstorm"))

  # points()
  def test_banned_phrase_points(self):
    s = BannedPhrase()
    self.assertEqual(s.points("Kappa"), 0)
    self.assertEqual(s.points("Darude sandstorm"), 1)
    self.assertEqual(s.points("Darude sandstorm Darude sandstorm"), 2)
    self.assertEqual(s.points("Darude sandstorm message deleted"), 2)

# twitchcancer.symptom.symptoms.EchoingRatio
class TestEchoingRatio(unittest.TestCase):

  # exhibited_by()
  def test_echoing_ratio_exhibited_by(self):
    s = EchoingRatio()

    self.assertFalse(s.exhibited_by("lol"))
    self.assertFalse(s.exhibited_by("foo bar"))
    self.assertTrue(s.exhibited_by("lol lol"))

  # points()
  def test_echoing_ratio_points(self):
    s = EchoingRatio()
    self.assertEqual(s.points("lol"), 0)
    self.assertEqual(s.points("lol lol"), 1)
    self.assertEqual(s.points("lol lol lol"), 2)
    self.assertEqual(s.points("lol lol lol lol"), 2)
    self.assertEqual(s.points("lol rekt lol rekt"), 1)
