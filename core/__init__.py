import logging

from .config import LOGFORMAT, LOGFILE, DEBUG

log_level = logging.INFO
if DEBUG:
    log_level = logging.DEBUG
logging.basicConfig(format=LOGFORMAT,
                    level=log_level,
                    filename=LOGFILE)

log_formatter = logging.Formatter(LOGFORMAT)
logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)
logging.getLogger().addHandler(stream_handler)