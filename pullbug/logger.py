import logging
import logging.handlers
import os

PULLBUG_LOCATION = os.path.expanduser(
    os.getenv('PULLBUG_LOCATION', '~/pullbug')
)
LOG_PATH = os.path.join(PULLBUG_LOCATION, 'logs')
LOG_FILE = os.path.join(LOG_PATH, 'pullbug.log')


class PullBugLogger():
    @classmethod
    def _setup_logging(cls, logger):
        """Setup project logging (to console and log file).
        """
        if not os.path.exists(LOG_PATH):
            os.makedirs(LOG_PATH)
        logger.setLevel(logging.INFO)
        handler = logging.handlers.RotatingFileHandler(
            LOG_FILE,
            maxBytes=200000,
            backupCount=5
        )
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(logging.StreamHandler())
        logger.addHandler(handler)
