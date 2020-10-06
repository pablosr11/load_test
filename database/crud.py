from sqlalchemy.orm import Session
from sqlalchemy import desc

from . import models, schemas


def get_requests(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Requests).order_by(desc("id")).offset(skip).limit(limit).all()


def create_request(db: Session, request: schemas.RequestBase):
    db_request = models.Requests(
        origin_ip=request.origin_ip,
        origin_port=request.origin_port,
        endpoint=request.endpoint,
        method=request.method,
        message=request.message,
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request
