from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from . import models


def add_commit_refresh(db, request):
    db.add(request)
    db.commit()
    db.refresh(request)  # This will run an additional query
    return request


def get_request(db: Session, sms_id: int) -> Optional[models.Requests]:
    return (
        db.query(models.Requests)
        .options(joinedload(models.Requests.replies))
        .get(sms_id)
    )


def get_requests(
    db: Session,
    date: datetime = datetime.now() - timedelta(30),
    skip: int = 0,
    limit: int = 50,
) -> List[models.Requests]:
    return (
        db.query(models.Requests)
        .filter(models.Requests.date_created > date)
        .order_by(desc(models.Requests.id))
        .offset(skip)
        .limit(limit)
        .options(joinedload(models.Requests.replies))
        .all()
    )


def create_message(db: Session, message: models.Requests) -> models.Requests:
    """
    Given a DB session and a SQLAlchemy model, store it in Database.
    """
    return add_commit_refresh(db=db, request=message)
