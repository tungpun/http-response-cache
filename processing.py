import requests

from logz import *
from config import *


def do_fetch(url, post_data, req_headers):
    logger.info(f"Fetching... {url}")
    logger.info(f"post_data: {post_data}")
    logger.info(f"req_headers: {req_headers}")

    try:
        if post_data is None:
            response = requests.get(url, timeout=HTTP_TIMEOUT, headers=req_headers)
        else:
            response = requests.post(url, timeout=HTTP_TIMEOUT, headers=req_headers, data=post_data)

    except Exception as e:
        logger.error(f"Failed to fetch {url} with exception {e}")
        return None
    
    if response.status_code == 200:
        return response.text
    else:
        logger.error(f"Failed to fetch {url} with status code {response.status_code}")
        return None
