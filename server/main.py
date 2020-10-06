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


def save(db, q, req):
    origin_ip = req.client.host
    origin_port = req.client.port
    endpoint = req.url.path
    method = req.method
    message = q if q else ""
    request = schemas.RequestBase(
        origin_ip=origin_ip,
        origin_port=origin_port,
        endpoint=endpoint,
        method=method,
        message=message,
    )
    print(request)
    crud.create_request(db, request)
    return origin_ip, origin_port, endpoint, method


@app.get("/")
async def read_root(request: Request, q: str = None, db: Session = Depends(get_db)):
    origin_ip, origin_port, endpoint, method = save(db, q, request)
    return {
        "Hello": {
            "From": f"{origin_ip}:{origin_port}",
            "Endpoint used": endpoint,
            "Method": method,
            "Message": q,
        }
    }


@app.get("/read/", response_model=List[schemas.Request])
async def read_requests(
    request: Request,
    q: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    save(db, q, request)

    requests = crud.get_requests(db, skip=skip, limit=limit)
    return requests
