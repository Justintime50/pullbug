import logging
import logging.handlers
import os


class PullBugLogger:
    def _setup_logging(self, logger):
        """Setup project logging (to console and log file)."""
        log_path = os.path.join(self.location, 'logs')
        log_file = os.path.join(log_path, 'pullbug.log')

        if not os.path.exists(log_path):
            os.makedirs(log_path)

        logger.setLevel(logging.INFO)
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=200000,
            backupCount=5,
        )
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(logging.StreamHandler())
        logger.addHandler(handler)
