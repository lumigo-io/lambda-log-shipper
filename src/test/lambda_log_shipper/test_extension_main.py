import http
from http.server import HTTPServer

import pytest
import time
from types import SimpleNamespace
import urllib
from unittest.mock import Mock

from lambda_log_shipper.extension_main import register_extension, extension_loop, main


@pytest.fixture
def register_mock(monkeypatch):
    mock = Mock()
    mock("127.0.0.1").getresponse.return_value = SimpleNamespace(
        headers={"Lambda-Extension-Identifier": "eid"}, read=lambda: ""
    )
    monkeypatch.setattr(http.client, "HTTPConnection", mock)


@pytest.fixture
def next_event_mock(monkeypatch):
    http_mock = Mock()
    monkeypatch.setattr(urllib.request, "urlopen", lambda *args: http_mock)
    return http_mock.read


def test_register_happy_flow(register_mock):
    result = register_extension()
    assert result == "eid"


def test_extension_loop_happy_flow(next_event_mock):
    """
    This test checks the case of two requests and shutdown.
    """
    deadline = time.time() * 1000
    next_event_mock.side_effect = [
        f'{{"eventType": "INVOKE", "requestId": "1", "deadlineMs": {deadline}}}',
        f'{{"eventType": "INVOKE", "requestId": "2", "deadlineMs": {deadline}}}',
        f'{{"eventType": "SHUTDOWN", "deadlineMs": {deadline}}}',
    ]

    extension_loop("eid")  # finishes successfully

    assert next_event_mock.call_count == 3


def test_main(monkeypatch, register_mock, next_event_mock):
    monkeypatch.setattr(HTTPServer, "serve_forever", lambda: None)
    monkeypatch.setattr(HTTPServer, "server_bind", lambda _: None)
    next_event_mock.side_effect = ['{"eventType": "SHUTDOWN", "deadlineMs": 1}']

    main()

    assert next_event_mock.call_count == 1
