import logging

from fastapi import APIRouter, HTTPException, Request, Response

from app.config import settings
from app.models import LinkCreate, LinkResponse, LinkUpdate
from app.repository import link_repository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


def parse_range(range_header: str):
    try:
        range_str = range_header.strip("[]")
        start, end = map(int, range_str.split(","))
        return start, end
    except (ValueError, AttributeError):
        return None, None


@router.get("", response_model=list[LinkResponse])
async def get_links(request: Request, response: Response):
    logger.info(f"GET /api/links - Headers: range={request.headers.get('range')}")

    range_header = request.headers.get("range")
    start, end = parse_range(range_header) if range_header else (0, 9)

    if start is None or end is None or start < 0 or end < start:
        start, end = 0, 9

    links, total = link_repository.get_all(start, end)

    response.headers["Content-Range"] = f"links {start}-{end}/{total}"
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"

    logger.info(f"Returning {len(links)} links, total={total}")

    return [
        LinkResponse(
            id=link.id,
            original_url=link.original_url,
            short_name=link.short_name,
            short_url=f"{settings.BASE_URL}/r/{link.short_name}",
            created_at=link.created_at,
        )
        for link in links
    ]


@router.post("", response_model=LinkResponse, status_code=201)
async def create_link(link: LinkCreate):
    logger.info(f"POST /api/links - Creating link with short_name={link.short_name}")

    db_link = link_repository.create(link)
    if not db_link:
        raise HTTPException(status_code=400, detail="Short name already exists")

    return LinkResponse(
        id=db_link.id,
        original_url=db_link.original_url,
        short_name=db_link.short_name,
        short_url=f"{settings.BASE_URL}/r/{db_link.short_name}",
        created_at=db_link.created_at,
    )


@router.get("/{link_id}", response_model=LinkResponse)
async def get_link(link_id: int):
    logger.info(f"GET /api/links/{link_id}")

    link = link_repository.get_by_id(link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    return LinkResponse(
        id=link.id,
        original_url=link.original_url,
        short_name=link.short_name,
        short_url=f"{settings.BASE_URL}/r/{link.short_name}",
        created_at=link.created_at,
    )


@router.put("/{link_id}", response_model=LinkResponse)
async def update_link(link_id: int, link_update: LinkUpdate):
    logger.info(f"PUT /api/links/{link_id}")

    link = link_repository.update(link_id, link_update)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    return LinkResponse(
        id=link.id,
        original_url=link.original_url,
        short_name=link.short_name,
        short_url=f"{settings.BASE_URL}/r/{link.short_name}",
        created_at=link.created_at,
    )


@router.delete("/{link_id}", status_code=204)
async def delete_link(link_id: int):
    logger.info(f"DELETE /api/links/{link_id}")

    if not link_repository.delete(link_id):
        raise HTTPException(status_code=404, detail="Link not found")

    return None
