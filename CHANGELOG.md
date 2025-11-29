# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2025-11-29

### Added
- **Enhanced User Registration System**
  - Added comprehensive user profile fields: `date_joined`, `location`, `age`, `gender`, `profile_pic`, `bio`
  - Profile picture upload support with validation (JPG, PNG, GIF, WebP)
  - Two-column responsive registration form layout
  - Gender selection dropdown (Male/Female/Other/Prefer not to say)
  - Age validation (minimum 13 years)
  - Bio/description textarea for user profiles
  - Profile pictures stored in `uploads/profiles/` directory

### Changed
- **Database Schema Update**
  - Rebuilt database with enhanced User model structure
  - Updated `models.py` with new user fields
  - Updated `auth.py` registration handler with file upload processing
  - Enhanced `register.html` template with modern, grid-based layout
  - Added form styles for select dropdowns and file inputs

### Breaking Changes
- **Database reset required** - Old `viewflow.db` must be deleted
- Existing user data will not migrate automatically

## [0.1.1] - 2025-11-29

### Fixed
- **Like/Dislike Reaction System**
  - Fixed JavaScript form action attribute conflict with input `name="action"`
  - Changed `form.action` to `form.getAttribute('action')` in `async_actions_simple.js`
  - Resolved 404 error showing `[object HTMLInputElement]` in URL
  - Fixed authentication check to return proper JSON error (401) for unauthenticated AJAX requests
  - Removed `@login_required` decorator in favor of manual auth checks for AJAX compatibility
  - Added proper error handling for non-authenticated users
  - Moved script tags inside `<body>` for proper execution order

### Changed
- Created simplified `async_actions_simple.js` with better error handling and console logging
- Added `[ASYNC]` prefix to all console logs for easier debugging
- Improved button state management (accent/primary class toggling)

## [0.1.0] - 2025-11-28

### Added
- Implemented custom ViewFlow player supporting local HTML5 files and YouTube iframe
- Added theme system (dark/light) with persistent toggle and CSS variables
- Replaced in-file test templates with filesystem templates under `templates/`
- Implemented async like/dislike reactions and subscribe/unsubscribe endpoints with JSON responses
- Added `Subscription` and `Reaction` models and UI support for likes/dislikes and subscriptions
- Added user profile / channel pages with public-facing display name and region + joined date
- Added `init_db()` to auto-create `uploads/` directory and apply best-effort SQLite migrations
- Added `.gitignore` to ignore `viewflow.db` and `uploads/`
- Updated styles: theme-aware player UI, pure-white dark text, linen/off-white light theme, blur/backdrop styling
- Added `async_actions.js` to handle reactions/subscriptions without reloading the page

### Notes
- Database migrations are a best-effort convenience for development. Use Alembic for production
