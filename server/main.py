from datetime import datetime, timedelta
from typing import Dict, List, NoReturn, Optional

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    Form,
    HTTPException,
    Request,
    Response,
)
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from twilio.twiml.messaging_response import MessagingResponse

from caches.redis_client import redis_cache
from database import crud, models, schemas
from database.db import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "*",  # to be modified for added security once we have static urls/other way of adding known origins
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def parse_request(request: Request):
    return {
        "origin_ip": request.client.host,
        "origin_port": request.client.port,
        "endpoint": request.url.path,
        "method": request.method,
    }


def store_request(
    db: SessionLocal,
    req: Request,
    new_message: str = None,
    replies_to: int = None,
    phone: str = None,
) -> schemas.Request:

    """
    Persist a message in the DB
    Returns serialised ready for return/cache storage
    """
    new_object = models.Requests(
        **parse_request(req), message=new_message, replies_to=replies_to
    )
    created_object = crud.create_message(db=db, message=new_object)

    ## This schema will contain replies, which are sqlalchemy models that are not serializble
    return schemas.Request.from_orm(created_object)


@app.get("/api", response_model=Dict)
async def read_root():
    # background_tasks.add_task(store_request, db, request)
    return {"Hello": "This is welcome page"}


@app.get("/api/sms/{sms_id}", response_model=schemas.RequestWithReplies)
async def read_replies(
    request: Request,
    sms_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # background_tasks.add_task(store_request, db, request)

    # try to get from cache
    if redis_cache.exists(sms_id):
        return schemas.Request.parse_raw(redis_cache.get(sms_id))

    # if not, query and store in cache
    req = crud.get_request(db=db, sms_id=sms_id)
    if not req:
        raise HTTPException(status_code=404, detail="Message not found")

    redis_cache.set(sms_id, schemas.Request.from_orm(req).json())
    return req


@app.get(
    "/api/sms/",
    response_model=List[schemas.RequestMessageOut],
    response_model_exclude_none=True,
)
async def read_messages(
    request: Request,
    background_tasks: BackgroundTasks,
    date: Optional[datetime] = datetime.now() - timedelta(30),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[schemas.Request]:
    # background_tasks.add_task(store_request, db, request)

    # if we have enough entries in cache, return from cache
    if redis_cache.llen("all") > 100:
        return [
            schemas.RequestMessageOut.parse_raw(x)
            for x in redis_cache.lrange("all", skip, skip + limit)
        ]

    # If less thatn required entries in cache, query db and add to cache
    requests = crud.get_requests(db, skip=skip, limit=limit, date=date)

    ## This breaks if the messages have replies. Currently working because none of the latest messages have
    redis_cache.lpush("all", *[schemas.Request.from_orm(x).json() for x in requests])
    return requests


@app.post(
    "/api/sms/{sms_id}",
    response_model=schemas.RequestMessageOut,
    response_model_exclude_none=True,
)
async def write_reploy(
    sms_id: int,
    request: Request,
    message: schemas.RequestMessageIn,
    db: Session = Depends(get_db),
):

    # If its not in cache, try to find it in the DB
    if not redis_cache.exists(sms_id):
        original_sms = crud.get_request(db, sms_id)
        if not original_sms:
            raise HTTPException(status_code=404, detail="Message not found")

    new_sms = store_request(
        db=db, req=request, new_message=message.message, replies_to=sms_id
    )
    # Update general cache with new message
    redis_cache.lpush("all", new_sms.json())

    # Delete original from cache as it has a new reply
    redis_cache.delete(sms_id)

    return new_sms


@app.post(
    "/api/sms/",
    response_model=schemas.RequestMessageOut,
    response_model_exclude_none=True,
)
async def write_message(
    request: Request, message: schemas.RequestMessageIn, db: Session = Depends(get_db)
):
    built_request = store_request(db=db, req=request, new_message=message.message)
    # Add new message to general cache
    redis_cache.lpush("all", built_request.json())
    return built_request


## to use these endpoints, webhooks have to be added to twilio backend.
@app.get("/twilio/")
@app.post("/twilio/")
async def twilio_write(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...),
    db: Session = Depends(get_db),
):
    store_request(db=db, req=request, new_message=Body, phone=From)

    # Twilio integration. Respond to messages
    # Some sec could be added here by checking the headers for a twilio signature against the origin url for a given account
    # more info on https://www.twilio.com/blog/build-secure-twilio-webhook-python-fastapi
    response = MessagingResponse()
    response.message(
        f"Welcome to Pablo's Avocados - We have confirmed your appointment. We will contact you at {From}. The words you used, namely '{Body}', don't have any creativity or rythm whatsoever but have a good day nonetheless"
    )
    return Response(content=str(response), media_type="application/xml")
