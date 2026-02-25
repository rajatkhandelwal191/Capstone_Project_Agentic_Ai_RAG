from pydantic import BaseModel
from typing import Optional


class Incident(BaseModel):
    id: str
    title: str
    severity: str
    team: str
    status: str
    created_at: str


class ServiceRequest(BaseModel):
    id: str
    department: str
    request_type: str
    status: str
    created_at: str
