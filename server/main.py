from datetime import datetime
from typing import List

from database import crud, models, schemas
from database.db import SessionLocal, engine
from fastapi import Depends, FastAPI, Request
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


@app.post("/sms/")
async def write_message(
    request: Request, message: schemas.RequestMessage, db: Session = Depends(get_db)
):
    sms = message.message
    save(db, request, sms)
    return {"request": sms}


# new CONVO endpoint with id of request as path parameter
# POST sends a response
# GET gets message and all its replies
