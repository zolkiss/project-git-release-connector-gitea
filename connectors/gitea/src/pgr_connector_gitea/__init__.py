import logging

from pgr import create_logger, create_console_handler

log = create_logger(name=__name__, level=logging.DEBUG)
log.addHandler(create_console_handler(level=logging.DEBUG))

from pgr_connector_gitea.gitea_connector import GiteaConnector

__all__ = ["GiteaConnector", "log"]
