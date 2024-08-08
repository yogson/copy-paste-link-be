import random

from redis.client import Redis

from app.dependencies import get_redis_client


def make_onetime_key(uid_key: str):
    return f"{uid_key}_onetime"


def make_short_code_subkey_for(*, key: str):
    redis_client = get_redis_client()
    is_clean_key = False
    while not is_clean_key:
        subkey = ''.join(random.choices('0123456789', k=4))
        is_clean_key = redis_client.set(name=subkey, value=key, nx=True)
    return subkey


def get_text_by_id(text_id: str, redis_client: Redis):
    text, is_one_time = redis_client.mget(keys=(text_id, make_onetime_key(text_id)))
    is_one_time = bool(int(is_one_time)) if is_one_time is not None else None
    if text and is_one_time:
        redis_client.delete(text_id)
    return text
