import pickle
import streamlit as st
import requests
import os
from dotenv import load_dotenv

# ── Load environment variables from .env file ───
load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

def fetch_poster(movie_title):
    try:
        url = f"http://www.omdbapi.com/?t={requests.utils.quote(movie_title)}&apikey={OMDB_API_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()
        poster = data.get("Poster")
        if poster and poster != "N/A":
            return poster
        return get_placeholder(movie_title)
    except Exception:
        return get_placeholder(movie_title)

def get_placeholder(title):
    encoded = requests.utils.quote(title[:20])
    return f"https://placehold.co/300x450/1a1a2e/white?text={encoded}"

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        title = movies.iloc[i[0]].title
        recommended_movie_posters.append(fetch_poster(title))
        recommended_movie_names.append(title)
    return recommended_movie_names, recommended_movie_posters

# ── PAGE CONFIG ─────────────────────────────────
st.set_page_config(page_title="CineMatch", page_icon="🎬", layout="wide")

# ── CUSTOM CSS ──────────────────────────────────
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    * { font-family: 'Poppins', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        min-height: 100vh;
    }
    .hero {
        text-align: center;
        padding: 50px 20px 20px 20px;
    }
    .hero h1 {
        font-size: 3.2em;
        font-weight: 700;
        background: linear-gradient(90deg, #f953c6, #b91d73);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    .hero p {
        color: #aaa;
        font-size: 1.1em;
        margin-top: 0;
    }
    .stSelectbox label {
        color: #ddd !important;
        font-size: 1em !important;
        font-weight: 600 !important;
    }
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        color: white !important;
        font-size: 1em !important;
    }
    .stButton > button {
        background: linear-gradient(90deg, #f953c6, #b91d73) !important;
        color: white !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 12px 40px !important;
        font-size: 1em !important;
        font-weight: 600 !important;
        width: 100% !important;
        margin-top: 10px !important;
        cursor: pointer !important;
        transition: opacity 0.2s !important;
    }
    .stButton > button:hover { opacity: 0.85 !important; }
    .movie-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 12px;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
    }
    .movie-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(249, 83, 198, 0.3);
    }
    .movie-card img { border-radius: 10px; width: 100%; }
    .movie-name {
        color: #ffffff;
        font-size: 0.85em;
        font-weight: 600;
        margin-top: 10px;
        line-height: 1.3;
    }
    .section-title {
        color: white;
        font-size: 1.4em;
        font-weight: 700;
        margin: 30px 0 20px 0;
        border-left: 4px solid #f953c6;
        padding-left: 12px;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ── HERO ────────────────────────────────────────
st.markdown("""
    <div class='hero'>
        <h1>🎬 CineMatch</h1>
        <p>Discover movies you'll love — powered by AI</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── LOAD MODEL ──────────────────────────────────
movies     = pickle.load(open('model/movie_list.pkl', 'rb'))
similarity = pickle.load(open('model/similarity.pkl', 'rb'))
movie_list = movies['title'].values

# ── SEARCH UI ───────────────────────────────────
col_left, col_mid, col_right = st.columns([1, 3, 1])
with col_mid:
    selected_movie = st.selectbox("🎥 Search for a movie", movie_list)
    search_btn = st.button('✨ Find Similar Movies')

st.markdown("<br>", unsafe_allow_html=True)

# ── RESULTS ─────────────────────────────────────
if search_btn:
    with st.spinner('🍿 Finding your next favourite movies...'):
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

    st.markdown("<div class='section-title'>🍿 You might also like</div>", unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]

    for idx, col in enumerate(cols):
        with col:
            st.markdown(f"""
                <div class='movie-card'>
                    <img src='{recommended_movie_posters[idx]}' />
                    <div class='movie-name'>{recommended_movie_names[idx]}</div>
                </div>
            """, unsafe_allow_html=True)