import logging
import pytest


@pytest.fixture(autouse=True)
def log_all(caplog):
    caplog.set_level(logging.DEBUG)


@pytest.fixture(autouse=True)
def extension_env(monkeypatch):
    monkeypatch.setenv("AWS_LAMBDA_RUNTIME_API", "127.0.0.1")


@pytest.fixture
def raw_record():
    return {'time': '2020-11-02T12:02:04.575Z', 'type': 'platform.start', 'record': {'requestId': '1-2-3-4', 'version': '$LATEST'}}
