from sqlmodel import Session, func, select

from app.database import engine
from app.models import Link, LinkCreate, LinkUpdate


class LinkRepository:
    def __init__(self):
        self.engine = engine

    def get_session(self):
        with Session(self.engine) as session:
            yield session

    def get_all(self, start: int, end: int):
        with Session(self.engine) as session:
            total = session.exec(select(func.count(Link.id))).one()
            limit = end - start + 1
            offset = start
            query = select(Link).offset(offset).limit(limit)
            links = session.exec(query).all()
            return links, total

    def get_by_short_name(self, short_name: str):
        with Session(self.engine) as session:
            return session.exec(
                select(Link).where(Link.short_name == short_name)
            ).first()

    def get_by_id(self, link_id: int):
        with Session(self.engine) as session:
            return session.get(Link, link_id)

    def create(self, link: LinkCreate):
        with Session(self.engine) as session:
            existing = session.exec(
                select(Link).where(Link.short_name == link.short_name)
            ).first()
            if existing:
                return None
            db_link = Link.model_validate(link)
            session.add(db_link)
            session.commit()
            session.refresh(db_link)
            return db_link

    def update(self, link_id: int, link_update: LinkUpdate):
        with Session(self.engine) as session:
            link = session.get(Link, link_id)
            if not link:
                return None
            if link_update.short_name != link.short_name:
                existing = session.exec(
                    select(Link).where(Link.short_name == link_update.short_name)
                ).first()
                if existing:
                    return None
            link.original_url = link_update.original_url
            link.short_name = link_update.short_name
            session.add(link)
            session.commit()
            session.refresh(link)
            return link

    def delete(self, link_id: int):
        with Session(self.engine) as session:
            link = session.get(Link, link_id)
            if not link:
                return False
            session.delete(link)
            session.commit()
            return True


link_repository = LinkRepository()
