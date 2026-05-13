import logging
import os


def get_logger() -> logging.Logger:
    env_level = os.getenv('LOG_LEVEL', 'INFO')
    log_level = logging.getLevelName(env_level)
    preconfigured_root_logger = logging.getLogger()
    preconfigured_root_logger.setLevel(log_level)

    return preconfigured_root_logger
