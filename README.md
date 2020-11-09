<p align="center">
 <img width="20%" height="20%" src="./logo.svg">
</p>

# Lambda-Log-Shipper

Ship your AWS lambda logs. The no-code style.


[![MIT](https://img.shields.io/packagist/l/doctrine/orm.svg?style=flat-square)]()
[![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)]()
[![codecov](https://codecov.io/gh/lumigo-io/lambda-log-shipper/branch/main/graph/badge.svg?token=3Sv1vOyN8W)](https://codecov.io/gh/lumigo-io/lambda-log-shipper)

- [Usage](#usage)
- [Advanced Configuration](#advanced-configuration)
- [How it works](#how-it-works)
- [Contribute](#contribute)

## Usage

Add the [latest extension](https://github.com/lumigo-io/lambda-log-shipper/LAYERS.txt) to your lambda ([read how](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html#configuration-layers-using)).

Choose a shipping method:
* S3 - Set the environment variable `LUMIGO_EXTENSION_LOG_S3_BUCKET` to your target bucket. Don't forget to add proper permissions.
* <Your next service / 3rd party method>


## Advanced Configuration

(Optional) Choose shipping parameters:
* `LUMIGO_EXTENSION_LOG_BATCH_SIZE` indicates the target size (in bytes) of each log file. We will aggregate logs to at least this size before shipping.
* `LUMIGO_EXTENSION_LOG_BATCH_TIME` indicates the target time (in milliseconds) before closing a log file. We will aggregate logs for at least this period before shipping.

Note: We will ship the logs immediately when the container is shutting down. Therefore, log files can be smaller and more frequent than the above configuration.

## How it works

We use the new extensions ([read more](https://lumigo.io/blog/aws-lambda-extensions-what-are-they-and-why-do-they-matter/)) feature to trigger a new process that handles your logs.
This process is triggered by the LambdaService with the lambda's logs, which being aggregated in-memory and transferred to your chosen shipping method.

## Contribute

Our extension is written in python3.7, and our test environment is [pytest](
https://pytest.org/) and [moto](https://github.com/spulec/moto) to test interaction AWS services.

To add another log-shipping method, open a PR with 4 file changes:
1. `src/lambda_log_shipper/handlers/your_new_handler.py` - Contains a class that extends `LogsHandler`, and implements the method: `def handle_logs(self, records: List[LogRecord]) -> bool`
2. `test/lambda_log_shipper/handlers/test_your_new_handler.py` - Contains your tests
3. Update the file `src/lambda_log_shipper/handlers/__init__.py` With an import to your class
4. `src/lambda_log_shipper/configuration.py` - Contains your new configuration properties.

You can run the tests with `./scripts/checks.sh`, which also checks linting and code convensions.

You can upload a private version of the extension with `./scripts/deploy.sh` for local testing. This script will output the ARN of your local layer.
