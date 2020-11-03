from lambda_log_shipper.utils import never_fail


def test_never_fail(caplog):
    with never_fail("test"):
        raise ValueError()

    # No exception raised
    assert caplog.records[0].levelname == "ERROR"
    assert caplog.records[0].exc_info[0] == ValueError
