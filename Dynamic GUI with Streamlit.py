import streamlit as st
import pickle
import pandas as pd
import requests
import random
import time

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="CineMatrix | AI Recommender",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (NEON & ANIMATIONS) ---
st.markdown("""
    <style>
    /* Dark Cyberpunk Background */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 50%, #1a1a2e 0%, #000000 100%);
        color: #e0e0e0;
    }

    /* Glowing Title */
    .neon-text {
        font-family: 'Courier New', sans-serif;
        font-size: 1000px;
        font-weight: bold;
        text-align: center;
        color: #fff;
        text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff, 0 0 40px #00d4ff;
        animation: pulse 2s infinite;
        margin-bottom: 30px;
    }

    @keyframes pulse {
        0% { text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff; }
        50% { text-shadow: 0 0 20px #ff00de, 0 0 40px #ff00de; }
        100% { text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff; }
    }

    /* Glassmorphism Cards */
    .movie-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 10px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        text-align: center;
    }
    
    .movie-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.6);
        border: 1px solid #00d4ff;
    }

    /* Match Score Badge */
    .match-score {
        background: linear-gradient(90deg, #ff00de, #00d4ff);
        color: white;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        margin-top: 10px;
        display: inline-block;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #333;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_resource
def load_data():
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity

try:
    movies, similarity = load_data()
except FileNotFoundError:
    st.error("Error: Pickle files not found. Please run your Jupyter Notebook to generate 'movie_dict.pkl' and 'similarity.pkl'.")
    st.stop()

# --- FUNCTIONS ---
def fetch_poster(movie_id):
    # API KEY ADDED HERE
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=2f8d51659817f1f010ec4cdce7af1633&language=en-US"
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            data = response.json()
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    except:
        pass
    return "https://via.placeholder.com/500x750?text=No+Poster"

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    recommendations = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        score = round(i[1] * 100) # Convert similarity score to percentage
        recommendations.append({
            "title": movies.iloc[i[0]].title,
            "poster": fetch_poster(movie_id),
            "score": score
        })
    return recommendations

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Controls")
    
    # Search Box
    selected_movie = st.selectbox(
        "🔍 Search Movie",
        movies['title'].values
    )
    
    # Main Button
    if st.button('🚀 Recommend Movies', type="primary"):
        trigger_recommendation = True
    else:
        trigger_recommendation = False
        
    st.markdown("---")
    
    # Surprise Me Feature
    if st.button('🎲 Surprise Me!'):
        selected_movie = random.choice(movies['title'].values)
        trigger_recommendation = True
        st.toast(f"Surprise! Selected: {selected_movie}")

# --- MAIN LAYOUT ---
st.markdown('<p class="neon-text">CINE MATRIX</p>', unsafe_allow_html=True)

if trigger_recommendation:
    with st.spinner('Analyzing patterns...'):
        time.sleep(1) # Artificial delay for "processing" effect
        results = recommend(selected_movie)
    
    st.balloons() # Dynamic confetti effect
    
    st.markdown(f"### 🤖 Based on **'{selected_movie}'**, AI suggests:")
    
    # Dynamic Columns
    cols = st.columns(5)
    
    for idx, col in enumerate(cols):
        movie = results[idx]
        with col:
            # Using HTML to create the card effect
            st.markdown(f"""
                <div class="movie-card">
                    <img src="{movie['poster']}" style="width:100%; border-radius:10px;">
                    <h4 style="margin-top:10px; font-size:16px;">{movie['title']}</h4>
                    <span class="match-score">{movie['score']}% Match</span>
                </div>
            """, unsafe_allow_html=True)

else:
    # Idle State Display
    st.markdown("""
        <div style="text-align: center; margin-top: 50px; color: #888;">
            <h2>👈 Select a movie to start the engine</h2>
            <p>Explore thousands of movies using our AI-driven content filtering system.</p>
        </div>
    """, unsafe_allow_html=True)


