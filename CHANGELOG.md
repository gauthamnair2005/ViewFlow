# Changelog

All notable changes to this project will be documented in this file.

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
