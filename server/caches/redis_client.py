import os

import redis

REDIS_CACHE_POLICIES = {"lru": "allkeys-lru", "random": "allkeys-random"}
REDIS_MAX_MEM = "200mb"


def get_redis_client():
    rc = redis.StrictRedis(
        host=os.getenv("REDIS_HOST"),
        port=os.getenv("REDIS_PORT"),
        db=os.getenv("REDIS_CACHE_DB"),
        decode_responses=True,
    )
    rc.config_set(name="maxmemory", value=REDIS_MAX_MEM)
    rc.config_set(
        name="maxmemory-policy", value=REDIS_CACHE_POLICIES.get("lru", "random")
    )
    return rc
