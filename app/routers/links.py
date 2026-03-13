import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlmodel import Session, func, select

from app.config import settings
from app.database import engine
from app.models import Link, LinkCreate, LinkResponse, LinkUpdate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


def get_session():
    with Session(engine) as session:
        yield session


def parse_range(range_header: str):
    try:
        range_str = range_header.strip("[]")
        start, end = map(int, range_str.split(","))
        return start, end
    except (ValueError, AttributeError):
        return None, None


@router.get("", response_model=list[LinkResponse])
async def get_links(
    request: Request, response: Response, session: Session = Depends(get_session)
):
    logger.info(f"GET /api/links - Headers: range={request.headers.get('range')}")
    total = session.exec(select(func.count(Link.id))).one()
    range_header = request.headers.get("range")
    start, end = parse_range(range_header) if range_header else (0, 9)
    if start is None or end is None or start < 0 or end < start:
        start, end = 0, 9
    limit = end - start + 1
    offset = start
    response.headers["Content-Range"] = f"links {start}-{end}/{total}"
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    query = select(Link).offset(offset).limit(limit)
    links = session.exec(query).all()
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
async def create_link(link: LinkCreate, session: Session = Depends(get_session)):
    logger.info(f"POST /api/links - Creating link with short_name={link.short_name}")
    stmt = select(Link).where(Link.short_name == link.short_name)
    existing = session.exec(stmt).first()
    if existing:
        raise HTTPException(status_code=400, detail="Short name already exists")
    db_link = Link.model_validate(link)
    session.add(db_link)
    session.commit()
    session.refresh(db_link)
    return LinkResponse(
        id=db_link.id,
        original_url=db_link.original_url,
        short_name=db_link.short_name,
        short_url=f"{settings.BASE_URL}/r/{db_link.short_name}",
        created_at=db_link.created_at,
    )


@router.get("/{link_id}", response_model=LinkResponse)
async def get_link(link_id: int, session: Session = Depends(get_session)):
    link = session.get(Link, link_id)
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
async def update_link(
    link_id: int, link_update: LinkUpdate, session: Session = Depends(get_session)
):
    link = session.get(Link, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    if link_update.short_name != link.short_name:
        stmt = select(Link).where(Link.short_name == link_update.short_name)
        existing = session.exec(stmt).first()
        if existing:
            raise HTTPException(status_code=400, detail="Short name already exists")
    link.original_url = link_update.original_url
    link.short_name = link_update.short_name
    session.add(link)
    session.commit()
    session.refresh(link)
    return LinkResponse(
        id=link.id,
        original_url=link.original_url,
        short_name=link.short_name,
        short_url=f"{settings.BASE_URL}/r/{link.short_name}",
        created_at=link.created_at,
    )


@router.delete("/{link_id}", status_code=204)
async def delete_link(link_id: int, session: Session = Depends(get_session)):
    link = session.get(Link, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    session.delete(link)
    session.commit()
    return None
