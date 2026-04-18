import os
import requests
import streamlit as st

st.set_page_config(page_title="MovieMate", page_icon="🎬", layout="wide")

API_BASE_URL = os.getenv("API_BASE_URL", "https://movie-recommendation-system-jroq.onrender.com")
OMDB_API_KEY = os.getenv("OMDB_API_KEY", "YOUR_OMDB_API_KEY")
PLACEHOLDER_POSTER = "https://via.placeholder.com/300x450?text=No+Poster"

def fetch_poster(movie_title: str) -> str:
    if OMDB_API_KEY == "YOUR_OMDB_API_KEY":
        return PLACEHOLDER_POSTER
    try:
        response = requests.get(
            "https://www.omdbapi.com/",
            params={"t": movie_title, "apikey": OMDB_API_KEY},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        poster = data.get("Poster")
        if poster and poster != "N/A":
            return poster
    
    except requests.RequestException:
        pass
    return PLACEHOLDER_POSTER

@st.cache_data(ttl=300)
def fetch_movie_titles() -> list[str]:
    response = requests.get(f'{API_BASE_URL}/movies', timeout=10)
    response.raise_for_status()
    return response.json()

def fetch_recommendations(title: str, top_k: int = 5) -> list[str]:
    response = requests.post(
        f"{API_BASE_URL}/recommend",
        json={"title": title, "top_k": top_k},
        timeout=15,
    )
    if response.status_code == 404:
        return []
    response.raise_for_status()
    return response.json()["recommendations"]

st.title("🎬 Movie Recommendation System")

try:
    movie_titles = fetch_movie_titles()
except requests.RequestException as e:
    st.error(f'Could not reach API at {API_BASE_URL}, Error: {e}')
    st.stop()

selected_movie = st.selectbox("Select a movie to get recommendations:", movie_titles)

if st.button("Show Recommendation", type = "primary"):
    recommendations = fetch_recommendations(selected_movie, top_k=5)
    if not recommendations:
        st.warning("Movie not found in the backend database")
    else:
        st.write(f"### Recommendations for {selected_movie}")
        cols = st.columns(5)
        for idx, title in enumerate(recommendations):
            with cols[idx]:
                st.image(fetch_poster(title), use_container_width=True)
                st.caption(title)