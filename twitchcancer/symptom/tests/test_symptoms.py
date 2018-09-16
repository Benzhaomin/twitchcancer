import unittest

from twitchcancer.symptom import symptoms

p = symptoms.Symptom.precompute

messages = {
    'sentence': p('this is a long sentence but not too long'),
    'oneemote': p('Kappa'),
    'onechar': p('k'),
    'oneword': p('Elephant'),
    'short': p('lol'),
    'emotesandwords': p('THIS Kappa IS Kappa WHAT Kappa I Kappa CALL Kappa MUSIC'),
    'longsentence': p('this is a long sentence but so long that it\s too long this is a long sentence but so long '
                      'that it\s too long this is a long sentence but so long that it\s too long'),
    'caps': p('THATS A LOT OF Caps'),
}


class TestSymptom(unittest.TestCase):

    # twitchcancer.symptom.symptoms.Symptom.__str__()
    # check that we get the class's name in the string representation
    def test_rule_str(self):
        self.assertEqual(str(symptoms.Symptom()), "Symptom")

    # twitchcancer.symptom.symptoms.Symptom.exhibited_by()
    # check that the no-op Symptom class allows everything
    def test_rule_exhibited_by(self):
        s = symptoms.Symptom()

        for m in messages:
            self.assertFalse(s.exhibited_by(m))


# twitchcancer.symptom.symptoms.MinimumWordCount
class TestMinimumWordCount(unittest.TestCase):

    # exhibited_by()
    def test_minimum_word_count_exhibited_by(self):
        s = symptoms.MinimumWordCount()

        for k, v in messages.items():
            if k in ["sentence", "emotesandwords", "longsentence", "caps"]:
                self.assertFalse(s.exhibited_by(v))
            else:
                self.assertTrue(s.exhibited_by(v))

    # points()
    def test_minimum_word_count_points(self):
        s1 = symptoms.MinimumWordCount()
        self.assertEqual(s1.points(p("sentence")), 1)
        self.assertEqual(s1.points(p("sentence words")), 0)
        self.assertEqual(s1.points(p("sentence words words")), 0)

        s2 = symptoms.MinimumWordCount(3)
        self.assertEqual(s2.points(p("sentence")), 2)
        self.assertEqual(s2.points(p("sentence words")), 1)
        self.assertEqual(s2.points(p("sentence words words")), 0)
        self.assertEqual(s2.points(p("sentence words words words")), 0)


# twitchcancer.symptom.symptoms.MinimumMessageLength
class TestMinimumMessageLength(unittest.TestCase):

    # exhibited_by()
    def test_minimum_message_length_exhibited_by(self):
        s = symptoms.MinimumMessageLength()

        for k, v in messages.items():
            if k == "onechar":
                self.assertTrue(s.exhibited_by(v))
            else:
                self.assertFalse(s.exhibited_by(v))

    # points()
    def test_minimum_message_length_points(self):
        s1 = symptoms.MinimumMessageLength()
        self.assertEqual(s1.points(p("123456789012345")), 0)
        self.assertEqual(s1.points(p("1234567890")), 0)
        self.assertEqual(s1.points(p("12345")), 0)
        self.assertEqual(s1.points(p("123")), 0)
        self.assertEqual(s1.points(p("1")), 1)

        s2 = symptoms.MinimumMessageLength(10)
        self.assertEqual(s2.points(p("123456789012345")), 0)
        self.assertEqual(s2.points(p("1234567890")), 0)
        self.assertEqual(s2.points(p("12345")), 2)
        self.assertEqual(s2.points(p("123")), 3)
        self.assertEqual(s2.points(p("1")), 4)


# twitchcancer.symptom.symptoms.MaximumMessageLength
class TestMaximumMessageLength(unittest.TestCase):

    # exhibited_by()
    def test_maximum_message_length_exhibited_by(self):
        s = symptoms.MaximumMessageLength()

        for k, v in messages.items():
            if k == "longsentence":
                self.assertTrue(s.exhibited_by(v))
            else:
                self.assertFalse(s.exhibited_by(v))

    # points()
    def test_maximum_message_length_points(self):
        s1 = symptoms.MaximumMessageLength()
        self.assertEqual(s1.points(p("1234567890")), 0)
        self.assertEqual(
            s1.points(p("123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890")),
            3)

        s2 = symptoms.MaximumMessageLength(10)
        self.assertEqual(s2.points(p("1234567890")), 0)
        self.assertEqual(s2.points(p("1234567890123")), 1)
        self.assertEqual(s2.points(p("123456789012345")), 2)


# twitchcancer.symptom.symptoms.CapsRatio
class TestCapsRatio(unittest.TestCase):

    # exhibited_by()
    def test_caps_ratio_exhibited_by(self):
        s = symptoms.CapsRatio()

        for k, v in messages.items():
            if k in ["caps", "emotesandwords"]:
                self.assertTrue(s.exhibited_by(v))
            else:
                self.assertFalse(s.exhibited_by(v))

    # points()
    def test_caps_ratio_points(self):
        s1 = symptoms.CapsRatio()
        self.assertEqual(s1.points(p("Foobar")), 0)
        self.assertEqual(s1.points(p("FooBar")), 1)
        self.assertEqual(s1.points(p("FOOBAR")), 2)

        s2 = symptoms.CapsRatio(1)
        self.assertEqual(s2.points(p("FAHDASH DSAHDHAS")), 0)
        self.assertEqual(s2.points(p("DASDASDA")), 0)


# twitchcancer.symptom.symptoms.EmoteCount
class TestEmoteCount(unittest.TestCase):

    # count()
    def test_emote_count_count(self):
        self.assertEqual(symptoms.EmoteCount.count(p('Kappa')), 1)
        self.assertEqual(symptoms.EmoteCount.count(p('notanemote')), 0)
        self.assertEqual(symptoms.EmoteCount.count(p('Kappa KappaPride Keepo')), 3)

    # exhibited_by()
    def test_emote_count_exhibited_by(self):
        s = symptoms.EmoteCount()

        for k, v in messages.items():
            if k == "emotesandwords":
                self.assertTrue(s.exhibited_by(v))
            else:
                self.assertFalse(s.exhibited_by(v))

    # points()
    def test_emote_count_points(self):
        s1 = symptoms.EmoteCount()
        self.assertEqual(s1.points(p("Kappa")), 0)
        self.assertEqual(s1.points(p("Kappa KappaPride")), 1)
        self.assertEqual(s1.points(p("Kappa KappaPride Keepo")), 2)
        self.assertEqual(s1.points(p("Kappa KappaPride Keepo Keepo")), 2)
        self.assertEqual(s1.points(p("Kappa KappaPride Keepo Keepo KappaPride")), 3)

        s2 = symptoms.EmoteCount(3)
        self.assertEqual(s2.points(p("Kappa")), 0)
        self.assertEqual(s2.points(p("Kappa KappaPride Keepo")), 0)
        self.assertEqual(s2.points(p("Kappa KappaPride Keepo Keepo")), 1)
        self.assertEqual(s2.points(p("Kappa KappaPride Keepo Keepo KappaPride KappaPride")), 2)


# twitchcancer.symptom.symptoms.symptoms.EmoteRatio
class TestEmoteRatio(unittest.TestCase):

    # exhibited_by()
    def test_emote_ratio_exhibited_by(self):
        s = symptoms.EmoteRatio()

        for k, v in messages.items():
            if k == "oneemote":
                self.assertTrue(s.exhibited_by(v))
            else:
                self.assertFalse(s.exhibited_by(v))

    # points()
    def test_emote_ratio_points(self):
        s1 = symptoms.EmoteRatio()
        self.assertEqual(s1.points(p("Foo")), 0)
        self.assertEqual(s1.points(p("Kappa")), 2)
        self.assertEqual(s1.points(p("Kappa test test")), 0)
        self.assertEqual(s1.points(p("Kappa KappaPride Keepo")), 2)
        self.assertEqual(s1.points(p("Kappa KappaPride Keepo Keepo")), 2)
        self.assertEqual(s1.points(p("Kappa KappaPride Keepo Keepo KappaPride")), 2)

        s2 = symptoms.EmoteRatio(1)
        self.assertEqual(s2.points(p("Kappa")), 0)
        self.assertEqual(s2.points(p("Kappa KappaPride Keepo")), 0)
        self.assertEqual(s2.points(p("Kappa KappaPride Keepo Keepo")), 0)
        self.assertEqual(s2.points(p("Kappa KappaPride Keepo Keepo KappaPride KappaPride")), 0)


# TestEmoteCountAndRatio
class TestEmoteCountAndRatio(unittest.TestCase):

    # points()
    def test_emote_count_points(self):
        s1 = symptoms.EmoteCountAndRatio()
        self.assertEqual(s1.points(p("Kappa")), 2)
        self.assertEqual(s1.points(p("Kappa KappaPride Keepo")), 4)
        self.assertEqual(s1.points(p("Kappa KappaPride Keepo Keepo KappaPride")), 5)


# twitchcancer.symptom.symptoms.BannedPhrase
class TestBannedPhrase(unittest.TestCase):

    # exhibited_by()
    def test_banned_phrase_exhibited_by(self):
        s = symptoms.BannedPhrase()

        self.assertFalse(s.exhibited_by(p("Darude")))
        self.assertTrue(s.exhibited_by(p("Darude Sandstorm")))

    # points()
    def test_banned_phrase_points(self):
        s = symptoms.BannedPhrase()
        self.assertEqual(s.points(p("Kappa")), 0)
        self.assertEqual(s.points(p("Darude sandstorm")), 1)
        self.assertEqual(s.points(p("Darude sandstorm Darude sandstorm")), 2)
        self.assertEqual(s.points(p("Darude sandstorm message deleted")), 2)


# twitchcancer.symptom.symptoms.EchoingRatio
class TestEchoingRatio(unittest.TestCase):

    # exhibited_by()
    def test_echoing_ratio_exhibited_by(self):
        s = symptoms.EchoingRatio()

        self.assertFalse(s.exhibited_by(p("lol")))
        self.assertFalse(s.exhibited_by(p("foo bar")))
        self.assertTrue(s.exhibited_by(p("lol lol")))

    # points()
    def test_echoing_ratio_points(self):
        s = symptoms.EchoingRatio()
        self.assertEqual(s.points(p("lol")), 0)
        self.assertEqual(s.points(p("lol lol")), 1)
        self.assertEqual(s.points(p("lol lol lol")), 2)
        self.assertEqual(s.points(p("lol lol lol lol")), 2)
        self.assertEqual(s.points(p("lol rekt lol rekt")), 1)
