from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.database import engine
from app.models import Link, LinkCreate, LinkUpdate, LinkResponse
from app.config import settings

router = APIRouter()


def get_session():
    with Session(engine) as session:
        yield session


@router.get("", response_model=list[LinkResponse])
async def get_links(session: Session = Depends(get_session)):
    links = session.exec(select(Link)).all()
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
    existing = session.exec(
        select(Link).where(Link.short_name == link.short_name)
    ).first()
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
    link = session.get(Link, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    session.delete(link)
    session.commit()
    return None
