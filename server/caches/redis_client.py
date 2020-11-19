import os

import redis

try:
    redis_cache = redis.StrictRedis(
        host=os.getenv("REDIS_HOST"),
        port=os.getenv("REDIS_PORT"),
        db=os.getenv("REDIS_CACHE_DB"),
        decode_responses=True,
    )
    cache_policy = {"lru": "allkeys-lru", "random": "allkeys-random"}
    redis_cache.config_set(name="maxmemory", value="200mb")
    redis_cache.config_set(name="maxmemory-policy", value=cache_policy["lru"])
except Exception as exc:
    print("err connecting to redis")
    raise exc
