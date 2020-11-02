from datetime import datetime, timedelta
from typing import List, Optional

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

from database import crud, models, schemas
from database.db import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://192.168.0.2:3000",
    "http://localhost",
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
    origin_ip = request.client.host
    origin_port = request.client.port
    endpoint = request.url.path
    method = request.method
    built_request = schemas.RequestBase(
        origin_ip=origin_ip,
        origin_port=origin_port,
        endpoint=endpoint,
        method=method,
    )
    return built_request


def store_request(db: SessionLocal, req: Request) -> schemas.RequestBase:
    built_request = generate_message(req)
    crud.create_request(db, built_request)
    return built_request


def store_request_with_message(
    db: SessionLocal, req: Request, text: str
) -> schemas.Request:
    built_request = generate_message(req)
    request_with_sms = crud.create_request(db=db, request=built_request, sms=text)
    return request_with_sms


def store_reply(
    db: SessionLocal, req: Request, text: str, og_message: models.Requests
) -> schemas.Request:
    built_request = generate_message(req)
    request_with_sms = crud.create_reply(
        db=db, original_sms=og_message, request=built_request, request_sms=text
    )
    return request_with_sms


@app.get("/api")
async def read_root(
    request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    ## fastapi.backgrounds tasks might be too slow? Or maybe we need to increase open connections with DB.
    # sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) FATAL:  sorry, too many clients already
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
    original = crud.get_request(db=db, sms_id=sms_id)
    return original


@app.get("/api/sms/", response_model=List[schemas.Request])
async def read_messages(
    request: Request,
    background_tasks: BackgroundTasks,
    date: Optional[datetime] = datetime.now() - timedelta(30),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[schemas.Request]:
    # background_tasks.add_task(store_request, db, request)
    requests = crud.get_requests(db, skip=skip, limit=limit, date=date)
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

    original_sms = crud.get_request(db, sms_id)

    if not original_sms:
        raise HTTPException(status_code=404, detail="Message not found")

    reply = message.message
    new_sms = store_reply(db=db, req=request, text=reply, og_message=original_sms)
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
