import random

import pandas as pd
import requests
import streamlit as st

# Mood-Based Music Recommender
# Python 3.10 | Streamlit | Apple iTunes Search API (no API key required)

st.set_page_config(
    page_title="MoodTune | Mood-Based Music",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)

MOODS = {
    "Happy 😊": {"genres": ["Pop", "Dance", "Disco", "Afrobeats"], "terms": ["feel good", "happy hits", "upbeat"]},
    "Sad 😢": {"genres": ["Acoustic", "Indie", "R&B", "Soft Pop"], "terms": ["sad songs", "heartbreak", "melancholy"]},
    "Relaxed 😌": {"genres": ["Ambient", "Jazz", "Acoustic", "Classical"], "terms": ["relaxing", "chill", "calm"]},
    "Energetic ⚡": {"genres": ["EDM", "Rock", "Dance", "Hip-Hop"], "terms": ["workout", "high energy", "party"]},
    "Romantic ❤️": {"genres": ["R&B", "Pop", "Soul", "Acoustic"], "terms": ["love songs", "romantic", "love ballads"]},
    "Angry 😠": {"genres": ["Rock", "Metal", "Hip-Hop", "Punk"], "terms": ["hard rock", "intense", "powerful"]},
    "Anxious 😟": {"genres": ["Ambient", "Classical", "Lo-fi", "Acoustic"], "terms": ["calming", "peaceful", "stress relief"]},
    "Nostalgic 🕰️": {"genres": ["Classic Pop", "Rock", "Soul", "Oldies"], "terms": ["throwback", "classic hits", "oldies"]},
    "Focused 🧠": {"genres": ["Lo-fi", "Instrumental", "Ambient", "Classical"], "terms": ["study beats", "focus music", "instrumental"]},
    "Motivated 🚀": {"genres": ["Hip-Hop", "Rock", "Pop", "EDM"], "terms": ["motivation", "inspirational", "power"]},
    "Lonely 🌙": {"genres": ["Indie", "Acoustic", "R&B", "Jazz"], "terms": ["late night", "lonely", "introspective"]},
    "Hopeful 🌅": {"genres": ["Pop", "Gospel", "Indie", "Folk"], "terms": ["hope", "inspiring", "new beginnings"]},
    "Stressed 😫": {"genres": ["Ambient", "Lo-fi", "Jazz", "Classical"], "terms": ["stress relief", "relaxing piano", "unwind"]},
    "Adventurous 🧭": {"genres": ["World", "Afrobeats", "Latin", "Rock"], "terms": ["adventure", "travel", "explore"]},
    "Sleepy 😴": {"genres": ["Ambient", "Classical", "Acoustic", "Jazz"], "terms": ["sleep", "soft piano", "lullaby"]},
}

GENRES = [
    "Any", "Pop", "Rock", "Hip-Hop", "R&B", "EDM", "Dance", "Jazz",
    "Classical", "Acoustic", "Indie", "Lo-fi", "Ambient", "Metal",
    "Soul", "Latin", "Country", "Reggae", "Folk", "Gospel", "Afrobeats",
    "Disco", "Instrumental", "K-Pop", "Soundtrack"
]
LANGUAGES = [
    "Any language", "English", "Urdu", "Hindi", "Punjabi", "Arabic",
    "Spanish", "Korean", "Japanese", "French", "Turkish", "Bengali",
    "Pashto", "Persian"
]
LANGUAGE_TERMS = {
    "Any language": "",
    "English": "English",
    "Urdu": "Urdu Pakistani",
    "Hindi": "Hindi Bollywood",
    "Punjabi": "Punjabi",
    "Arabic": "Arabic",
    "Spanish": "Spanish",
    "Korean": "K-pop Korean",
    "Japanese": "Japanese",
    "French": "French",
    "Turkish": "Turkish",
    "Bengali": "Bengali",
    "Pashto": "Pashto",
    "Persian": "Persian Farsi",
}
COUNTRY_CODES = {
    "Any language": "us", "English": "us", "Urdu": "pk", "Hindi": "in",
    "Punjabi": "in", "Arabic": "sa", "Spanish": "es", "Korean": "kr",
    "Japanese": "jp", "French": "fr", "Turkish": "tr", "Bengali": "in",
    "Pashto": "pk", "Persian": "us",
}

def api_search(term, country="us", limit=25):
    """Search real tracks through Apple's public iTunes Search API."""
    url = "https://itunes.apple.com/search"
    params = {
        "term": term,
        "entity": "song",
        "media": "music",
        "limit": limit,
        "country": country,
    }
    try:
        response = requests.get(url, params=params, timeout=12)
        response.raise_for_status()
        payload = response.json()
        results = []
        for item in payload.get("results", []):
            title = item.get("trackName")
            artist = item.get("artistName")
            if not title or not artist:
                continue
            results.append({
                "Song": title,
                "Artist": artist,
                "Album": item.get("collectionName", "Unknown album"),
                "Genre": item.get("primaryGenreName", "Unknown"),
                "Language": "",  # The catalog API does not reliably expose track language.
                "Artwork": item.get("artworkUrl100", ""),
                "Preview": item.get("previewUrl", ""),
                "Listen": item.get("trackViewUrl", ""),
                "Track ID": item.get("trackId", ""),
            })
        return results, None
    except requests.RequestException as exc:
        return [], str(exc)
    except (ValueError, TypeError) as exc:
        return [], str(exc)

def make_search_terms(mood, genre, language, purpose, custom_query=""):
    mood_name = mood.split(" ", 1)[0]
    mood_data = MOODS.get(mood, MOODS["Happy 😊"])
    selected_genre = "" if genre == "Any" else genre
    lang_term = LANGUAGE_TERMS.get(language, "")
    if custom_query.strip():
        core = custom_query.strip()
    else:
        term = random.choice(mood_data["terms"])
        core = " ".join(x for x in [selected_genre, term, lang_term, purpose] if x)
    # Keep the API search focused rather than sending a long sentence.
    return " ".join(core.split()), COUNTRY_CODES.get(language, "us")

def recommend(mood, genre, language, purpose, custom_query="", limit=25):
    query, country = make_search_terms(mood, genre, language, purpose, custom_query)
    rows, error = api_search(query, country=country, limit=limit)
    # If the first search is too restrictive, retry with a broader query.
    if len(rows) < 5:
        fallback_parts = []
        if genre != "Any":
            fallback_parts.append(genre)
        if language != "Any language":
            fallback_parts.append(LANGUAGE_TERMS.get(language, ""))
        fallback_parts.append(random.choice(MOODS.get(mood, MOODS["Happy 😊"])["terms"]))
        fallback = " ".join(x for x in fallback_parts if x)
        if fallback and fallback.lower() != query.lower():
            more, second_error = api_search(fallback, country=country, limit=limit)
            known = {r["Track ID"] for r in rows}
            rows.extend(r for r in more if r["Track ID"] not in known)
            error = error or second_error
    # De-duplicate by track ID
    unique = {}
    for row in rows:
        unique[row["Track ID"]] = row
    return list(unique.values()), query, error

def add_to_playlist(track):
    existing = {str(t.get("Track ID")) for t in st.session_state.playlist}
    if str(track.get("Track ID")) not in existing:
        st.session_state.playlist.append(track)

def show_track(track, index):
    with st.container(border=True):
        col1, col2 = st.columns([1.15, 4.85], vertical_alignment="center")
        with col1:
            if track.get("Artwork"):
                st.image(track["Artwork"], use_container_width=True)
            else:
                st.markdown('<div class="artwork-fallback">♪</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="track-title">{track["Song"]}</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="track-meta">{track["Artist"]} · {track.get("Album", "Unknown album")}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(f'<span class="genre-pill">{track.get("Genre", "Unknown")}</span>', unsafe_allow_html=True)
            if track.get("Preview"):
                st.audio(track["Preview"])
            elif track.get("Listen"):
                st.link_button("Open in Apple Music", track["Listen"])
            else:
                st.caption("No preview link was supplied for this track.")
            if st.button("＋ Add to my playlist", key=f"add_{index}_{track.get('Track ID')}"):
                add_to_playlist(track)
                st.toast("Added to your playlist", icon="✅")

if "playlist" not in st.session_state:
    st.session_state.playlist = []
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []
if "chat" not in st.session_state:
    st.session_state.chat = [
        {"role": "assistant", "content": "Hi! 🎧 I'm MoodTune. Tell me how you're feeling, and I'll help you find music that fits."}
    ]
if "chat_step" not in st.session_state:
    st.session_state.chat_step = 0
if "chat_answers" not in st.session_state:
    st.session_state.chat_answers = {}

# Spotify-inspired styling
st.markdown("""
<style>
    :root { --ink: #f5f5f5; --muted: #a7a7a7; --green: #1ed760; --panel: #181818; }
    .stApp { background: #121212; color: var(--ink); }
    [data-testid="stHeader"] { background: rgba(18,18,18,.85); }
    [data-testid="stSidebar"] { background: #000; border-right: 1px solid #282828; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #fff; }
    h1, h2, h3 { letter-spacing: -0.6px; color: #fff; }
    .hero {
        padding: 2rem 2.2rem; border-radius: 18px;
        background: linear-gradient(115deg, #1c3d2c 0%, #17652d 48%, #1ed760 150%);
        margin-bottom: 1.4rem; box-shadow: 0 16px 40px rgba(0,0,0,.24);
    }
    .hero h1 { color: white; font-size: 2.6rem; margin-bottom: .25rem; }
    .hero p { color: #e4f8e9; margin-bottom: 0; font-size: 1.05rem; }
    .eyebrow { color: #1ed760; font-size: .75rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
    .track-title { color: #fff; font-size: 1.08rem; font-weight: 700; margin-bottom: .18rem; }
    .track-meta { color: #b3b3b3; font-size: .88rem; margin-bottom: .55rem; }
    .genre-pill {
        display: inline-block; padding: .18rem .55rem; margin-bottom: .45rem;
        border-radius: 999px; background: #282828; color: #b3b3b3; font-size: .72rem;
    }
    .artwork-fallback {
        display: grid; place-items: center; aspect-ratio: 1; border-radius: 8px;
        background: linear-gradient(135deg, #1ed760, #0d5c2a); color: #fff; font-size: 3rem;
    }
    div[data-testid="stMetric"] { background: #181818; border: 1px solid #282828; padding: 14px; border-radius: 12px; }
    div[data-testid="stMetricLabel"] { color: #a7a7a7; }
    div[data-testid="stMetricValue"] { color: #fff; }
    .stButton > button[kind="primary"], .stLinkButton > a {
        background: var(--green); color: #000; border: 0; font-weight: 700;
    }
    .stButton > button[kind="primary"]:hover, .stLinkButton > a:hover { background: #1fdf68; color: #000; }
    div[data-testid="stContainer"] { border-color: #2b2b2b !important; background: #181818; }
    [data-baseweb="tab-list"] { gap: .35rem; }
    [data-baseweb="tab"] { color: #a7a7a7; }
    [aria-selected="true"] { color: #1ed760 !important; }
    .sidebar-brand { padding: .4rem 0 1.1rem; border-bottom: 1px solid #282828; margin-bottom: 1rem; }
    .sidebar-brand strong { color: #fff; font-size: 1.35rem; }
    .sidebar-brand span { color: var(--green); }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="eyebrow">Your personal soundtrack</div>
    <h1>Find the music that feels like you.</h1>
    <p>Tell us your mood and MoodTune will build a fresh soundtrack from real music.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="sidebar-brand"><strong><span>♪</span> MoodTune</strong><br><small>Your mood. Your sound.</small></div>', unsafe_allow_html=True)
    st.markdown("### Tune your discovery")
    mood = st.selectbox("How are you feeling right now?", list(MOODS.keys()), index=0)
    suggested = MOODS[mood]["genres"]
    genre = st.selectbox("Preferred genre", GENRES, index=0)
    language = st.selectbox("Music language", LANGUAGES, index=0)
    purpose = st.selectbox(
        "What are you listening for?",
        ["", "studying", "working out", "sleeping", "driving", "relaxing", "partying", "meditating", "commuting"],
        format_func=lambda x: "Any purpose" if x == "" else x.title()
    )
    result_count = st.slider("Number of recommendations", 5, 30, 15, 5)
    st.caption("Mood picks")
    st.markdown(" · ".join(f"`{item}`" for item in suggested))
    st.divider()
    st.caption(f"{len(st.session_state.playlist)} saved tracks in your library")
    st.caption("Catalog powered by Apple Music. Availability varies by country.")

tab_discover, tab_chat, tab_playlist, tab_about = st.tabs(
    ["✨ Discover music", "💬 Music chatbot", "🎶 My playlist", "ℹ️ About"]
)

with tab_discover:
    st.markdown('<div class="eyebrow">Discover</div>', unsafe_allow_html=True)
    st.subheader("Find your sound")
    left, right = st.columns([3, 2])
    with left:
        custom_query = st.text_input(
            "Optional search",
            placeholder="e.g. Urdu romantic songs, 2000s pop, calm piano",
            help="Leave empty to search based on the mood and preferences selected in the sidebar."
        )
    with right:
        st.write("")
        st.write("")
        find_clicked = st.button("🔎 Find my music", type="primary", use_container_width=True)

    if find_clicked:
        with st.spinner("Searching the music catalog..."):
            tracks, query, error = recommend(
                mood, genre, language, purpose, custom_query, limit=result_count
            )
        st.session_state.recommendations = tracks
        st.session_state.last_query = query
        st.session_state.last_error = error

    tracks = st.session_state.recommendations
    if tracks:
        st.caption(f"Search used: {st.session_state.get('last_query', 'your preferences')}")
        st.write(f"Found **{len(tracks)} tracks**. Preview a track, then save your favourites to your playlist.")
        for idx, track in enumerate(tracks):
            show_track(track, idx)
    else:
        st.info("Choose your mood, genre, and language in the sidebar, then select **Find my music**.")
        st.markdown("### Start with a vibe")
        quick_cols = st.columns(3)
        quick_moods = ["Happy 😊", "Relaxed 😌", "Energetic ⚡"]
        for i, qm in enumerate(quick_moods):
            with quick_cols[i]:
                st.markdown(f"**{qm}**")
                st.caption(", ".join(MOODS[qm]["genres"][:3]))

    if st.session_state.get("last_error") and not tracks:
        st.warning("The online music catalog could not be reached. Check your internet connection and try again.")

with tab_chat:
    st.subheader("Chat with MoodTune")
    st.write("Answer a few quick questions and the bot will build recommendations around your answers.")
    for message in st.session_state.chat:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.chat_step < 3:
        prompts = [
            ("mood", "What's your current mood?", list(MOODS.keys())),
            ("genre", "Which genre would you like?", GENRES),
            ("language", "Which language should the songs be in?", LANGUAGES),
        ]
        key, question, options = prompts[st.session_state.chat_step]
        with st.form(key=f"chat_form_{st.session_state.chat_step}"):
            answer = st.selectbox(question, options, key=f"chat_answer_{key}")
            submitted = st.form_submit_button("Send answer", type="primary")
        if submitted:
            st.session_state.chat_answers[key] = answer
            st.session_state.chat.append({"role": "user", "content": answer})
            st.session_state.chat.append({"role": "assistant", "content": [
                "Thanks! I'll use that mood to guide the recommendations.",
                "Nice choice. Your genre preference is saved.",
                "Great! I'll use your language preference in the music search."
            ][st.session_state.chat_step]})
            st.session_state.chat_step += 1
            st.rerun()
    else:
        st.success("Your music profile is ready!")
        answers = st.session_state.chat_answers
        st.write(
            f"**Mood:** {answers.get('mood', 'Happy 😊')}  \n"
            f"**Genre:** {answers.get('genre', 'Any')}  \n"
            f"**Language:** {answers.get('language', 'Any language')}"
        )
        purpose_chat = st.selectbox(
            "Optional listening purpose",
            ["", "studying", "working out", "sleeping", "driving", "relaxing", "partying", "meditating"],
            key="chat_purpose"
        )
        if st.button("🎧 Build my recommendations", type="primary"):
            with st.spinner("Finding songs for your mood..."):
                recs, query, error = recommend(
                    answers.get("mood", "Happy 😊"),
                    answers.get("genre", "Any"),
                    answers.get("language", "Any language"),
                    purpose_chat,
                    limit=20
                )
            st.session_state.recommendations = recs
            st.session_state.last_query = query
            st.session_state.last_error = error
            st.session_state.chat.append({
                "role": "assistant",
                "content": f"I searched for **{answers.get('mood')}** music in **{answers.get('language')}**. I found {len(recs)} tracks. Open the **Discover music** tab to preview and add them to your playlist."
            })
            st.rerun()
        if st.button("🔄 Start chat again"):
            st.session_state.chat = [
                {"role": "assistant", "content": "Hi again! 🎧 Let's build a new soundtrack for your mood."}
            ]
            st.session_state.chat_step = 0
            st.session_state.chat_answers = {}
            st.rerun()

with tab_playlist:
    st.subheader("Your personal playlist")
    playlist = st.session_state.playlist
    metric_cols = st.columns(3)
    metric_cols[0].metric("Saved tracks", len(playlist))
    metric_cols[1].metric("Unique artists", len({x["Artist"] for x in playlist}))
    metric_cols[2].metric("Moods supported", len(MOODS))
    if not playlist:
        st.info("Your playlist is empty. Go to Discover music and select **Add to my playlist** on any track.")
    else:
        for idx, track in enumerate(playlist):
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 5, 1])
                with c1:
                    if track.get("Artwork"):
                        st.image(track["Artwork"], use_container_width=True)
                with c2:
                    st.markdown(f"**{track['Song']}**")
                    st.caption(f"{track['Artist']} · {track.get('Album', 'Unknown album')}")
                    if track.get("Listen"):
                        st.markdown(f"[Listen / open track]({track['Listen']})")
                with c3:
                    if st.button("Remove", key=f"remove_{idx}_{track.get('Track ID')}"):
                        st.session_state.playlist.pop(idx)
                        st.rerun()

        df = pd.DataFrame(playlist)
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Download playlist as CSV",
            data=csv,
            file_name="moodtune_playlist.csv",
            mime="text/csv",
            type="primary"
        )
        if st.button("🗑️ Clear playlist"):
            st.session_state.playlist = []
            st.rerun()

with tab_about:
    st.subheader("About this project")
    st.markdown("""
    **MoodTune** is a mood-based music discovery application built with Python and Streamlit.

    **How it works**
    1. The user selects a mood, genre, language, and listening purpose.
    2. A mood-to-genre mapping suggests suitable search themes.
    3. The app searches a real online music catalog and presents returned tracks.
    4. The user previews tracks where available and saves favourites to a personal playlist.

    **Important limitations**
    - The chatbot in this version is a guided, rule-based chatbot, not a generative AI model. It asks structured questions and uses the answers to search music.
    - Mood-to-genre associations are suggestions, not psychological assessments.
    - Language filtering is approximate because the catalog does not reliably expose a language field for every song.
    - The app does not download full copyrighted songs. It links to the catalog and uses preview clips when available.
    - The iTunes Search API's promotional content and preview assets are subject to Apple's terms. Keep previews near the relevant store link and review the current terms before public or commercial deployment.
    """)
    st.markdown("**Data source:** [Apple iTunes Search API documentation](https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/).")
    st.markdown("**Alternative metadata source:** [MusicBrainz API](https://musicbrainz.org/doc/MusicBrainz_API), which provides music metadata and has rate limits.")

st.caption("MoodTune · A Python 3.10 student project · Music availability and previews depend on catalog and region.")
