# ViewFlow

**Version:** 0.8.0

ViewFlow is a modern, lightweight video sharing platform prototype built with Flask. It features a custom-built video player, a sophisticated recommendation engine, and a sleek, theme-aware user interface.

## 🚀 Key Features

### 🧠 Machine Learning Recommendation Engine
ViewFlow now includes a powerful content-based filtering system that personalizes the viewing experience:
- **Vector-Based Profiling**: Builds a dynamic user profile vector based on watched categories, tags, and channels.
- **Smart Context Awareness**:
  - **Recency Decay**: Prioritizes recent interests over older history.
  - **Replay Boosting**: Detects and boosts content you watch repeatedly.
  - **"Current Mood"**: Heavily weights the last 2 videos to adapt instantly to your current session.
- **Personalized Feeds**:
  - **For You**: A curated list of videos matching your unique taste profile.
  - **From Your Channels**: Highlights content from creators you engage with most.
  - **Up Next**: Intelligent suggestions that keep the binge going.

### 🎬 Advanced Video Player
A custom-built, themeable HTML5 player that rivals major platforms:
- **Universal Support**: Plays local video uploads and YouTube embeds seamlessly.
- **Theatre & Fullscreen Modes**: Immersive viewing options.
- **Replay System**: Large, intuitive replay controls when a video ends.
- **Ambient Mode**: Dynamic background lighting effects based on video content.

### 👤 Enhanced User Experience
- **Rich Profiles**: Customize your presence with profile pictures, bio, location, and more.
- **Social Interactions**: Like, dislike, subscribe, and comment asynchronously without page reloads.
- **Dark/Light Mode**: A beautiful, persistent theme system that respects your eyes.
- **Responsive Design**: Fully responsive layout that looks great on desktop and mobile.

### 🛠️ Developer Friendly
- **Zero-Config Setup**: Automatically initializes the database and storage directories.
- **Auto-Migration**: Best-effort SQLite schema migration for rapid prototyping.
- **Modular Architecture**: Clean separation of concerns with Flask Blueprints.

## 📦 Quick Start

### Prerequisites
- Python 3.10+

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