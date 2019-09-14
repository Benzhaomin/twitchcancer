import logging
import requests

from twitchcancer.config import Config

logger = logging.getLogger(__name__)


class TwitchApi:

    @classmethod
    def stream_list(cls) -> dict:
        """ Returns a list of the top 100 streams, sorted by viewer count
        """
        url = 'https://api.twitch.tv/kraken/streams/?limit=100'
        return cls.request(url)

    @classmethod
    def request(cls, url: str) -> dict:
        """ Makes a call to Twitch's API
        """
        headers = {
            'Accept': 'application/vnd.twitchtv.v5+json',
            'Client-ID': Config.get('monitor.chat.clientid'),
            'User-agent': 'twitchcancer/python'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
