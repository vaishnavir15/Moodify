import streamlit as st
import requests

"""
This Streamlit app serves as a frontend for interacting with a FastAPI backend.
It allows users to perform various music-related tasks, such as storing music embeddings, 
creating playlists, and getting song recommendations by making HTTP requests to the FastAPI endpoints.

Features:
1. Store Embeddings: Fetches and stores song embeddings from the user's Spotify account.
2. Create Playlist: Creates a playlist based on a search query.
3. Get Recommendations: Fetches song recommendations based on a search query.

Dependencies:
- Streamlit: For building the frontend interface.
- Requests: For sending HTTP requests to the FastAPI backend.

Make sure to adjust the `BASE_URL` to match the actual URL of your FastAPI backend.
"""

# Base URL of your FastAPI backend
BASE_URL = "http://127.0.0.1:8235"

# Streamlit app layout
st.title("Music App")

# Navigation options
option = st.sidebar.selectbox(
    "Select Option", ("Get Lyrics", "Store Embeddings", "Create Playlist", "Get Recommendations")
)

# Store Embeddings
if option == "Store Embeddings":
    """
    Section for storing music embeddings.
    
    Allows the user to select the number of songs to fetch from their Spotify account using a slider.
    Upon clicking the "Store Embeddings" button, a GET request is sent to the `/store_embeddings` endpoint 
    of the FastAPI backend. The response from the backend is displayed as a success or error message.
    """
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
    """
    Section for creating a playlist.
    
    Allows the user to input a search query and specify the number of songs to include in the playlist.
    Upon clicking the "Create Playlist" button, a POST request is sent to the `/create_playlist` endpoint 
    of the FastAPI backend. The response from the backend is displayed as a success or error message.
    """
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
    """
    Section for getting song recommendations.
    
    Allows the user to input a search query and specify the number of recommendations to fetch.
    Upon clicking the "Get Recommendations" button, a GET request is sent to the `/get_recommendations` endpoint 
    of the FastAPI backend. The recommended tracks are displayed in the Streamlit app.
    """
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
