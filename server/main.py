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


def generate_message(request: Request) -> schemas.RequestBase:
    built_request = schemas.RequestBase(
        origin_ip=request.client.host,
        origin_port=request.client.port,
        endpoint=request.url.path,
        method=request.method,
    )
    return built_request


def store_request(db: SessionLocal, req: Request) -> NoReturn:
    crud.create_request(db, generate_message(req))


def store_request_with_message(
    db: SessionLocal, req: Request, text: str
) -> schemas.RequestMessageOut:
    built_request = generate_message(req)
    request_with_sms = crud.create_request(db=db, request=built_request, sms=text)
    return schemas.RequestMessageOut.from_orm(request_with_sms)


def store_reply(
    db: SessionLocal, req: Request, text: str, og_message: models.Requests
) -> schemas.RequestMessageOut:
    built_request = generate_message(req)
    request_with_sms = crud.create_reply(
        db=db, original_sms=og_message, request=built_request, request_sms=text
    )
    return schemas.RequestMessageOut.from_orm(request_with_sms)


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
        return schemas.RequestWithReplies.parse_raw(redis_cache.get(sms_id))

    # if not, query and store in cache
    req = crud.get_request(db=db, sms_id=sms_id)
    if not req:
        raise HTTPException(status_code=404, detail="Message not found")

    if req.replies:
        redis_cache.set(sms_id, schemas.RequestWithReplies.from_orm(req).json())
        
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

    #if we have enough entries in cache, return from cache
    if (redis_cache.llen("all") > 100):
        return [
            schemas.RequestMessageOut.parse_raw(x)
            for x in redis_cache.lrange("all", skip, skip + limit)
        ]

    # If less thatn required entries in cache, query db and add to cache
    requests = crud.get_requests(db, skip=skip, limit=limit, date=date)
    redis_cache.lpush("all", *[schemas.RequestMessageOut.from_orm(x).json() for x in requests])
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

    # Try to query this from cache - in such a way that we can store it in DB afterwards
    if redis_cache.exists(sms_id):
        original_sms = schemas.RequestWithReplies.parse_raw(redis_cache.get(sms_id))
    else:
        original_sms = crud.get_request(db, sms_id)

        if not original_sms:
            raise HTTPException(status_code=404, detail="Message not found")

    new_sms = store_reply(db=db, req=request, text=message.message, og_message=original_sms)
    
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
    sms = message.message
    built_request = store_request_with_message(db=db, req=request, text=sms)
    
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
    phone_request = generate_message(request)
    crud.create_request_from_phone(
        db=db, phone_number=From, phone_message=Body, request=phone_request
    )

    # Twilio integration. Respond to messages
    # Some sec could be added here by checking the headers for a twilio signature against the origin url for a given account
    # more info on https://www.twilio.com/blog/build-secure-twilio-webhook-python-fastapi
    response = MessagingResponse()
    response.message(
        f"Welcome to Pablo's Avocados - We have confirmed your appointment. We will contact you at {From}. The words you used, namely '{Body}', don't have any creativity or rythm whatsoever but have a good day nonetheless"
    )
    return Response(content=str(response), media_type="application/xml")
