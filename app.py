import pickle
import os
import gdown
import streamlit as st
import requests
from dotenv import load_dotenv

# ── Load environment variables ───────────────────
load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

# ── Google Drive file IDs ────────────────────────
CREDITS_FILE_ID = "1nrmYKrMICVCoozy5B5VsBl8E3TZmvsBy"
MOVIES_FILE_ID  = "1Zmlh6p2P6tX5otVUlSzpxbA_sm7Ediin"

# ── Auto-download CSVs if missing ────────────────
os.makedirs("model", exist_ok=True)

if not os.path.exists("tmdb_5000_credits.csv"):
    with st.spinner("⬇️ Downloading credits data..."):
        gdown.download(f"https://drive.google.com/uc?id={CREDITS_FILE_ID}", "tmdb_5000_credits.csv", quiet=False)

if not os.path.exists("tmdb_5000_movies.csv"):
    with st.spinner("⬇️ Downloading movies data..."):
        gdown.download(f"https://drive.google.com/uc?id={MOVIES_FILE_ID}", "tmdb_5000_movies.csv", quiet=False)

# ── Auto-generate model if pkl files missing ─────
if not os.path.exists("model/movie_list.pkl") or not os.path.exists("model/similarity.pkl"):
    with st.spinner("🤖 Building recommendation model (only happens once)..."):
        import pandas as pd
        import ast
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import nltk
        from nltk.stem.porter import PorterStemmer

        nltk.download('punkt', quiet=True)

        movies_df  = pd.read_csv("tmdb_5000_movies.csv")
        credits_df = pd.read_csv("tmdb_5000_credits.csv")

        movies_df = movies_df.merge(credits_df, on='title')

        movies_df = movies_df[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
        movies_df.dropna(inplace=True)

        def convert(obj):
            return [i['name'] for i in ast.literal_eval(obj)]

        def convert3(obj):
            return [i['name'] for i in ast.literal_eval(obj)[:3]]

        def fetch_director(obj):
            return [i['name'] for i in ast.literal_eval(obj) if i['job'] == 'Director']

        movies_df['genres']   = movies_df['genres'].apply(convert)
        movies_df['keywords'] = movies_df['keywords'].apply(convert)
        movies_df['cast']     = movies_df['cast'].apply(convert3)
        movies_df['crew']     = movies_df['crew'].apply(fetch_director)
        movies_df['overview'] = movies_df['overview'].apply(lambda x: x.split())

        for col in ['genres', 'keywords', 'cast', 'crew']:
            movies_df[col] = movies_df[col].apply(lambda x: [i.replace(" ", "") for i in x])

        movies_df['tags'] = (
            movies_df['overview'] +
            movies_df['genres'] +
            movies_df['keywords'] +
            movies_df['cast'] +
            movies_df['crew']
        )

        new_df = movies_df[['movie_id', 'title', 'tags']].copy()
        new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x).lower())

        ps = PorterStemmer()
        new_df['tags'] = new_df['tags'].apply(
            lambda x: " ".join([ps.stem(word) for word in x.split()])
        )

        cv  = CountVectorizer(max_features=5000, stop_words='english')
        vectors    = cv.fit_transform(new_df['tags']).toarray()
        similarity = cosine_similarity(vectors)

        pickle.dump(new_df, open('model/movie_list.pkl', 'wb'))
        pickle.dump(similarity, open('model/similarity.pkl', 'wb'))

        st.success("✅ Model built successfully! Reloading...")
        st.rerun()


# ── Helper functions ─────────────────────────────
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
    recommended_movie_names   = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        title = movies.iloc[i[0]].title
        recommended_movie_posters.append(fetch_poster(title))
        recommended_movie_names.append(title)
    return recommended_movie_names, recommended_movie_posters


# ── PAGE CONFIG ──────────────────────────────────
st.set_page_config(page_title="CineMatch", page_icon="🎬", layout="wide")

# ── CUSTOM CSS ───────────────────────────────────
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

# ── HERO ─────────────────────────────────────────
st.markdown("""
    <div class='hero'>
        <h1>🎬 CineMatch</h1>
        <p>Discover movies you'll love — powered by AI</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── LOAD MODEL ───────────────────────────────────
movies     = pickle.load(open('model/movie_list.pkl', 'rb'))
similarity = pickle.load(open('model/similarity.pkl', 'rb'))
movie_list = movies['title'].values

# ── SEARCH UI ────────────────────────────────────
col_left, col_mid, col_right = st.columns([1, 3, 1])
with col_mid:
    selected_movie = st.selectbox("🎥 Search for a movie", movie_list)
    search_btn = st.button('✨ Find Similar Movies')

st.markdown("<br>", unsafe_allow_html=True)

# ── RESULTS ──────────────────────────────────────
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