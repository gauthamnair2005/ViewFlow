# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2025-11-28
- Implemented custom ViewFlow player supporting local HTML5 files and YouTube iframe.
- Added theme system (dark/light) with persistent toggle and CSS variables.
- Replaced in-file test templates with filesystem templates under `templates/`.
- Implemented async like/dislike reactions and subscribe/unsubscribe endpoints with JSON responses.
- Added `Subscription` and `Reaction` models and UI support for likes/dislikes and subscriptions.
- Added user profile / channel pages with public-facing display name and region + joined date.
- Added `init_db()` to auto-create `uploads/` directory and apply best-effort SQLite migrations.
- Added `.gitignore` to ignore `viewflow.db` and `uploads/`.
- Updated styles: theme-aware player UI, pure-white dark text, linen/off-white light theme, blur/backdrop styling.
- Added `async_actions.js` to handle reactions/subscriptions without reloading the page.

### Notes
- Database migrations are a best-effort convenience for development. Use Alembic for production.
