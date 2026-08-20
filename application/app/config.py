import os


APP_NAME = os.getenv(
    "APP_NAME",
    "Order Management API",
)

APP_VERSION = os.getenv(
    "APP_VERSION",
    "1.0.0",
)

APP_ENV = os.getenv(
    "APP_ENV",
    "development",
)