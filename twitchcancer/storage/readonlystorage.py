import logging
import zmq

from twitchcancer.config import Config
from twitchcancer.storage.persistentstore import PersistentStore
from twitchcancer.storage.storageinterface import StorageInterface

logger = logging.getLogger(__name__)


#
# expose the entire model: read data, from the persistent and in-memory stores
#
# implements:
#  - storage.channel()
#  - storage.cancer()
#  - storage.leaderboards()
#  - storage.leaderboard()
#  - storage.status()
#  - storage.search()
class ReadOnlyStorage(StorageInterface):

    def __init__(self):
        super().__init__()

        self._store = PersistentStore()

        # request cancer levels
        self.context = zmq.Context()
        self.poller = zmq.Poller()
        self._connect()

    # request cancer level from a live message store
    # @socket.read()
    def cancer(self):
        self.socket.send(b'')

        if self.poller.poll(2 * 1000):  # 2s timeout in milliseconds
            return self.socket.recv_pyobj()
        else:
            logger.warning("no reply to a live cancer request, will reconnect")
            self._disconnect()
            self._connect()
            return []

    # read leaderboards from the database
    # @db.read()
    def leaderboards(self, horizon):
        return self._store.leaderboards(horizon)

    # returns a full leaderboard
    # @db.read()
    def leaderboard(self, leaderboard):
        return self._store.leaderboard(leaderboard)

    # read channel data from the database
    # @db.read()
    def channel(self, channel):
        return self._store.channel(channel)

    # returns an overview of the current status of both the db and the monitoring process
    # @db.read()
    # @socket.read()
    def status(self):
        # get totals from the database
        status = {
            'total': self._store.status(),
            'live': {
                'channels': 0,
                'messages': 0,
                'cancer': 0,
            }
        }

        # get live cancer levels
        live = self.cancer()

        # add up current cancer levels to have stats
        for channel in live:
            status['live']['messages'] += channel['messages']
            status['live']['cancer'] += channel['cancer']
        status['live']['channels'] = len(live)

        return status

    # search for a channel by its name
    # @db.read()
    def search(self, channel):
        return self._store.search(channel)

    # create a socket and connect to the cancer server
    # @socket.connect()
    def _connect(self):
        self.socket = self.context.socket(zmq.REQ)
        read_socket = Config.get('monitor.socket.read.cancer_request') or Config.get('monitor.socket.cancer_request')
        self.socket.connect(read_socket)
        self.poller.register(self.socket, zmq.POLLIN)

        logger.info("connected cancer request socket to %s", read_socket)

    # disconnect from the cancer server
    # @socket.close()
    def _disconnect(self):
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.close()
        self.poller.unregister(self.socket)
