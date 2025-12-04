# <img src="static/logo.svg" alt="ViewFlow Logo" width="40" height="40" style="vertical-align: -5px;"> ViewFlow

**Version:** 1.0.1

_Last updated: 2025-12-04T16:08:40.073Z_

ViewFlow is a modern, lightweight video sharing platform prototype built with Flask. It features a custom-built video player, a sophisticated recommendation engine, and a sleek, theme-aware user interface.

## 🚀 Key Features

### 📊 Analytics & Insights
Empower creators with data-driven insights directly on their profile:
- **Dashboard**: A dedicated "Analytics" tab for channel owners.
- **Visual Charts**: Interactive graphs showing **Views** and **New Subscribers** over the last 30 days.
- **Performance Metrics**: Track total views, subscriber count, and video library size.
- **Top Content**: Identify your best-performing videos at a glance.

### 🎬 Advanced Video Player
A custom-built, themeable HTML5 player that rivals major platforms:
- **"Most Replayed" Heatmap**: A YouTube-style graph overlay on the seek bar showing the most popular segments of a video.
- **Seek Previews**: Hover over the timeline to see a thumbnail preview of that exact moment.
- **Resolution Switching**: Seamlessly switch between 720p, 480p, and 360p qualities.
- **Seamless Playback**: Plays uploaded videos seamlessly with a modern HTML5 interface.
- **Theatre & Fullscreen Modes**: Immersive viewing options.
- **Ambient Mode**: Dynamic background lighting effects based on video content.

### 🛠️ Content Management
- **Background Uploads**: Videos process asynchronously (transcoding, thumbnail generation) so you can keep browsing.
- **Edit Details**: Update video titles, descriptions (with **Markdown** support), categories, and tags anytime.
- **Visibility Control**: Instantly toggle videos between **Public** and **Private** with a single click.
- **Smart Progress**: Real-time upload status indicators on your profile icon.

### 🧠 Machine Learning Recommendation Engine
ViewFlow includes a powerful content-based filtering system that personalizes the viewing experience:
- **Vector-Based Profiling**: Builds a dynamic user profile vector based on watch history.
- **Smart Context Awareness**:
  - **Recency Decay**: Prioritizes recent interests over older history.
  - **Replay Boosting**: Detects and boosts content you watch repeatedly.
  - **"Current Mood"**: Heavily weights the last 2 videos to adapt instantly to your current session.
- **Personalized Feeds**: "For You", "From Your Channels", and "Up Next" suggestions.

### 👤 Enhanced User Experience
- **Rich Profiles**: Customize your presence with profile pictures, bio, location, and more.
- **Social Interactions**: Like, dislike, subscribe, and comment asynchronously without page reloads.
- **Dark/Light Mode**: A beautiful, persistent theme system that respects your eyes.
- **Responsive Design**: Fully responsive layout that looks great on desktop and mobile.

## 📦 Quick Start

### Prerequisites
- Python 3.10+
- FFmpeg (for video processing)

### Installation

1. **Clone and Setup**
   ```bash
   # Create a virtual environment
   python3 -m venv .venv
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Run the Server**
   ```bash
   python3 test.py
   ```
   The server will start on `http://127.0.0.1:5000`.

   *Note: The application will automatically create a `viewflow.db` database and an `uploads/` directory on the first run.*

## 🏗️ Project Structure

- **`test.py`**: The main entry point and development server. Contains models and route logic.
- **`recommendations.py`**: The core logic for the ML recommendation engine.
- **`templates/`**: Jinja2 templates for the frontend.
- **`static/`**: CSS, JavaScript, and assets.
- **`models.py`**: SQLAlchemy database models.
- **`views.py`**: Route definitions (mirrored in `test.py` for the dev server).

## 🤝 Contributing

This project is a prototype for educational and development purposes. Feel free to fork, experiment, and submit pull requests!

---
*Developed by Gautham Nair & Deepak Patel*
