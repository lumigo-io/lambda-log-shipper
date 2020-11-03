import os
import json
import urllib.request

from lambda_log_shipper.logs_manager import LogsManager
from lambda_log_shipper.logs_subscriber import wait_for_logs, subscribe_to_logs
from lambda_log_shipper.utils import (
    get_logger,
    lambda_service,
    LUMIGO_EXTENSION_NAME,
    HEADERS_NAME_KEY,
    HEADERS_ID_KEY,
    never_fail,
)


EVENTS = ["INVOKE", "SHUTDOWN"]
EXTENSION_SHUTDOWN_LIMIT = 1


def register_extension() -> str:
    body = json.dumps({"events": EVENTS})
    headers = {HEADERS_NAME_KEY: LUMIGO_EXTENSION_NAME}

    conn = lambda_service()
    conn.request("POST", "/2020-01-01/extension/register", body, headers=headers)
    extension_id = conn.getresponse().headers["Lambda-Extension-Identifier"]
    get_logger().debug(f"Extension registered with id {extension_id}")
    return extension_id


def extension_loop(extension_id):
    url = (
        f"http://{os.environ['AWS_LAMBDA_RUNTIME_API']}/2020-01-01/extension/event/next"
    )
    req = urllib.request.Request(url, headers={HEADERS_ID_KEY: extension_id})
    while True:
        event = json.loads(urllib.request.urlopen(req).read())
        with never_fail("wait for logs"):
            get_logger().debug(f"Extension got event {event}")
            wait_for_logs(event["deadlineMs"])  # TODO: AWS have bug with this key
        if event.get("eventType") == "SHUTDOWN":
            with never_fail("send final batch"):
                LogsManager.get_manager().send_batch()
            break


def main():
    extension_id = register_extension()
    subscribe_to_logs(extension_id)
    extension_loop(extension_id)


if __name__ == "__main__":
    main()
