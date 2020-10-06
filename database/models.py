from sqlalchemy import Column, Integer, String

from .db import Base


class Requests(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    origin_ip = Column(String)
    origin_port = Column(Integer)
    endpoint = Column(String, index=True)
    method = Column(String, index=True)
    message = Column(String)
