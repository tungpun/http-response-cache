from flask import Flask, jsonify, request

from logz import *
from config import *
import processing
import hashlib


app = Flask(__name__)

redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@app.route("/")
def hello():
    return "<h1>Hello, World!</h1>"


def compose_the_redis_key(base64_url, headers_in_string, post_data_in_bytes):
    post_data_in_string = post_data_in_bytes.decode('utf-8') if post_data_in_bytes is not None else ""
    key_to_be_hashed = f"{base64_url}-{headers_in_string}-{post_data_in_string}"
    hash_string_sha256 = hashlib.sha256(key_to_be_hashed.encode()).hexdigest()
    return hash_string_sha256


@app.route("/fetch", methods=["GET", "POST"])
def resp_cache():
    base64_url = request.args.get('base64_url')
    if not base64_url:
        return jsonify({"error": "Missing base64_url parameter"}), 400
    
    if request.method == "POST":
        post_data_in_bytes = request.data
    else:
        post_data_in_bytes = None

    req_headers = {}
    for key, value in request.headers:
        if key not in IGNORE_HTTP_HEADERS:
            req_headers[key] = value
    headers_in_string = json.dumps(req_headers)

    redis_main_key = compose_the_redis_key(base64_url, req_headers, post_data_in_bytes)

    logger.info("The main key for url {} is {}".format(base64_url, redis_main_key))
    
    # set URL, post_data, headers in the redis
    redis.set(f"base64_url:{redis_main_key}", base64_url, ex=REDIS_KEY_EXPIRE)
    if post_data_in_bytes is not None:
        redis.set(f"post_data:{redis_main_key}", post_data_in_bytes, ex=REDIS_KEY_EXPIRE)
    if req_headers != {}:
        redis.set(f"headers:{redis_main_key}", headers_in_string, ex=REDIS_KEY_EXPIRE)

    # check if the response exists in the redis
    redis_key_response = f'response:{redis_main_key}'
    redis_value_respone = redis.get(redis_key_response)
    if redis_value_respone is None:
        logger.info(f"{redis_main_key} doesn't exist in the DB")
        url = base64.b64decode(base64_url).decode('utf-8')
        response = processing.do_fetch(url, post_data_in_bytes, req_headers)
        if response is not None:            
            redis.set(redis_key_response, response, ex=REDIS_KEY_EXPIRE)
        else:
            return jsonify({"error": "Failed to fetch the URL"})
    else:
        logger.info(f"{redis_key_response} exists in the DB")
        response = redis_value_respone
                
    return response
