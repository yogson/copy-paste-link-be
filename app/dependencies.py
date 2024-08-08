import redis

from app.config import redis_host, redis_port


def get_redis_client() -> redis.client.Redis:
    return redis.Redis(host=redis_host, port=redis_port, db=1)
