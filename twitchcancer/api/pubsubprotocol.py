import datetime
import json
import logging
from autobahn.asyncio.websocket import WebSocketServerProtocol

from twitchcancer.api.pubsubmanager import PubSubManager
from twitchcancer.api.requesthandler import RequestHandler

logger = logging.getLogger(__name__)


# transforms datetime into iso formatted strings
class DatetimeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


'''
  Requests:

    subscribe: {"subscribe": topic }
    unsubscribe {"unsubscribe": topic }
    request {"request": topic [, "data": something] }


  Replies:
    {
      'topic': topic
      'data': per-topic format
    }

  #topic: full path, eg twitchcancer.channel.forsenlol
'''


# implements a simple pubsub protocol
class PubSubProtocol(WebSocketServerProtocol):

    def __init__(self):
        super().__init__()

    def __str__(self):
        return self.peer

    def onConnect(self, request):  # noqa
        logger.debug('client connecting %s', self)

    def onOpen(self):  # noqa
        logger.info('opened a connection for %s', self)

    def onClose(self, wasClean, code, reason):  # noqa
        logger.info('connection closed for %s: %s', self, reason)
        PubSubManager.instance().unsubscribe_all(self)

    def onMessage(self, payload, isBinary):  # noqa
        try:
            s = json.loads(payload.decode('utf8'))
        except ValueError as e:
            logger.warning('got a bogus payload from %s: %s', self, e)
            return

        # handle subscriptions
        if 'subscribe' in s:
            PubSubManager.instance().subscribe(self, s['subscribe'])

            # respond with the latest data from this topic
            PubSubManager.instance().publish_one(self, s['subscribe'])

        # handle unsubscriptions
        if 'unsubscribe' in s:
            PubSubManager.instance().unsubscribe(self, s['unsubscribe'])

        # handle requests
        if 'request' in s:
            response = RequestHandler.instance().handle(s)
            self.send(s['request'], response)

    def send(self, topic, data):
        try:
            # prepare a stringified payload
            payload = {
                'topic': topic,
                'data': data
            }
            payload = json.dumps(payload, cls=DatetimeJSONEncoder).encode('utf8')

            self.sendMessage(payload, False)
        except Exception:
            logger.debug('got a non json topic event: %s', data)
