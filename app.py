from flask import Flask, jsonify, request

from logz import *
from config import *
import processing


app = Flask(__name__)

redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@app.route("/")
def hello():
    return "<h1>Hello, World!</h1>"


@app.route("/fetch")
def resp_cache():
    base64_url = request.args.get('base64_url')
    if not base64_url:
        return jsonify({"error": "Missing base64_url parameter"}), 400
    
    redis_key = f'base64_url:{base64_url}'
    redis_value = redis.get(redis_key)

    if redis_value is None:
        logger.info(f"{redis_key} doesn't exist in the DB")
        
        url = base64.b64decode(base64_url).decode('utf-8')
        response = processing.do_fetch(url)
        if response is not None:            
            redis.set(redis_key, response, ex=REDIS_KEY_EXPIRE)
    else:
        logger.info(f"{redis_key} exists in the DB")
        response = redis_value
    
    if response is None:
        return jsonify({"error": "Failed to fetch the URL"})
            
    return response
