import os
from flask import Flask, jsonify, request
from sqlmodel import select
from .database import get_session, create_db_and_tables, BASE_URL
from .models import Link, LinkCreate, LinkRead
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

if os.environ.get("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

app = Flask(__name__)

create_db_and_tables()


@app.route("/ping")
def ping():
    return "pong"


@app.route("/error")
def trigger_error():
    if os.environ.get("SENTRY_DSN"):
        raise ZeroDivisionError("Test error for Sentry")
    return "Sentry is not configured"


@app.route("/api/links", methods=["GET"])
def get_all_links():
    with next(get_session()) as session:
        statement = select(Link)
        results = session.exec(statement).all()

        links = []
        for link in results:
            link_data = LinkRead(
                id=link.id,
                original_url=link.original_url,
                short_name=link.short_name,
                short_url=f"{BASE_URL}/r/{link.short_name}",
                created_at=link.created_at,
            )
            links.append(link_data.dict())

        return jsonify(links)


@app.route("/api/links", methods=["POST"])
def create_link():
    data = request.get_json()

    if not data or "original_url" not in data or "short_name" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    link_create = LinkCreate(
        original_url=data["original_url"], short_name=data["short_name"]
    )

    with next(get_session()) as session:
        existing = session.exec(
            select(Link).where(Link.short_name == link_create.short_name)
        ).first()

        if existing:
            return jsonify(
                {
                    "error": "Short name already exists",
                    "short_name": link_create.short_name,
                }
            ), 409

        link = Link(**link_create.dict())
        session.add(link)
        session.commit()
        session.refresh(link)

        link_read = LinkRead(
            id=link.id,
            original_url=link.original_url,
            short_name=link.short_name,
            short_url=f"{BASE_URL}/r/{link.short_name}",
            created_at=link.created_at,
        )

        return jsonify(link_read.dict()), 201


@app.route("/api/links/<int:link_id>", methods=["GET"])
def get_link(link_id: int):
    with next(get_session()) as session:
        link = session.get(Link, link_id)

        if not link:
            return jsonify({"error": "Link not found"}), 404

        link_read = LinkRead(
            id=link.id,
            original_url=link.original_url,
            short_name=link.short_name,
            short_url=f"{BASE_URL}/r/{link.short_name}",
            created_at=link.created_at,
        )

        return jsonify(link_read.dict())


@app.route("/api/links/<int:link_id>", methods=["PUT"])
def update_link(link_id: int):
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    with next(get_session()) as session:
        link = session.get(Link, link_id)

        if not link:
            return jsonify({"error": "Link not found"}), 404

        if "short_name" in data and data["short_name"] != link.short_name:
            existing = session.exec(
                select(Link).where(Link.short_name == data["short_name"])
            ).first()

            if existing:
                return jsonify(
                    {
                        "error": "Short name already exists",
                        "short_name": data["short_name"],
                    }
                ), 409

        for key, value in data.items():
            if hasattr(link, key):
                setattr(link, key, value)

        session.add(link)
        session.commit()
        session.refresh(link)

        link_read = LinkRead(
            id=link.id,
            original_url=link.original_url,
            short_name=link.short_name,
            short_url=f"{BASE_URL}/r/{link.short_name}",
            created_at=link.created_at,
        )

        return jsonify(link_read.dict())


@app.route("/api/links/<int:link_id>", methods=["DELETE"])
def delete_link(link_id: int):
    with next(get_session()) as session:
        link = session.get(Link, link_id)

        if not link:
            return jsonify({"error": "Link not found"}), 404

        session.delete(link)
        session.commit()

        return "", 204


@app.route("/r/<short_name>", methods=["GET"])
def redirect_to_original(short_name: str):
    with next(get_session()) as session:
        link = session.exec(select(Link).where(Link.short_name == short_name)).first()

        if not link:
            return jsonify({"error": "Link not found"}), 404

        return jsonify({"url": link.original_url}), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
