import logging
from utils.constants import APP_NAME


class AppLogger:
    _logger = None

    @staticmethod
    def get_logger():
        if AppLogger._logger is None:
            # Configure logger
            logging.basicConfig(level=logging.INFO,
                                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')
            AppLogger._logger = logging.getLogger(APP_NAME)
        return AppLogger._logger


logger = AppLogger.get_logger()
