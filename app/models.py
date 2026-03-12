from sqlmodel import SQLModel, Field
from datetime import datetime


class LinkBase(SQLModel):
    original_url: str
    short_name: str = Field(unique=True, index=True)


class Link(LinkBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LinkCreate(LinkBase):
    pass


class LinkUpdate(LinkBase):
    pass


class LinkResponse(LinkBase):
    id: int
    short_url: str
    created_at: datetime
