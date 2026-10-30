# MoodTune — Mood-Based Music Recommender

A Streamlit application for Python 3.10. It recommends real catalog tracks based on a user's mood, preferred genre, language, and listening purpose. It includes a guided chatbot and a playlist builder with CSV export.

## Features

- 15 selectable moods
- Genre and language preferences
- Real music metadata from Apple's iTunes Search API
- Artwork, preview clips when available, and links to tracks
- Guided chatbot that asks about mood, genre, and language
- Add/remove tracks from a session playlist
- Download playlist as CSV
- Spotify-inspired dark interface with a green accent, compact track cards, and responsive layout
- No API key required for the iTunes Search API

## Requirements

- Python 3.10
- Internet connection
- VS Code (recommended)

## Setup in VS Code

Open the project folder in VS Code, then open the terminal in that folder.

### Windows

```powershell
py -3.10 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If `py -3.10` is not recognized, use the full path to your Python 3.10 executable to create the virtual environment.

### macOS / Linux

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Streamlit will print a local URL, usually `http://localhost:8501`. Open it in your browser.

## How to use

1. Select a mood, genre, language, and listening purpose in the sidebar.
2. Open **Discover music** and press **Find my music**.
3. Preview songs where a preview URL is provided.
4. Add favourite tracks to **My playlist**.
5. Or use **Music chatbot** to answer the mood, genre, and language questions, then build recommendations.
6. Download the playlist as CSV when you're ready.

## Notes

- Music results depend on your internet connection, region, and the online catalog.
- Language matching is approximate; not every returned track has a verified language field.
- This starter chatbot is rule-based. To make it a generative AI chatbot, connect an LLM provider and store its API key in Streamlit secrets or environment variables.
- Do not download or redistribute copyrighted music. Preview and store-link use must follow the relevant provider's current terms.
