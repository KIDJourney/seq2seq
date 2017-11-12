import signal
import inspect
from logger import logger

signal_handlers = []
RUNNING = False
FINISH_SAVE = False


def handle_inter(sign, frame):
    if FINISH_SAVE:
        exit()


def add_signal_handler(func):
    if not inspect.isfunction(func):
        logger.warning("try to add non function object=%s", func)
        return

    signal_handlers.append(func)


def init_script():
    for handler in signal_handlers:
        signal.signal(signal.SIGINT, handler)
    RUNNING = True
