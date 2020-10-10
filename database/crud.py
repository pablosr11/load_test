from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from . import models, schemas


def get_request(db: Session, sms_id: int) -> Optional[models.Requests]:
    return db.query(models.Requests).get(sms_id)


def get_requests(
    db: Session,
    date: datetime = datetime.now() - timedelta(30),
    skip: int = 0,
    limit: int = 100,
) -> List[models.Requests]:
    return (
        db.query(models.Requests)
        .filter(models.Requests.date_created > date)
        .order_by(desc("id"))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_replies(db: Session, sms_id: int) -> List[models.Requests]:
    return db.query(models.Requests).filter(models.Requests.replies_to == sms_id).all()


def create_reply(
    db: Session,
    original_sms: models.Requests,
    request: schemas.RequestBase,
    request_sms: str = None,
) -> models.Requests:
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


def create_request(
    db: Session, request: schemas.RequestBase, sms: str = None
) -> models.Requests:
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


def create_request_from_phone(
    db: Session, phone_number: str, phone_message: str, request: schemas.RequestBase
):
    print(db, phone_message, phone_number, request)
    db_request = models.Requests(
        origin_ip=request.origin_ip,
        origin_port=request.origin_port,
        endpoint=request.endpoint,
        method=request.method,
        message=phone_message,
        phone=phone_number,
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request
