import logging
import os
from datetime import datetime


class Logger:
    @staticmethod
    def get_logger():
        if not os.path.exists("logs"):
            os.makedirs("logs")

        logger = logging.getLogger("99acres-framework")
        logger.setLevel(logging.INFO)

        if logger.handlers:
            return logger

        log_filename = datetime.now().strftime("logs/test_%Y-%m-%d.log")
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        file_handler = logging.FileHandler(log_filename)
        file_handler.setFormatter(formatter)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        return logger

