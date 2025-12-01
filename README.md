# ViewFlow

**Version:** 0.5.2

ViewFlow is a lightweight Flask-based video sharing prototype used for local development and UI iteration. It provides a minimal video upload, playback (HTML5 + YouTube iframe), channel pages, simple subscription and like/dislike reactions, and a custom themeable player UI.

This repository is intended as a development playground, not a production-ready system.

## Features
- Upload and serve local video files (stored in `uploads/`).
- Custom player that supports HTML5 videos and YouTube iframes with custom controls.
- Like/dislike reactions and subscribe/unsubscribe (stored in SQLite DB).
- **Enhanced user profiles** with display name, age, gender, location, bio, and profile pictures.
- Per-video privacy (public/private) and owner-only delete.
- Light/Dark theme with a persistent toggle stored in `localStorage`.
- Async actions for reactions and subscriptions to avoid full page reloads.
- **Comprehensive registration system** with profile customization.

## Quick start (development)

Prerequisites:
- Python 3.10+ (tested locally with 3.12)
- A working virtual environment is recommended

1. Create and activate a virtualenv (optional but recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # or install flask and sqlalchemy manually
```

2. Run the dev server (default port 5000):

```bash
python3 test.py
# or use a different port:
PORT=8080 python3 test.py
```

3. Open http://127.0.0.1:5000 (or chosen port) in your browser.

Notes:
- The app creates an `uploads/` directory and a SQLite DB file (`viewflow.db`) automatically when started.
- `.gitignore` excludes `viewflow.db` and the `uploads/` folder so local artifacts are not committed.

## Data and migrations
- This project uses a simple, best-effort approach to add missing columns to the SQLite DB (via `ALTER TABLE`) when the server starts. This is intended only for development convenience. For production apps use a migration tool such as Alembic.

## Development notes
- Templates live in `templates/` for easy editing.
- Static assets are in `static/` (player, styles, async JS, theme script).
- The lightweight dev server is `test.py` which contains models, routes, and initialization logic for testing.