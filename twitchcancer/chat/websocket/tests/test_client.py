import unittest

from twitchcancer.chat.websocket.client import TwitchClient


class TestTwitchClientParseMessage(unittest.TestCase):

    def test_not_a_message(self):
        parsed = TwitchClient.parse_message(
            '@broadcaster-lang=;r9k=0;slow=0;subs-only=1 :tmi.twitch.tv ROOMSTATE #sc2proleague\n')
        self.assertEqual(parsed, None)

    def test_simple(self):
        parsed = TwitchClient.parse_message('@color=#FF69B4;display-name=Mancowbeaar;emotes=60257:0-6/28087:8-14;'
                                            'subscriber=1;turbo=0;user-type= :mancowbeaar!mancowbeaar@mancowbeaar.'
                                            'tmi.twitch.tv PRIVMSG #forsenlol :forsenX WutFace\n')
        self.assertEqual(parsed['channel'], "#forsenlol")
        self.assertEqual(parsed['message'], "forsenX WutFace")

    def test_extraneous_colon(self):
        parsed = TwitchClient.parse_message('@color=#FF69B4;display-name=Mancowbeaar;emotes=60257:0-6/28087:8-14;'
                                            'subscriber=1;turbo=0;user-type= :mancowbeaar!mancowbeaar@mancowbeaar.'
                                            'tmi.twitch.tv PRIVMSG #forsenlol :forsenX :extraneous colon WutFace\n')
        self.assertEqual(parsed['channel'], "#forsenlol")
        self.assertEqual(parsed['message'], "forsenX :extraneous colon WutFace")

    def test_command_in_message(self):
        parsed = TwitchClient.parse_message('@color=#FF69B4;display-name=Mancowbeaar;emotes=60257:0-6/28087:8-14;'
                                            'subscriber=1;turbo=0;user-type= :mancowbeaar!mancowbeaar@mancowbeaar.'
                                            'tmi.twitch.tv PRIVMSG #forsenlol :forsenX PRIVMSG WutFace\n')
        self.assertEqual(parsed['channel'], "#forsenlol")
        self.assertEqual(parsed['message'], "forsenX PRIVMSG WutFace")

    def test_action_message(self):
        parsed = TwitchClient.parse_message('@color=#FF69B4;display-name=Mancowbeaar;emotes=60257:0-6/28087:8-14;'
                                            'subscriber=1;turbo=0;user-type= :mancowbeaar!mancowbeaar@mancowbeaar.'
                                            'tmi.twitch.tv PRIVMSG #forsenlol :\x01ACTION forsenX WutFace\x01\n')
        self.assertEqual(parsed['channel'], "#forsenlol")
        self.assertEqual(parsed['message'], "forsenX WutFace")
