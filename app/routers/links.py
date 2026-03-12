import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlmodel import Session, func, select

from app.config import settings
from app.database import engine
from app.models import Link, LinkCreate, LinkResponse, LinkUpdate

# Настраиваем логирование
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


@router.get("/r/{short_name}")
async def redirect_to_url(
    short_name: str, request: Request, session: Session = Depends(get_session)
):
    logger.info("=== REDIRECT REQUEST RECEIVED ===")
    logger.info(f"Path: /r/{short_name}")
    logger.info(f"Full URL: {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Client host: {request.client.host if request.client else 'unknown'}")

    link = session.exec(select(Link).where(Link.short_name == short_name)).first()

    if not link:
        logger.warning(f"Link with short_name '{short_name}' not found in database")
        logger.info(
            f"Query executed: SELECT * FROM link WHERE short_name = '{short_name}'"
        )
        raise HTTPException(status_code=404, detail="Link not found")

    logger.info(f"Link found: id={link.id}, original_url={link.original_url}")
    logger.info(f"Redirecting to: {link.original_url}")

    return RedirectResponse(url=link.original_url, status_code=302)


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

    existing = session.exec(
        select(Link).where(Link.short_name == link.short_name)
    ).first()
    if existing:
        logger.warning(f"Short name '{link.short_name}' already exists")
        raise HTTPException(status_code=400, detail="Short name already exists")

    db_link = Link.model_validate(link)
    session.add(db_link)
    session.commit()
    session.refresh(db_link)

    logger.info(f"Link created with id={db_link.id}")

    return LinkResponse(
        id=db_link.id,
        original_url=db_link.original_url,
        short_name=db_link.short_name,
        short_url=f"{settings.BASE_URL}/r/{db_link.short_name}",
        created_at=db_link.created_at,
    )


@router.get("/{link_id}", response_model=LinkResponse)
async def get_link(link_id: int, session: Session = Depends(get_session)):
    logger.info(f"GET /api/links/{link_id}")

    link = session.get(Link, link_id)
    if not link:
        logger.warning(f"Link with id={link_id} not found")
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
    logger.info(f"PUT /api/links/{link_id}")

    link = session.get(Link, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if link_update.short_name != link.short_name:
        existing = session.exec(
            select(Link).where(Link.short_name == link_update.short_name)
        ).first()
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
    logger.info(f"DELETE /api/links/{link_id}")

    link = session.get(Link, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    session.delete(link)
    session.commit()
    return None
