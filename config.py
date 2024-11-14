from logz import *
from retry import retry
import os
from redis import Redis
import base64
import json

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env

REQ_RETRY_TIMES = 12
RETRY_BACKOFF = 2
RETRY_DELAY = 2
REQ_TIMEOUT = 18


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

HTTP_TIMEOUT = 10

REDIS_KEY_EXPIRE = 600  # in seconds
SLEEP_SECONDS = 60

## debugging purpose
# REDIS_KEY_EXPIRE = 30  # in seconds
# SLEEP_SECONDS = 5

IGNORE_HTTP_HEADERS = ['Host', 'Accept-Encoding', 'Connection', 'Content-Length']
