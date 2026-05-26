import os
from flask import Flask, render_template, request, jsonify
from flask_compress import Compress
from models import init_db, get_articles, count_articles, get_sources
from scheduler import start_scheduler, fetch_and_store

REFRESH_KEY = os.environ.get("REFRESH_KEY", "rucn2025")

app = Flask(__name__)
Compress(app)

init_db()
start_scheduler()
fetch_and_store()


@app.after_request
def set_headers(response):
    response.headers["X-Robots-Tag"] = "index, follow"
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/news")
def api_news():
    page = request.args.get("page", 1, type=int)
    lang = request.args.get("lang") or None
    source = request.args.get("source") or None
    per_page = 20

    articles = get_articles(page=page, per_page=per_page, lang=lang, source=source)
    total = count_articles(lang=lang, source=source)

    return jsonify({
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": max(1, (total + per_page - 1) // per_page),
        "articles": [dict(a) for a in articles],
    })


@app.route("/api/refresh")
def api_refresh():
    if request.args.get("key") != REFRESH_KEY:
        return jsonify({"error": "forbidden"}), 403
    fetch_and_store()
    return jsonify({"status": "ok", "articles": count_articles()})


@app.route("/health")
def health():
    return jsonify({"status": "ok", "articles": count_articles()})


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
