from datetime import datetime
from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from . import models, schemas


def get_request(db: Session, sms_id: int) -> Optional[models.Requests]:
    return db.query(models.Requests).get(sms_id)


def get_requests(db: Session, date: datetime, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Requests)
        .filter(models.Requests.date_created > date)
        .order_by(desc("id"))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_replies(db: Session, sms_id: int):
    return db.query(models.Requests).filter(models.Requests.replies_to == sms_id).all()


def create_reply(
    db: Session,
    original_sms: models.Requests,
    request: schemas.RequestBase,
    request_sms: str = None,
):
    db_request = models.Requests(
        origin_ip=request.origin_ip,
        origin_port=request.origin_port,
        endpoint=request.endpoint,
        method=request.method,
        message=request_sms,
        replies_to=original_sms.id,
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request


def create_request(db: Session, request: schemas.RequestBase, sms: str = None):
    db_request = models.Requests(
        origin_ip=request.origin_ip,
        origin_port=request.origin_port,
        endpoint=request.endpoint,
        method=request.method,
        message=sms,
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request
