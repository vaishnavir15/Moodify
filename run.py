import streamlit as st
import requests

# Base URL of your FastAPI backend
BASE_URL = "http://localhost:8000"

# Streamlit app layout
st.title("Music App")

# Navigation options
option = st.sidebar.selectbox(
    "Select Option", ("Get Lyrics", "Store Embeddings", "Create Playlist", "Get Recommendations")
)

# Get Lyrics
if option == "Get Lyrics":
    st.header("Get Song Lyrics")
    artist = st.text_input("Artist Name")
    title = st.text_input("Song Title")
    
    if st.button("Fetch Lyrics"):
        response = requests.get(f"{BASE_URL}/lyrics", params={"artist": artist, "title": title})
        if response.status_code == 200:
            lyrics = response.json().get("lyrics", "No lyrics found.")
            st.text_area("Lyrics", lyrics, height=400)
        else:
            st.error("Could not fetch lyrics.")

# Store Embeddings
elif option == "Store Embeddings":
    st.header("Store Your Music Embeddings")
    limit = st.slider("Number of songs to fetch:", min_value=1, max_value=100, value=50)
    
    if st.button("Store Embeddings"):
        response = requests.get(f"{BASE_URL}/store_embeddings", params={"limit": limit})
        if response.status_code == 200:
            st.success(response.json().get("message"))
        else:
            st.error("Failed to store embeddings.")

# Create Playlist
elif option == "Create Playlist":
    st.header("Create a Playlist")
    query = st.text_input("Search Query for Playlist")
    k = st.slider("Number of songs to fetch:", min_value=1, max_value=20, value=5)
    
    if st.button("Create Playlist"):
        response = requests.post(f"{BASE_URL}/create_playlist", params={"query": query, "k": k})
        if response.status_code == 200:
            st.success(response.json().get("message"))
        else:
            st.error("Failed to create playlist.")

# Get Recommendations
elif option == "Get Recommendations":
    st.header("Get Song Recommendations")
    query = st.text_input("Search Query for Recommendations")
    k = st.slider("Number of recommendations:", min_value=1, max_value=20, value=5)
    
    if st.button("Get Recommendations"):
        response = requests.get(f"{BASE_URL}/get_recommendations", params={"query": query, "k": k})
        if response.status_code == 200:
            recommendations = response.json().get("recommendations", [])
            st.write("Recommendations:")
            for track in recommendations:
                st.write(track.get("name"), "by", ", ".join([artist["name"] for artist in track.get("artists", [])]))
        else:
            st.error("Failed to fetch recommendations.")
