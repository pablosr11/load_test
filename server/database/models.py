from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime

from .db import Base


class Requests(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    origin_ip = Column(String)
    origin_port = Column(Integer)
    endpoint = Column(String, index=True)
    method = Column(String, index=True)
    date_created = Column(DateTime(timezone=True), default=func.now())
    message = Column(String)
    replies_to = Column(Integer, ForeignKey("requests.id"))
    replies = relationship("Requests")
    phone = Column(String)
