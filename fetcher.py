from logz import *
from config import *
import processing
import time


redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def start_a_round():
    logger.info("Starting a round...")
    keys = redis.keys('*')
    for key in keys:
        if key.startswith("base64_url:"):
            logger.info(f"Key: {key}")
            base64_url = key[len("base64_url:"):]
            url = base64.b64decode(base64_url).decode('utf-8')
            response = processing.do_fetch(url)
            if response is not None:
                logger.info(f"Setting {key} in the DB")
                redis.set(key, response, ex=REDIS_KEY_EXPIRE)
            else:
                logger.error(f"Failed to fetch {url}")
        time.sleep(RETRY_DELAY)
    logger.info("Round finished")
    

if __name__ == "__main__":
    logger.info("Starting the app...")
    while True:
        start_a_round()
        time.sleep(SLEEP_SECONDS)
    
