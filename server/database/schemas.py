from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel


class MethodEnum(str, Enum):
    GET = "GET"
    POST = "POST"

class RequestMessageIn(BaseModel):
    message: str


class RequestMessageOut(BaseModel):
    id: int
    message: str
    replies_to: int = None

    class Config:
        orm_mode = True


class Request(BaseModel):
    """Schema matching the DB model"""

    id: int
    date_created: datetime = None
    message: str = None
    origin_ip: str = None
    origin_port: int = None
    endpoint: str = None
    method: MethodEnum = None
    replies_to: int = None
    phone: str = None
    replies : List = None

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
