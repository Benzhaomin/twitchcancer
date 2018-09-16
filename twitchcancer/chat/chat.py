import logging

logger = logging.getLogger(__name__)


# profiling: import yappi

def run(args):
    # profiling: yappi.start()

    if args.protocol == 'irc':
        from twitchcancer.chat.irc.threaded import ThreadedIRCMonitor
        monitor = ThreadedIRCMonitor(viewers=args.viewers)
    else:
        from twitchcancer.chat.websocket.monitor import AsyncWebSocketMonitor
        monitor = AsyncWebSocketMonitor(viewers=args.viewers)

    monitor.run()

    # profiling: yappi.get_func_stats().print_all()
    # profiling: yappi.get_thread_stats().print_all()
