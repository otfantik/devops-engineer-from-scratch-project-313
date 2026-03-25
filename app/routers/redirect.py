from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from app.repository import link_repository

router = APIRouter()


@router.get("/r/{short_name}")
async def redirect_to_url(short_name: str):
    link = link_repository.get_by_short_name(short_name)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return RedirectResponse(url=link.original_url, status_code=302)
