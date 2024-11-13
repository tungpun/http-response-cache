import requests

from logz import *
from config import *


def do_fetch(url):
    logger.info(f"Fetching... {url}")

    try:
        response = requests.get(url, timeout=HTTP_TIMEOUT)
    except Exception as e:
        logger.error(f"Failed to fetch {url} with exception {e}")
        return None
    
    if response.status_code == 200:
        return response.text
    else:
        logger.error(f"Failed to fetch {url} with status code {response.status_code}")
        return None
