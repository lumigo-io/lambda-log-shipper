import setuptools

setuptools.setup(
    name="lambda_log_shipper",
    version="0.1",
    author="Lumigo LTD (https://lumigo.io)",
    author_email="support@lumigo.io",
    description="Ship logs from AWS lambdas with ease",
    long_description_content_type="text/markdown",
    url="https://github.com/lumigo-io/lambda-log-shipper.git",
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    install_requires=["urllib3==1.26.5", "pytest-cov", "pytest", "boto3", "moto"],
    license="Apache License 2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
