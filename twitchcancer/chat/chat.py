import logging

from twitchcancer.chat.websocket.monitor import AsyncWebSocketMonitor

logger = logging.getLogger(__name__)


# profiling: import yappi

def run(args):
    # profiling: yappi.start()

    monitor = AsyncWebSocketMonitor(viewers=args.viewers)
    monitor.run()

    # profiling: yappi.get_func_stats().print_all()
    # profiling: yappi.get_thread_stats().print_all()
