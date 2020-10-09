from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel


class MethodEnum(str, Enum):
    GET = "GET"
    POST = "POST"


class RequestBase(BaseModel):
    origin_ip: str
    origin_port: int = 0
    endpoint: str = None
    method: MethodEnum


class RequestMessageIn(BaseModel):
    message: str


class RequestMessageOut(BaseModel):
    id: int
    message: str
    replies_to: int = None

    class Config:
        orm_mode = True


class Request(RequestBase):
    id: int
    date_created: datetime
    message: str = None

    class Config:
        orm_mode = True


class RequestWithMessage(BaseModel):
    id: int
    message: str

    class Config:
        orm_mode = True


class RequestWithReplies(BaseModel):
    id: int
    message: str = None
    replies: List[RequestWithMessage]

    class Config:
        orm_mode = True
