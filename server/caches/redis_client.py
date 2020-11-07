import os

import redis

redis_cache = redis.StrictRedis(
    host=os.getenv("REDIS_HOST", "0.0.0.0"),
    port=os.getenv("REDIS_PORT", "6379"),
    db=os.getenv("REDIS_CACHE_DB", 0),
    decode_responses=True,
)
cache_policy = {"lru": "allkeys-lru", "random": "allkeys-random"}
redis_cache.config_set(name="maxmemory", value="200mb")
redis_cache.config_set(name="maxmemory-policy", value=cache_policy["lru"])
