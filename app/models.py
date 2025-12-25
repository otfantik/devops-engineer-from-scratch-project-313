from sqlmodel import Field, SQLModel
from datetime import datetime
import os


class Link(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    original_url: str
    short_name: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def short_url(self) -> str:
        base_url = os.getenv("BASE_URL", "http://localhost:5000")
        return f"{base_url}/{self.short_name}"
