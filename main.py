import pickle
import streamlit as st
import requests
from googleapiclient.discovery import build

# OMDB API Key
OMDB_API_KEY = "ef93f755"
# YouTube Data API Key
YOUTUBE_API_KEY = "AIzaSyCNy4FD6RVCmrQhRUaBzQR3NW_h9WhYnBE"

# Function to fetch movie poster from OMDb API
@st.cache_data
def fetch_poster(movie_name):
    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if "Poster" in data and data["Poster"] != "N/A":
        return data["Poster"]
    return None  # Return None if poster is not found

# Function to fetch trailer from YouTube Data API
def get_trailer(query):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    search_response = youtube.search().list(
        q=query + " official trailer",
        part="snippet",
        maxResults=1,
        type="video"
    ).execute()
    
    if search_response["items"]:
        video_id = search_response["items"][0]["id"]["videoId"]
        return f"https://www.youtube.com/watch?v={video_id}"
    return None

# Function to get movie recommendations
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_trailers = []
    
    for i in distances[1:6]:  # Get top 5 recommended movies
        movie_name = movies.iloc[i[0]].title
        recommended_movie_names.append(movie_name)
        recommended_movie_posters.append(fetch_poster(movie_name))  # Fetch poster from OMDb API
        recommended_movie_trailers.append(get_trailer(movie_name))  # Fetch trailer from YouTube API

    return recommended_movie_names, recommended_movie_posters, recommended_movie_trailers

# Streamlit App UI
st.title("🎬 Movie Recommender System")
st.write("Select a movie to get recommendations  🔎!")

# Load movie data and similarity matrix
movies = pickle.load(open('/Users/anishsmac/Desktop/Movie/movie_list.pkl', 'rb'))
similarity = pickle.load(open('/Users/anishsmac/Desktop/Movie/similarity.pkl', 'rb'))

# Movie Selection Dropdown
movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie:", movie_list)

# Show Recommendations
if st.button('Show Recommendations'):
    recommended_movie_names, recommended_movie_posters, recommended_movie_trailers = recommend(selected_movie)

    # Display recommendations in a horizontal scroll layout
    st.write("### Recommended Movies:")
    for i in range(0, len(recommended_movie_names), 5):  # Ensure it groups in sets of 5
        cols = st.columns(5)  # Creates 5 equal columns for each group
        
        for j, col in enumerate(cols):
            if i + j < len(recommended_movie_names):  # Check to avoid index out of range
                with col:
                    st.write(f"**{recommended_movie_names[i + j]}**")  # Show movie name
                    poster = recommended_movie_posters[i + j]
                    if poster:
                        st.image(poster, use_column_width=True, width=200)  # Set a fixed width
                    else:
                        st.error("Poster not found")  # Handle missing posters
                    
                    # Show trailer link
                    trailer_url = recommended_movie_trailers[i + j]
                    if trailer_url:
                        st.markdown(f"[🎥 Watch Trailer]({trailer_url})")
                    else:
                        st.warning("Trailer not found.")
