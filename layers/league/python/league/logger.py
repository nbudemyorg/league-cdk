import logging
import os
import sys


def create_logger(logger_name: str) -> logging.Logger:
    env_level = os.getenv('LOG_LEVEL', 'INFO')
    log_level = logging.getLevelName(env_level)
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    logger.propagate = False
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
