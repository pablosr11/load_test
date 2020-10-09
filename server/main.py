from datetime import datetime
from typing import List

from database import crud, models, schemas
from database.db import SessionLocal, engine
from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save(db, req, sms: str = None):
    origin_ip = req.client.host
    origin_port = req.client.port
    endpoint = req.url.path
    method = req.method
    request = schemas.RequestBase(
        origin_ip=origin_ip,
        origin_port=origin_port,
        endpoint=endpoint,
        method=method,
    )
    crud.create_request(db, request, sms)
    return origin_ip, origin_port, endpoint, method


@app.get("/")
async def read_root(request: Request, db: Session = Depends(get_db)):
    origin_ip, origin_port, endpoint, method = save(db, request)
    return {
        "Hello": {
            "From": f"{origin_ip}:{origin_port}",
            "Endpoint used": endpoint,
            "Method": method,
        }
    }


@app.get("/sms/{sms_id}")
async def read_replies(sms_id: int, db: Session = Depends(get_db)):
    ### query db for all replies to this message
    replies = crud.get_replies(db, sms_id)
    ### query the message
    original = crud.get_request(db, sms_id)

    ### return the message and its replies
    return {"message": original, "replies": replies}


@app.get("/sms/", response_model=List[schemas.Request])
async def read_messages(
    request: Request,
    date: datetime = "",
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    save(db, request)
    requests = crud.get_requests(db, skip=skip, limit=limit, date=date)
    return requests


@app.post("/sms/{sms_id}")
async def write_reploy(
    sms_id: int,
    request: Request,
    message: schemas.RequestMessage,
    db: Session = Depends(get_db),
):
    ### query db to get the sms_id
    sms = crud.get_request(db, sms_id)

    ### if not found, return 404
    if not sms:
        raise HTTPException(status_code=404, detail="Item not found")

    ### if found, store request in db with message and its reply_to
    origin_ip = request.client.host
    origin_port = request.client.port
    endpoint = request.url.path
    method = request.method
    request = schemas.RequestBase(
        origin_ip=origin_ip,
        origin_port=origin_port,
        endpoint=endpoint,
        method=method,
    )
    reply = message.message
    new_sms = crud.create_reply(db, sms, request, reply)
    return new_sms


@app.post("/sms/")
async def write_message(
    request: Request, message: schemas.RequestMessage, db: Session = Depends(get_db)
):
    sms = message.message
    save(db, request, sms)
    return {"request": sms}
