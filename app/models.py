from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class LinkBase(SQLModel):
    original_url: str = Field(index=True)
    short_name: str = Field(unique=True, index=True)


class Link(LinkBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LinkCreate(LinkBase):
    pass


class LinkRead(LinkBase):
    id: int
    short_url: str
    created_at: datetime


class LinkUpdate(SQLModel):
    original_url: Optional[str] = None
    short_name: Optional[str] = None
