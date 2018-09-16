import datetime
import logging

logger = logging.getLogger(__name__)


# represents a topic, roughly a data type/view on the model accessible on the socket
class PubSubTopic:
    # keep track of all instances to be able to find them by name later
    # TODO: have any other mechanism handle that job (pass object, singleton, etc)
    instances = set()

    # init a PubSubTopic with its name, callback to get data from and sleep duration between cycles
    def __init__(self, name, callback, sleep):
        self.name = name
        self.callback = callback
        self.sleep = sleep
        self.data = None

        # TODO: remove on destroy
        PubSubTopic.instances.add(self)

    # evaluates to the path (eg. "twitchcancer.live")
    def __str__(self):
        return self.name

    # topics are uniquely identified by their name
    def __eq__(self, other):
        return self.name == other.name

    # see __eq__
    def __neq__(self, other):
        return self.name != other.name

    # see __eq__
    def __hash__(self):
        return hash(self.name)

    # find a topic by name
    @staticmethod
    def find(name):
        for t in PubSubTopic.instances:
            if t.match(name):
                return t
        logger.warning('no result in find(%s)', name)
        return None

    # check whether name is the name of this topic
    def match(self, name):
        return self.name == name

    # return the topic's current data from cache or freshly computed
    def payload(self, use_cache=False, **kwargs):
        if not use_cache \
                or self.data is None \
                or (datetime.datetime.now() - self.data["date"]).total_seconds() > 60:
            self.data = {
                "data": self.callback(),
                "date": datetime.datetime.now()
            }
        return self.data["data"]


# represents a topic where the last part of the path is variable
class PubSubVariableTopic(PubSubTopic):

    def __init__(self, name, callback, sleep):
        super().__init__(name, callback, sleep)

        # cached data can belong to multiple topics depending on our variable
        self.data = {}

        if not self.name.endswith(".*") or len(self.name) < 3:
            raise NotImplementedError("regexp topics must end with a variable part")

    # checks whether name is like the name of this topic
    def match(self, name):
        return name.startswith(self.name.replace("*", ""))

    # return the variable part of the path
    def argument(self, name):
        return name[len(self.name.replace("*", "")):]

    # return the topic's current data from cache or freshly computed
    def payload(self, use_cache=False, **kwargs):
        name = kwargs["name"]
        if not use_cache \
                or name not in self.data \
                or (datetime.datetime.now() - self.data[name]["date"]).total_seconds() > 60:
            self.data[kwargs["name"]] = {
                "data": self.callback(self.argument(name)),
                "date": datetime.datetime.now()
            }

        return self.data[name]["data"]
