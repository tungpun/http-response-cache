from requests import post
from logz import *
from config import *
import processing
import time


redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def start_a_round():
    logger.info("Starting a round...")
    keys = redis.keys('*')
    for selected_key in keys:
        if selected_key.startswith("base64_url:"):
            
            redis_main_key = selected_key[len("base64_url:"):]
            logger.info(f"Processing {redis_main_key}")

            base64_url = redis.get(f"base64_url:{redis_main_key}")
            url = base64.b64decode(base64_url).decode('utf-8')

            # unpact the post_data and req_headers
            post_data = redis.get(f"post_data:{redis_main_key}")
            req_headers_in_string = redis.get(f"headers:{redis_main_key}")
            req_headers = {}
            if req_headers_in_string:
                req_headers = json.loads(req_headers_in_string)

            response = processing.do_fetch(url, post_data, req_headers)

            if response is not None:
                logger.info(f"Setting keys for {redis_main_key} in the DB")
                redis.set(f'response:{redis_main_key}', response, ex=REDIS_KEY_EXPIRE)  # set the response in the redis
                redis.set(f"base64_url:{redis_main_key}", base64_url, ex=REDIS_KEY_EXPIRE)  # refresh the expire time for the url
                if post_data:
                    redis.set(f"post_data:{redis_main_key}", post_data, ex=REDIS_KEY_EXPIRE)  # refresh the expire time for post_data
                if req_headers_in_string != {}:
                    redis.set(f"headers:{redis_main_key}", req_headers_in_string, ex=REDIS_KEY_EXPIRE)  # refresh the expire time for headers
            else:
                logger.error(f"Failed to fetch {url}")
        time.sleep(RETRY_DELAY)
    logger.info("Round finished")
    

if __name__ == "__main__":
    logger.info("Starting the app...")
    while True:
        start_a_round()
        time.sleep(SLEEP_SECONDS)
    
