from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class MethodEnum(str, Enum):
    GET = "GET"
    POST = "POST"


class RequestBase(BaseModel):
    origin_ip: str
    origin_port: int = 0
    endpoint: str = None
    method: MethodEnum


class Request(RequestBase):
    id: int
    date_created: datetime

    class Config:
        orm_mode = True
