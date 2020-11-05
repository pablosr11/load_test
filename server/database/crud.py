from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from . import models, schemas


def add_commit_refresh(db, request):
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


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
        message=request_sms, replies_to=original_sms.id, **request.dict()
    )
    return add_commit_refresh(db=db, request=db_request)


def create_request(
    db: Session, request: schemas.RequestBase, sms: str = None
) -> models.Requests:
    db_request = models.Requests(
        message=sms,
        **request.dict(),
    )
    return add_commit_refresh(db=db, request=db_request)


def create_request_from_phone(
    db: Session, phone_number: str, phone_message: str, request: schemas.RequestBase
):
    db_request = models.Requests(
        message=phone_message, phone=phone_number, **request.dict()
    )
    return add_commit_refresh(db=db, request=db_request)
