import logging

logging.basicConfig(level=logging.DEBUG)


_log_format = """%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"""


def _get_file_handler(log_file):
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler


def _get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler


def get_logger(name, log_file="extraction.log"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(_get_file_handler(log_file))
    logger.addHandler(_get_stream_handler())
    return logger
