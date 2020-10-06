## TBC https://fastapi.tiangolo.com/tutorial/sql-databases/

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
    message: str = None


class Request(RequestBase):
    id: int

    class Config:
        orm_mode = True
