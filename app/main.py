from sqlalchemy.pool import StaticPool
from flask import Flask, request, g
from sqlmodel import SQLModel, create_engine, Session, select
from app.models import Link
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

app = Flask(__name__)

# Определение DATABASE_URL в зависимости от окружения
if os.getenv("TESTING", "").lower() == "true":
    DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")
    # Исправляем postgres:// на postgresql:// для SQLAlchemy (важно для Render)
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(DATABASE_URL)

app.engine = engine


# Создание таблиц при запуске приложения
def create_db_and_tables():
    try:
        SQLModel.metadata.create_all(engine)
        app.logger.info("✅ Таблицы базы данных созданы/проверены")
        return True
    except Exception as e:
        app.logger.error(f"❌ Ошибка при создании таблиц: {e}")
        return False


# Создаем таблицы сразу при импорте/запуске
# Это сработает и локально, и на Render при старте приложения
create_db_and_tables()


# Health check endpoint с проверкой БД
@app.route("/health", methods=["GET"])
def health_check():
    try:
        # Проверяем подключение к БД
        with Session(engine) as session:
            result = session.execute("SELECT 1")
            
            # Проверяем существование таблицы link
            result = session.execute(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'link')"
            )
            table_exists = result.scalar()
            
            if table_exists:
                # Пробуем получить количество записей
                try:
                    count_result = session.execute("SELECT COUNT(*) FROM link")
                    count = count_result.scalar()
                    return {
                        "status": "healthy",
                        "database": "connected",
                        "table_exists": True,
                        "links_count": count
                    }, 200
                except:
                    # Если не получается посчитать, но таблица есть
                    return {
                        "status": "healthy",
                        "database": "connected",
                        "table_exists": True,
                        "links_count": "unknown"
                    }, 200
            else:
                # Если таблицы нет, пытаемся создать
                app.logger.warning("Таблица 'link' не найдена, создаем...")
                if create_db_and_tables():
                    return {
                        "status": "initializing",
                        "database": "connected",
                        "table_exists": False,
                        "message": "Tables created successfully"
                    }, 200
                else:
                    return {
                        "status": "error",
                        "database": "connected",
                        "table_exists": False,
                        "message": "Failed to create tables"
                    }, 500
                
    except Exception as e:
        app.logger.error(f"Health check failed: {e}")
        # При ошибке пробуем создать таблицы заново
        try:
            create_db_and_tables()
            return {
                "status": "recovering",
                "error": str(e),
                "message": "Attempting to recreate tables..."
            }, 503
        except:
            return {
                "status": "unhealthy",
                "error": str(e)
            }, 500


# Функция для получения сессии
def get_session():
    if "session" not in g:
        g.session = Session(engine)
    return g.session


# функцию доступной как атрибут приложения
app.get_session = get_session


@app.route("/ping", methods=["GET"])
def ping():
    return {"message": "pong"}


@app.route("/api/links", methods=["POST"])
def create_link():
    try:
        data = request.get_json()

        if not data or "original_url" not in data or "short_name" not in data:
            return {"error": "Missing required fields"}, 400

        session = get_session()

        # Проверка на дубликат
        existing = session.exec(
            select(Link).where(Link.short_name == data["short_name"])
        ).first()

        if existing:
            return {"error": "Short name already exists"}, 409

        # Создание новой ссылки
        link = Link(original_url=data["original_url"], short_name=data["short_name"])

        session.add(link)
        session.commit()
        session.refresh(link)

        return {
            "id": link.id,
            "original_url": link.original_url,
            "short_name": link.short_name,
            "short_url": link.short_url,
            "created_at": link.created_at.isoformat() if link.created_at else None,
        }, 201
    except Exception as e:
        app.logger.error(f"Error creating link: {e}")
        return {"error": "Internal server error"}, 500


@app.route("/api/links", methods=["GET"])
def get_all_links():
    try:
        session = get_session()
        links = session.exec(select(Link)).all()

        return {
            "links": [
                {
                    "id": link.id,
                    "original_url": link.original_url,
                    "short_name": link.short_name,
                    "short_url": link.short_url,
                    "created_at": link.created_at.isoformat()
                    if link.created_at
                    else None,
                }
                for link in links
            ]
        }
    except Exception as e:
        app.logger.error(f"Error getting links: {e}")
        return {"error": "Internal server error"}, 500


@app.route("/api/links/<int:link_id>", methods=["GET"])
def get_link(link_id):
    try:
        session = get_session()
        link = session.get(Link, link_id)

        if not link:
            return {"error": "Link not found"}, 404

        return {
            "id": link.id,
            "original_url": link.original_url,
            "short_name": link.short_name,
            "short_url": link.short_url,
            "created_at": link.created_at.isoformat() if link.created_at else None,
        }
    except Exception as e:
        app.logger.error(f"Error getting link {link_id}: {e}")
        return {"error": "Internal server error"}, 500


@app.route("/api/links/<int:link_id>", methods=["PUT"])
def update_link(link_id):
    try:
        data = request.get_json()

        if not data:
            return {"error": "No data provided"}, 400

        session = get_session()
        link = session.get(Link, link_id)

        if not link:
            return {"error": "Link not found"}, 404

        # Обновление полей
        if "original_url" in data:
            link.original_url = data["original_url"]

        if "short_name" in data:
            # Проверка на дубликат (кроме текущей записи)
            existing = session.exec(
                select(Link).where(
                    Link.short_name == data["short_name"], Link.id != link_id
                )
            ).first()

            if existing:
                return {"error": "Short name already exists"}, 409

            link.short_name = data["short_name"]

        session.add(link)
        session.commit()
        session.refresh(link)

        return {
            "id": link.id,
            "original_url": link.original_url,
            "short_name": link.short_name,
            "short_url": link.short_url,
            "created_at": link.created_at.isoformat() if link.created_at else None,
        }
    except Exception as e:
        app.logger.error(f"Error updating link {link_id}: {e}")
        return {"error": "Internal server error"}, 500


@app.route("/api/links/<int:link_id>", methods=["DELETE"])
def delete_link(link_id):
    try:
        session = get_session()
        link = session.get(Link, link_id)

        if not link:
            return {"error": "Link not found"}, 404

        session.delete(link)
        session.commit()

        return {"message": "Link deleted successfully"}
    except Exception as e:
        app.logger.error(f"Error deleting link {link_id}: {e}")
        return {"error": "Internal server error"}, 500


# Редирект по короткой ссылке
@app.route("/<short_name>", methods=["GET"])
def redirect_to_original(short_name):
    try:
        session = get_session()
        link = session.exec(select(Link).where(Link.short_name == short_name)).first()

        if not link:
            return {"error": "Link not found"}, 404

        return {"redirect_to": link.original_url}, 302
    except Exception as e:
        app.logger.error(f"Error redirecting {short_name}: {e}")
        return {"error": "Internal server error"}, 500


@app.teardown_appcontext
def teardown_session(exception=None):
    session = g.pop("session", None)
    if session is not None:
        session.close()


@app.errorhandler(404)
def not_found(error):
    return {"error": "Not found"}, 404


if __name__ == "__main__":
    # Локальный запуск - таблицы уже созданы в начале
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
