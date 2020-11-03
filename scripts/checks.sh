#!/usr/bin/env bash
set -eo pipefail

pre-commit run -a
python -m pytest --cov=src/lambda_log_shipper src/test
