# Changelog

All notable changes to this project will be documented in this file.

## [0.9.0] - 2025-12-03

### Added
- **Analytics Dashboard**
  - Integrated analytics into the user profile page (visible only to the owner).
  - **Charts**: Visual representation of Views and New Subscribers over the last 30 days using Chart.js.
  - **Stats**: Summary cards for Total Views, Total Subscribers, and Total Videos.
  - **Top Videos**: List of top 5 performing videos with detailed stats.
- **Advanced Video Management**
  - **Edit Video**: Added functionality to edit video title, description, category, tags, and thumbnail.
  - **Visibility Toggle**: Quick toggle button (Public/Private) directly on the watch and profile pages.
  - **Background Uploads**: Video processing (transcoding, thumbnail generation) now happens in the background.
  - **Upload Progress**: Added a visual indicator (pulsing badge) on the profile icon for ongoing uploads.
- **Player Enhancements**
  - **"Most Replayed" Heatmap**: Added a YouTube-style heatmap graph overlay on the seek bar to show popular segments.
  - **Seek Preview Frames**: Hovering over the seek bar now displays a preview thumbnail of that specific time.
  - **Resolution Switching**: Support for multiple video resolutions (720p, 480p, 360p) with a quality selector in the player.
  - **Markdown Descriptions**: Video descriptions now support Markdown formatting (bold, italics, links, lists).
- **Database & Backend**
  - Added `heatmap` and `preview_images` columns to `Video` model.
  - Added `status` column to track upload processing state (`processing`, `ready`, `failed`).
  - Implemented background thread for video processing using `threading`.
  - Added API endpoints for heatmap data and upload status.

### Changed
- **Profile Page**:
  - Introduced tabbed interface ("Videos" and "Analytics") for channel owners.
  - Improved layout of video management controls (Edit, Delete, Visibility) to be side-by-side.
- **Video Player**:
  - Updated seek bar tooltip to be positioned above the bar with a pointed arrow.
  - Heatmap visualization changed from bars to a smooth line graph with filled area.

## [0.8.3] - 2025-12-03

### Added
- **Search Suggestions**
  - Implemented search suggestions dropdown in the search bar.
  - Suggestions include trending videos (when query is empty) and matching video titles (when typing).
  - Added backend endpoint `/search/suggestions` to serve suggestion data.
  - Updated `test.py` to include the new search suggestions endpoint for development testing.
- **UI/UX Improvements**
  - **Animated Gradient Background**: Added a subtle, animated gradient background for both light and dark themes.
  - **Modern Auth Pages**: Redesigned Login and Register pages with glassmorphism, rounded corners, and better input styling.
  - **Search Bar**: Added a floating suggestions dropdown with backdrop blur.

### Changed
- **Visual Polish**
  - Enhanced dark theme with deep, subtle colors in the animated gradient.
  - Improved light theme with very pale, non-intrusive gradient colors.
  - Updated `static/style.css` with new animations and component styles.

## [0.8.2] - 2025-12-02

### Added
- **Profile Settings & Management**
  - Added `/settings` page for users to update profile details (Username, Display Name, Bio, Location, Gender).
  - Implemented profile picture upload and update functionality.
  - Replaced static `age` field with `date_of_birth` (Date type) for dynamic age calculation.
  - Updated registration flow to capture Date of Birth.
- **Subscriptions Page**
  - Added `/subscriptions` route displaying a personalized feed of videos from subscribed channels.
  - **Smart Sorting**: Subscribed channels are prioritized based on user engagement (view history).
  - **Top Panel**: Horizontal scrollable list of subscribed channels with avatars.
- **Enhanced Navigation Bar**
  - **Responsive Design**: Navbar buttons automatically switch to icon-only mode on smaller screens (< 1100px).
  - **Profile Integration**: Replaced text display name with user's profile picture (squircle style).
  - **Icon Refresh**: Updated Upload and Settings icons to cleaner, standard SVG icons.
  - **Mobile Optimization**: Improved layout for mobile devices, hiding non-essential text labels.

### Changed
- **Watch Page UI**
  - Removed redundant "Subscribe" button from the channel info bar (kept the main action button).
  - Reduced spacing between channel avatar and name for a tighter layout.
  - Updated channel name link color to match main text color (white in dark mode) instead of accent color.
- **Database Schema**
  - Updated `User` model to include `date_of_birth` column.
  - Added `age` property to `User` model for dynamic calculation.

## [0.8.1] - 2025-12-02

### Security
- **Fixed Information Exposure Vulnerability**:
  - Patched `views.py` and `test.py` to prevent returning raw exception messages to the client in the voice search API.
  - Generic error messages are now returned to the user, while detailed errors are logged server-side.

## [0.8.0] - 2025-12-02

### Added
- **Voice Search Capability**
  - Implemented voice search using `SpeechRecognition` and `Vosk` for offline support.
  - Added microphone button to the search bar with pulsing visual feedback.
  - Added backend API endpoint `/voice_search` to handle audio processing securely.
  - Integrated `static-ffmpeg` for reliable audio conversion across environments.
  - Added `voice.py` module for natural language query processing (e.g., "Show me funny cats" -> "funny cats").
- **Enhanced Search UI**
  - Redesigned search bar with a modern, unified container.
  - Added search icon button and improved focus states.
  - Added real-time feedback ("Listening...", "Processing...") and error handling.

### Changed
- **Configuration**
  - Un-hardcoded sensitive configuration values (`SECRET_KEY`, `VOSK_MODEL_PATH`) to use environment variables.
  - Updated `app.py` and `test.py` to respect these environment variables.

## [0.7.2] - 2025-12-02

### Security
- **Fixed DOM-based XSS Vulnerability**:
  - Patched `static/player.js` to prevent potential DOM text reinterpretation as HTML by normalizing video URLs before assignment.
- **Fixed Open Redirect Vulnerabilities**:
  - Removed unsafe usage of `request.referrer` in `views.py` and `test.py` to prevent open redirect attacks.
  - Replaced redirects with explicit `url_for` routing.
- **Hardened Configuration**:
  - Disabled Flask debug mode by default in `test.py` (now controlled via `FLASK_DEBUG` environment variable).

## [0.7.1] - 2025-12-02

### Fixed
- Fixed security vulnerability #19

## [0.7.0] - 2025-12-01

### Added
- **Machine Learning Recommendation Engine**
  - Implemented a content-based filtering algorithm to personalize video feeds.
  - **Vector-Based Profiling**: Builds weighted user profile vectors based on watch history (Categories, Tags, Channels).
  - **Dynamic Weighting**:
    - **Recency Decay**: Recent views are weighted higher (5% decay per step).
    - **Replay Boosting**: Repeated views increase feature weights logarithmically.
    - **Short-Term Context**: Immediate last 2 videos get a massive 2.5x weight boost to capture "current mood".
  - **Similarity Scoring**: Recommendations are generated via dot product similarity between user vectors and video attributes.
  - **Homepage Sections**:
    - **For You**: Personalized recommendations for logged-in users; random selection for guests.
    - **Latest**: Most recent uploads.
    - **Trending**: Most viewed videos.
    - **From <Channel>**: Videos from a channel the user watches frequently.
  - **Up Next**: "Watch" page suggestions are now powered by the ML engine for logged-in users.

### Changed
- **Homepage Redesign**:
  - Replaced single "Recommended" list with categorized sections ("For You", "Latest", "Trending", "From Channel").
  - Sections are dynamically hidden if empty or not applicable (e.g., for new users).
  - Limited each section to 4 videos for a cleaner layout.
- **Database Schema**:
  - Added `category` and `tags` columns to `Video` model.
  - Added `ViewHistory` model to track user viewing activity with timestamps.
  - Updated `init_db` to automatically migrate schema for new columns.
- **Upload Flow**:
  - Added **Category** dropdown and **Tags** input to the video upload form.

## [0.6.1] - 2025-12-01

### Fixed
- Fixed player visibility in fullscreen mode.

## [0.6.0] - 2025-12-01

### Added
- **Asynchronous Comments System**
  - Implemented `Comment` model with user and video relationships.
  - Added API endpoints for adding and deleting comments (`/video/<id>/comment`, `/comment/<id>/delete`).
  - Updated `watch.html` to display comments section with user avatars and timestamps.
  - Integrated `async_actions.js` to handle comment submission and deletion without page reloads.
  - Comments update dynamically in the UI upon submission.

## [0.5.4] - 2025-12-01

### Changed
- Replaced all UI emojis with SVG icons for better visual consistency and scalability.
  - Player controls (Play, Pause, Mute, Volume, Theatre, Fullscreen, Replay).
  - Theme toggle (Sun/Moon).
  - Interaction buttons (Like, Dislike).
  - Added Bell icon to Subscribe button.
  - Video thumbnail placeholders.

## [0.5.3] - 2025-12-01

### Fixed
- Fixed asynchronous actions (like, dislike, subscribe) causing page reloads.
- Fixed issue where `form.action` was shadowed by input named "action", breaking AJAX requests.
- Improved AJAX detection in backend to support `ajax=1` query parameter.
- Updated `base.html` to reference the correct `async_actions.js` script.

## [0.5.2] - 2025-12-01

### Fixed
- Fixed video player timer logic to correctly display hours for long videos (e.g. 1:30:21 instead of 30:21).

## [0.5.1] - 2025-12-01

### Changed
- Increased maximum video upload size limit to 16GB (from 2GB).

## [0.5.0] - 2025-12-01

### Fixed
- Fixed issue with search causing error.

## [0.4.2] - 2025-11-30

### Changed
- UI improvements merged from UI branch.

## [0.4.1] - 2025-11-29

### Fixed
- **Template & Route Compatibility**
  - Refactored `test.py` to use Flask Blueprints (`main`, `auth`) matching the production app structure.
  - Updated all templates (`base.html`, `home.html`, `user.html`, etc.) to use namespaced `url_for` calls (e.g., `main.home`).
  - Fixed `BuildError` caused by mismatched endpoint names between templates and route definitions.
  - Added missing `/search` route to `views.py` to prevent crashes.

- **File Uploads & Serving**
  - Fixed profile picture upload paths in `auth.py` to explicitly use forward slashes for compatibility.
  - Updated `uploaded_file` route in `test.py` to support serving files from subdirectories (e.g., `uploads/profiles/`).
  - Fixed issue where uploaded profile pictures were not displaying due to incorrect URL generation.

- **View Counting**
  - Reverted view counting logic to correctly exclude video owners from incrementing their own view counts.

## [0.4.0] - 2025-11-29

### Added
- **Video Player Theatre Mode**
  - Now video player can switch to theatre mode, giving best viewing experience.

### Fixed
- Fixed fullscreen mode to include proper aspect ratio.

## [0.3.1] - 2025-11-29

### Added
- **Video Player Replay Functionality**
  - Replay button (🔄) appears when video ends
  - Large centered replay button (96px circle)
  - Play button changes to replay icon when video ends
  - Works with both HTML5 and YouTube videos
  - Multiple replay methods: center button, control button, or space bar
  - Replay button stays above "Up Next" overlay
  - Enhanced visual feedback with hover effects
  
- **Player Visual Enhancements**
  - Replay button hover effect: darker background + scale(1.05)
  - Smooth transitions (0.2s ease)
  - Darker replay button background for better visibility
  - Replay button z-index increased to 35 (above overlay at 30)

### Changed
- Modified `player.js` to handle video end state
- Added `showReplayBtn()` and `hideReplayBtn()` helper functions
- Updated play button click behavior to detect ended state
- Updated big play button to handle replay functionality
- Enhanced `.vf-bigplay` CSS with z-index and hover effects
- "Play Next" button now properly resets replay state

### Fixed
- Replay button now stays clickable above "Up Next" overlay
- No interference between replay and "Up Next" features
- Video properly restarts from beginning on replay
- Button states correctly managed across play/pause/replay

## [0.3.0] - 2025-11-29

### Added
- **Comprehensive Form Element Styling**
  - Enhanced all input types with theme-aware styling
  - Custom file upload button with accent color and hover effects
  - Styled select dropdowns with proper focus/hover states
  - Textarea with vertical resize and minimum height
  - Number input with visible spin buttons
  - Checkbox and radio button styling with accent color
  - Form validation states (valid/invalid with color indicators)
  - Disabled state styling with reduced opacity
  - Label styling with bold font and proper spacing
  - Placeholder styling with secondary text color
  - Range input slider styling for volume controls
  
- **Visual Feedback Enhancements**
  - Smooth transitions (0.2s ease) on all form interactions
  - Focus glow effect with accent color shadow
  - Hover border color changes
  - File selector button hover animation with transform
  - Upload progress bar styling (for future implementation)

### Fixed
- **Select Dropdown Rendering**
  - Removed `appearance: none` that broke native dropdown functionality
  - Removed custom SVG arrow that caused display issues
  - Dropdowns now open and display options correctly
  
- **Video Player Controls**
  - Fixed range input (volume slider) being affected by global input styles
  - Excluded range, checkbox, and radio inputs from global form styles
  - Added specific overrides for range input hover/focus states
  - Video seek bar and volume slider now work properly without conflicts

### Changed
- Enhanced CSS selector specificity for form elements
- Form elements now use `input:not([type="range"]):not([type="checkbox"]):not([type="radio"])` selector
- Range inputs have dedicated styling separate from text inputs
- Search input expands on focus (400px → 500px)
- All form elements maintain consistent 8px border-radius

## [0.2.1] - 2025-11-29

### Fixed
- **Subscribe Button Async Update**
  - Fixed subscribe button not updating text/style without page reload
  - Added subscribe action handling in `async_actions_simple.js`
  - Updated `user.html` template with proper classes (`js-async-form`, `js-subscribe-btn`)
  - Added `data-action="subscribe"` attribute to forms
  - Wrapped subscriber count in `<span id="subs-count">` for dynamic updates
  - Button now correctly toggles between "Subscribe" and "Subscribed"
  - Button style now toggles between `btn-accent` and `btn-primary`
  - Subscriber count updates in real-time on user profile pages

### Changed
- Improved async form handler to support multiple action types (like, dislike, subscribe)
- Added conditional logic to handle different action responses
- Enhanced console logging for subscribe actions with `[ASYNC]` prefix

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
