from dataclasses import asdict
import datetime
import pytest

from moto import mock_s3
import boto3

from lambda_log_shipper.handlers.base_handler import LogRecord, LogType
from lambda_log_shipper.handlers.s3_handler import S3Handler
from lambda_log_shipper.configuration import Configuration


@pytest.fixture(autouse=True)
def lambda_name(monkeypatch):
    monkeypatch.setenv("AWS_LAMBDA_FUNCTION_NAME", "func")


def test_generate_key_name(record):
    t1 = datetime.datetime(2020, 5, 22, 10, 20, 30)
    r1 = LogRecord(**{**asdict(record), "log_time": t1})
    t2 = datetime.datetime(2020, 5, 22, 10, 20, 35)
    r2 = LogRecord(**{**asdict(record), "log_time": t2})

    key = S3Handler.generate_key_name([r1, r2])

    assert key.startswith("logs/2020/5/22/10/func/20:30:0-")


def test_format_records(record):
    t1 = datetime.datetime(2020, 5, 22, 10, 20, 30, 123456)
    r1 = LogRecord(log_type=LogType.START, log_time=t1, record="a")
    r2 = LogRecord(log_type=LogType.FUNCTION, log_time=t1, record="b")

    data = S3Handler.format_records([r1, r2])

    expected = "2020-05-22T10:20:30.123456    START     a\n2020-05-22T10:20:30.123456    FUNCTION  b"
    assert data.decode() == expected


@mock_s3
def test_handle_logs_happy_flow(record, monkeypatch):
    s3 = boto3.client("s3", region_name="us-west-2")
    monkeypatch.setattr(Configuration, "s3_bucket_arn", "123")
    s3.create_bucket(
        Bucket="123", CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
    )

    t1 = datetime.datetime(2020, 5, 22, 10, 20, 30, 123456)
    r1 = LogRecord(log_type=LogType.START, log_time=t1, record="a")

    assert S3Handler().handle_logs([r1])

    key_name = s3.list_objects(Bucket=Configuration.s3_bucket_arn)["Contents"][0]["Key"]
    obj = s3.get_object(Key=key_name, Bucket=Configuration.s3_bucket_arn)
    assert obj["Body"].read().decode() == "2020-05-22T10:20:30.123456    START     a"


@mock_s3
def test_handle_logs_no_config(monkeypatch, record):
    assert not S3Handler().handle_logs([record])  # no exception
