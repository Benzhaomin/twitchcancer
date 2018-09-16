import logging
import pickle
import zmq

from twitchcancer.config import Config
from twitchcancer.storage.persistentstore import PersistentStore
from twitchcancer.storage.storageinterface import StorageInterface

logger = logging.getLogger(__name__)


#
# keep leaderboards up-to-date with new data from the monitoring process
#
# implements:
#  - storage.record()
class WriteOnlyStorage(StorageInterface):

    def __init__(self):
        super().__init__()

        self._store = PersistentStore()

        # subscribe to summaries from the publisher socket
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.setsockopt(zmq.SUBSCRIBE, b'summary')
        self.socket.connect(Config.get('monitor.socket.cancer_summary'))
        logger.info("connected summary socket to %s", Config.get('monitor.socket.cancer_summary'))

    # start listening for summaries to persist
    # @socket.recv()
    # @db.write()
    def record(self):
        # update leaderboards with summaries we receive (one per channel per minute)
        while True:
            [topic, msg] = self.socket.recv_multipart()
            summary = pickle.loads(msg)
            self._store.update_leaderboard(summary)


# TODO: add proper unit testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    storage = WriteOnlyStorage()
