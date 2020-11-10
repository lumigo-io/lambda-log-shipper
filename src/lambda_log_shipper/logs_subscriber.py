from http.server import HTTPServer, BaseHTTPRequestHandler
from concurrent.futures.thread import ThreadPoolExecutor
import json

from lambda_log_shipper.logs_manager import LogsManager
from lambda_log_shipper.utils import (
    LOG_SUBSCRIBER_PORT,
    HEADERS_ID_KEY,
    lambda_service,
    get_logger,
    never_fail,
)


LOG_SUBSCRIPTION_REQUEST = {
    "destination": {
        "protocol": "HTTP",
        "URI": f"http://sandbox:{LOG_SUBSCRIBER_PORT}",
    },
    "types": ["platform", "function"],
}
TIMEOUT_SAFETY_GAP = 0.5


def subscribe_to_logs(extension_id):
    server = HTTPServer(("0.0.0.0", LOG_SUBSCRIBER_PORT), LogsHttpRequestHandler)
    server.server_activate()
    ThreadPoolExecutor().submit(server.serve_forever)

    body = json.dumps(LOG_SUBSCRIPTION_REQUEST)
    conn = lambda_service()
    conn.request(
        "PUT", "/2020-08-15/logs", body, headers={HEADERS_ID_KEY: extension_id}
    )


class LogsHttpRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        with never_fail("parse logs event"):
            size = int(self.headers.get("Content-Length", "0"))
            records = json.loads(self.rfile.read(size))
            get_logger().info(records)
            LogsManager.get_manager().add_records(records)
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):
        # Do not write console logs per request
        return
