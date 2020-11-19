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

try:
    models.Base.metadata.create_all(bind=engine)
except Exception as exc:
    print("err connecting with the DB")
    raise exc

app = FastAPI()

## queries profiling
# import sqltap
# @app.middleware("http")
# async def add_sql_tap(request: Request, call_next):
#     profiler = sqltap.start()
#     response = await call_next(request)
#     statistics = profiler.collect()
#     sqltap.report(statistics, "report.txt", report_format="text")
#     return response

# import yappi
# import sqlalchemy
# import fastapi
# @app.middleware("http")
# async def yappi_metrics(request: Request, call_next):
#     yappi.set_clock_type("wall")
#     yappi.start()
#     response = await call_next(request)
#     yappi.stop()
#     # endpoint_func = yappi.get_func_stats(filter_callback=lambda x: fastapi.routing.run_endpoint_function)
#     # deps = yappi.get_func_stats(filter_callback=lambda x: fastapi.routing.solve_dependencies)
#     # db_exec_time = yappi.get_func_stats(filter_callback=lambda x: sqlalchemy.engine.base.Engine.execute.__qualname__)
#     # db_fetch_time = yappi.get_func_stats(filter_callback=lambda x: (
# 	# 	sqlalchemy.engine.ResultProxy.fetchone,
# 	# 	sqlalchemy.engine.ResultProxy.fetchmany,
# 	# 	sqlalchemy.engine.ResultProxy.fetchall,
# 	# ))
#     # pydantic_time = yappi.get_func_stats(filter_callback=lambda x: fastapi.routing.serialize_response.__qualname__)
#     # render_time = yappi.get_func_stats(filter_callback=lambda x: response.render.__qualname__)

#     yappi.get_func_stats().sort('ttot', sort_order="desc").print_all() # All time
#     return response


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
    return schemas.Request(**created_object.__dict__)


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

    serialised = schemas.Request.from_orm(req)

    redis_cache.set(sms_id, serialised.json())
    return serialised


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
    limit: int = 50,
    db: Session = Depends(get_db),
) -> List[schemas.Request]:
    # background_tasks.add_task(store_request, db, request)

    # if we have enough entries in cache, return from cache
    if redis_cache.llen("all") >= limit:
        return [
            schemas.RequestMessageOut.parse_raw(x)
            for x in redis_cache.lrange("all", skip, skip + limit)
        ]

    # If less thatn required entries in cache, query db and add to cache
    requests = crud.get_requests(db, skip=skip, limit=limit, date=date)

    # Could we fix id we pull the tables on query .options(joinedload(models.Requests.replies))
    # this might on empty queryset
    redis_cache.lpush("all", *[schemas.Request(**x.__dict__).json() for x in requests])
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
        redis_cache.set(sms_id, schemas.Request.from_orm(original_sms).json())

    new_sms = store_request(
        db=db, req=request, new_message=message.message, replies_to=sms_id
    )
    # Update general cache with new message
    redis_cache.lpush("all", new_sms.json())

    # Set expiration date on key to refresh it from DB. That way we
    # will fetch the new replies after some seconds. This will save
    # queries if we keep titting this endpoint and also regresh from
    # db after N time.
    if redis_cache.ttl(sms_id) == -1:
        redis_cache.expire(name=sms_id, time=20)

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
