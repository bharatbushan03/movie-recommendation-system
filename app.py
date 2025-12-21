import pandas as pd
import joblib
import streamlit as st
import requests

st.set_page_config(page_title="MovieMate", page_icon="🎬", layout="wide")

# --- OMDb API Configuration ---
# Replace this with the key you get from email
API_KEY = "YOUR_OMDB_API_KEY" 

def fetch_poster(movie_title):
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        
        # OMDb returns 'N/A' if no poster is found
        if data.get('Poster') and data['Poster'] != 'N/A':
            return data['Poster']
        else:
            return "https://via.placeholder.com/300x450?text=No+Poster"
            
    except Exception as e:
        return "https://via.placeholder.com/300x450?text=Error"

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv')
    similarity = joblib.load(open('model.joblib', 'rb'))
    return df, similarity

# Handle missing files gracefully
try:
    df, similarity = load_data()
except:
    st.error("Files not found. Please make sure data.csv and model.joblib are in the folder.")
    st.stop()

# --- Recommendation Logic ---
def get_recommendations(movie):
    try:
        idx = df[df['title'] == movie].index[0]
        distances = similarity[idx]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        
        names = []
        posters = []
        
        for i in movies_list:
            # Fetch title from dataframe
            title = df.iloc[i[0]].title
            names.append(title)
            # Fetch poster from API
            posters.append(fetch_poster(title))
            
        return names, posters
    except IndexError:
        return ["Movie not found"], []

# --- UI Layout ---
# Hide Streamlit Default Elements
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.title('🎬 Movie Recommendation System')

selected_movie = st.selectbox(
    'Type or select a movie to get recommendations:',
    df['title'].values
)

if st.button('Show Recommendation', type="primary"):
    names, posters = get_recommendations(selected_movie)
    
    st.write(f"### Recommendations for **{selected_movie}**:")
    
    # Create 5 columns for the display
    cols = st.columns(5)
    
    for i in range(len(names)):
        with cols[i]:
            st.image(posters[i], use_container_width=True)
            st.caption(names[i])