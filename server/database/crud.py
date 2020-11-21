from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from server.database.models import Requests


def add_commit_refresh(db, request):
    db.add(request)
    db.commit()
    db.refresh(request)  # This will run an additional query
    return request


def get_request(db: Session, sms_id: int) -> Optional[Requests]:
    return db.query(Requests).options(joinedload(Requests.replies)).get(sms_id)


def get_requests(
    db: Session,
    date: datetime = None,
    skip: int = 0,
    limit: int = 50,
) -> List[Requests]:
    if not date:
        date = datetime.now() - timedelta(30)
    return (
        db.query(Requests)
        .filter(Requests.date_created > date)
        .order_by(desc(Requests.id))
        .offset(skip)
        .limit(limit)
        .options(joinedload(Requests.replies))
        .all()
    )


def create_message(db: Session, message: Requests) -> Requests:
    """
    Given a DB session and a SQLAlchemy model, store it in Database.
    """
    return add_commit_refresh(db=db, request=message)
