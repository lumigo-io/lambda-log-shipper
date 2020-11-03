import pytest

from lambda_log_shipper.configuration import parse_env, parse_env_to_int


def test_parse_env_exists(monkeypatch):
    monkeypatch.setenv("ENV_VAR", "a")
    assert parse_env("ENV_VAR", "default") == "a"


def test_parse_env_not_exists(monkeypatch):
    monkeypatch.delenv("ENV_VAR", None)
    assert parse_env("ENV_VAR", "default") == "default"


@pytest.mark.parametrize(
    "actual_env, expected_result",
    [
        ("3", 3),
        ("a", 5),
    ],
)
def test_parse_env_to_int_exists(actual_env, expected_result, monkeypatch):
    monkeypatch.setenv("ENV_VAR", actual_env)
    assert parse_env_to_int("ENV_VAR", 5) == expected_result


def test_parse_env_to_int_not_exists(monkeypatch):
    monkeypatch.delenv("ENV_VAR", None)
    assert parse_env_to_int("ENV_VAR", 5) == 5
