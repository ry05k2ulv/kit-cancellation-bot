from logging import basicConfig, getLogger


def get_logger(name):
    basicConfig()
    logger = getLogger(name)
    logger.setLevel("DEBUG")
    return logger
