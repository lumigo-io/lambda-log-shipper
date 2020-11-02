import os

import setuptools

VERSION_PATH = os.path.join(os.path.dirname(__file__), "src", "lumigo_tracer", "VERSION")

setuptools.setup(
    name="lambda_log_shipper",
    version='0.1',
    author="Lumigo LTD (https://lumigo.io)",
    author_email="support@lumigo.io",
    description="Ship logs from AWS lambdas with ease",
    long_description_content_type="text/markdown",
    url="https://github.com/lumigo-io/python_tracer.git",
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    install_requires=["pytest"],
    license="Apache License 2.0",
    classifiers=["Programming Language :: Python :: 3", "Operating System :: OS Independent"],
)
