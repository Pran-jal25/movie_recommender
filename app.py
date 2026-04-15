import streamlit as st
import pickle
import pandas as pd
import requests
import os

st.set_page_config(page_title="YourMatch", page_icon="🎬", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: radial-gradient(ellipse at top, #1b1040 0%, #0d0d1a 60%); color: #fff; }
    .hero { text-align: center; padding: 3.5rem 1rem 1rem; }
    .hero h1 {
        font-size: 3.6rem; font-weight: 700;
        background: linear-gradient(90deg, #f7971e, #ffd200);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin: 0 0 0.5rem; line-height: 1.1;
    }
    .hero p { font-size: 1.05rem; color: #9b93bb; margin: 0; }
    .stSelectbox label { display: none; }
    .stSelectbox > div > div {
        background-color: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important; color: #fff !important; font-size: 1rem;
    }
    .stButton > button {
        background: linear-gradient(90deg, #f7971e, #ffd200);
        color: #1a1a2e; font-weight: 700; font-size: 1rem;
        border: none; border-radius: 12px; padding: 0.7rem 2rem;
        width: 100%; margin-top: 0.8rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(247,151,30,0.45); }
    .section-label {
        text-align: center; font-size: 1.25rem; font-weight: 600;
        color: #ffd200; margin: 2.5rem 0 1.2rem;
        letter-spacing: 0.05em; text-transform: uppercase;
    }
    .movie-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 18px; padding: 0.7rem; text-align: center;
        transition: transform 0.28s ease, box-shadow 0.28s ease, border-color 0.28s ease;
    }
    .movie-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 48px rgba(0,0,0,0.6);
        border-color: rgba(255,210,0,0.35);
    }
    .movie-card img { border-radius: 12px; width: 100%; display: block; }
    .movie-title { margin-top: 0.65rem; font-size: 0.82rem; font-weight: 600; color: #ddd6f3; line-height: 1.35; }
    .rank-badge {
        display: inline-block;
        background: linear-gradient(90deg, #f7971e, #ffd200);
        color: #1a1a2e; font-size: 0.65rem; font-weight: 700;
        border-radius: 999px; padding: 0.15rem 0.55rem; margin-bottom: 0.4rem;
    }
    .divider { border: none; border-top: 1px solid rgba(255,255,255,0.07); margin: 1.5rem 0; }
    footer, #MainMenu, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# [LOAD DATA]
@st.cache_resource
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    movies_dict = pickle.load(open(os.path.join(base, "movies_dict.pkl"), "rb"))
    similarity  = pickle.load(open(os.path.join(base, "similarity.pkl"), "rb"))
    return pd.DataFrame(movies_dict), similarity

movies, similarity = load_data()

TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"

def fetch_poster(movie_id):
    try:
        url  = "https://api.themoviedb.org/3/movie/" + str(movie_id) + "?api_key=" + TMDB_API_KEY
        data = requests.get(url, timeout=5).json()
        path = data.get("poster_path", "")
        if path:
            return "https://image.tmdb.org/t/p/w500" + path
    except Exception:
        pass
    return "https://via.placeholder.com/500x750?text=No+Poster"

def recommend(movie):
    idx       = movies[movies["title"] == movie].index[0]
    distances = similarity[idx]
    top5      = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    titles, posters = [], []
    for i, _ in top5:
        titles.append(movies.iloc[i].title)
        posters.append(fetch_poster(movies.iloc[i]["id"]))
    return titles, posters

# [HERO]
st.markdown("""
<div class="hero">
    <h1>YourMatch🎬</h1>
    <p>Pick a movie you love and we will find five more you will enjoy.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# [SEARCH UI]
left, center, right = st.columns([1, 2, 1])
with center:
    option  = st.selectbox("Pick a movie", movies["title"].values, label_visibility="collapsed")
    clicked = st.button("Find Similar Movies", use_container_width=True)

if clicked:
    with st.spinner("Matching your taste..."):
        t, p = recommend(option)
    st.session_state["rec_titles"]  = t
    st.session_state["rec_posters"] = p

# [RESULTS]
if "rec_titles" in st.session_state:
    st.markdown("<div class='section-label'>Top Picks For You</div>", unsafe_allow_html=True)
    cols = st.columns(5)
    for idx, (col, title, poster) in enumerate(zip(cols, st.session_state["rec_titles"], st.session_state["rec_posters"]), 1):
        with col:
            st.markdown(
                '<div class="movie-card">'
                + '<span class="rank-badge">#' + str(idx) + '</span>'
                + '<img src="' + poster + '" alt="poster">'
                + '<div class="movie-title">' + title + '</div>'
                + '</div>',
                unsafe_allow_html=True
            )
