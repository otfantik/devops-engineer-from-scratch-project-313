from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.database import engine
from app.models import Link

router = APIRouter()


def get_session():
    with Session(engine) as session:
        yield session


@router.get("/r/{short_name}")
async def redirect_to_url(short_name: str, session: Session = Depends(get_session)):
    link = session.exec(select(Link).where(Link.short_name == short_name)).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return RedirectResponse(url=link.original_url, status_code=302)
