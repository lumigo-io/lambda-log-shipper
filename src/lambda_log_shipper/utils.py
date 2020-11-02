import os
import http
import logging

_logger = None

LOG_SUBSCRIBER_PORT = 1060
LUMIGO_EXTENSION_NAME = "logs"
HEADERS_ID_KEY = "Lambda-Extension-Identifier"
HEADERS_NAME_KEY = "Lambda-Extension-Name"


def get_logger():
    global _logger
    if not _logger:
        _logger = logging.getLogger("lambda-log-shipper")
        handler = logging.StreamHandler()
        if os.environ.get("LOG_SHIPPER_DEBUG", "").lower() == "true":
            _logger.setLevel(logging.DEBUG)
            handler.setLevel(logging.DEBUG)
        _logger.addHandler(handler)
    return _logger


def lambda_service():
    return http.client.HTTPConnection(os.environ["AWS_LAMBDA_RUNTIME_API"])
