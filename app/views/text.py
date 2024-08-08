from fastapi import APIRouter, HTTPException, Depends

import uuid

from redis.client import Redis
from starlette.requests import Request

from app.config import max_text_length
from app.dependencies import get_redis_client
from app.helpers import make_onetime_key, make_short_code_subkey_for, get_text_by_id
from app.limit import limiter
from app.models import TextItem

text_router = APIRouter()


@text_router.post("/")
@limiter.limit("5/minute")
async def send_text(request: Request, item: TextItem, redis_client: Redis = Depends(get_redis_client)):
    try:
        if len(item.text) > max_text_length:
            raise HTTPException(status_code=400, detail="Text is too long")
        text_id = str(uuid.uuid4())
        data = {
            text_id: item.text,
            make_onetime_key(text_id): 1 if item.one_time else 0
        }
        short_code = None
        if item.short_code:
            short_code = make_short_code_subkey_for(key=text_id)
            data.update(short_code=short_code)
            redis_client.expire(short_code, 60)

        redis_client.mset(data)
        redis_client.expire(text_id, 3600 * 24)
        return {"id": text_id} | ({"short_code": short_code} if short_code else {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@text_router.get("/{text_id}")
@limiter.limit("15/minute")
async def get_text(request: Request, text_id: str, redis_client: Redis = Depends(get_redis_client)):
    try:
        text = get_text_by_id(text_id=text_id, redis_client=redis_client)
        if text is None:
            raise HTTPException(status_code=404, detail="Text not found")
        return {"text": text.decode('utf-8')}
    except Exception as e:
        if not isinstance(e, HTTPException):
            raise HTTPException(status_code=500, detail=str(e))
        raise e


@text_router.get("/by-code/{code}")
@limiter.limit("15/minute")
async def get_text_by_code(request: Request, code: str, redis_client: Redis = Depends(get_redis_client)):
    try:
        key = redis_client.get(name=code)
        if key is None:
            raise HTTPException(status_code=404, detail="Text not found")
        text = get_text_by_id(text_id=key, redis_client=redis_client)
        if text is None:
            raise HTTPException(status_code=404, detail="Text not found")
        return {"text": text.decode('utf-8')}
    except Exception as e:
        if not isinstance(e, HTTPException):
            raise HTTPException(status_code=500, detail=str(e))
        raise e