import os
import sys
import time
from datetime import datetime
from pathlib import Path

from flask import Flask, g, jsonify, request, send_from_directory

import db
from media_names import safe_media_filename

_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = _DIR / "uploads"

_COLOR = sys.stderr.isatty() or sys.stdout.isatty()


def _ansi(code: str, text: str) -> str:
    if not _COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def _status_label(code: int) -> str:
    if code < 300:
        return _ansi("32", str(code))
    if code < 400:
        return _ansi("36", str(code))
    if code < 500:
        return _ansi("33", str(code))
    return _ansi("31", str(code))


def create_app() -> Flask:
    app = Flask(__name__)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    @app.before_request
    def _open_db() -> None:
        g._req_started = time.perf_counter()
        if "db" not in g:
            g.db = db.connect()

    @app.teardown_request
    def _close_db(exc: BaseException | None) -> None:
        connection = g.pop("db", None)
        if connection is not None:
            connection.close()

    @app.after_request
    def _log_request(response):
        started = getattr(g, "_req_started", None)
        elapsed_ms = (time.perf_counter() - started) * 1000 if started is not None else 0.0
        path = request.full_path.rstrip("?")
        client = request.remote_addr or "-"
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level = _ansi("1;36", "INFO")
        method = _ansi("1", request.method)
        status = _status_label(response.status_code)
        line = (
            f"[{ts}] {level}  {elapsed_ms:7.1f}ms  {client}  "
            f'"{method} {path} HTTP/1.1"  {status}'
        )
        print(line, flush=True)
        return response

    @app.post("/upload")
    def upload_video():
        company_name = (request.form.get("company_name") or "").strip()
        file = request.files.get("file")
        if not company_name or file is None or not file.filename:
            return jsonify({"error": "company_name and file are required"}), 400

        filename = safe_media_filename(company_name)
        dest = UPLOAD_DIR / filename
        file.save(dest)
        abs_path = str(dest.resolve())
        video_url = f"{request.host_url.rstrip('/')}/media/{filename}"

        db.upsert_video(g.db, company_name, abs_path, video_url)

        return jsonify({"company_name": company_name, "video_url": video_url}), 200

    @app.get("/get_video_url")
    def get_video_url():
        company_name = (request.args.get("company_name") or "").strip()
        if not company_name:
            return jsonify({"error": "company_name is required"}), 400

        row = g.db.execute(
            "SELECT company_name, video_url FROM videos WHERE company_name = ?",
            (company_name,),
        ).fetchone()
        if row is None:
            return jsonify({"error": "not found"}), 404

        return jsonify({"company_name": row["company_name"], "video_url": row["video_url"]}), 200

    @app.get("/media/<path:filename>")
    def serve_media(filename: str):
        return send_from_directory(UPLOAD_DIR, filename, conditional=True)

    @app.get("/videos")
    def list_videos():
        rows = g.db.execute(
            "SELECT company_name, file_path, video_url, created_at, updated_at FROM videos ORDER BY company_name"
        ).fetchall()
        return jsonify([dict(row) for row in rows]), 200

    return app


def main() -> None:
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT") or os.environ.get("PORT", "8000"))
    app = create_app()
    print(f"Video service listening on http://{host}:{port} (Ctrl+C to stop)", flush=True)
    try:
        from waitress import serve

        serve(app, host=host, port=port, threads=8)
    except ImportError:
        app.run(host=host, port=port, threaded=True, use_reloader=False)


if __name__ == "__main__":
    main()
