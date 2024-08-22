import os
import logging
from fastapi import FastAPI, HTTPException, Request, Query  # Corrected import
from fastapi.responses import RedirectResponse, JSONResponse
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from spotipy.exceptions import SpotifyException
from langchain_core.documents import Document
from langchain_chroma import Chroma
from FlagEmbedding import BGEM3FlagModel
from uuid import uuid4
import nest_asyncio
import uvicorn
import asyncio
import lyricsgenius

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Spotify OAuth configuration
sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri="http://localhost:8235/callback",
    scope="user-top-read user-library-read playlist-read-private playlist-modify-public playlist-modify-private"
)


# Initialize Genius API
genius = lyricsgenius.Genius(os.getenv("GENIUS_API_TOKEN"))

# Initialize the BGEM3FlagModel for generating real embeddings
model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)

def get_spotify_client():
    token_info = sp_oauth.get_cached_token()

    if not token_info:
        raise HTTPException(status_code=307, detail="Redirecting to Spotify authorization", headers={"Location": "/login"})

    access_token = token_info['access_token']
    sp = spotipy.Spotify(auth=access_token)
    return sp

from langchain_community.embeddings import HuggingFaceBgeEmbeddings 

# Initialize the BGEM3FlagModel for generating real embeddings
model_name = "BAAI/bge-m3"

embedding_function = HuggingFaceBgeEmbeddings(model_name=model_name)

def get_text_collection(user_id: str):
    # Create a unique collection name for textual data based on user ID
    collection_name = f"{user_id}_text_collection"
    
    # Initialize Chroma vector store for text data with the embedding function
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embedding_function,
        persist_directory="./chroma_langchain_db"
    )
    
    return vector_store

  


def get_audio_collection(user_id: str):
    # Create a unique collection name for audio data based on user ID
    collection_name = f"{user_id}_audio_collection"
    
    # Initialize Chroma vector store for audio data (no embeddings needed)
    vector_store = Chroma(
        collection_name=collection_name,
         embedding_function=embedding_function,
        persist_directory="./chroma_langchain_db"
    )
    
    return vector_store

def get_audio_features_and_analysis(sp, track_id):
    audio_features = sp.audio_features([track_id])[0]  # Fetching audio features
    audio_analysis = sp.audio_analysis(track_id)       # Fetching audio analysis
    return {
        "audio_features": audio_features,
        "audio_analysis": audio_analysis
    }


def filter_none_metadata(metadata):
    """
    Recursively filters out None values from the metadata dictionary.
    """
    if isinstance(metadata, dict):
        return {k: filter_none_metadata(v) for k, v in metadata.items() if v is not None}
    return metadata


@app.get("/lyrics")
async def lyrics(artist: str, title: str):
    try:
        song = genius.search_song(title, artist)
        if song:
            return {"lyrics": song.lyrics}
        else:
            raise HTTPException(status_code=404, detail="Lyrics not found")
    except HTTPException as e:
        raise e

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Spotify integration with FastAPI"}

@app.get("/login")
async def login():
    auth_url = sp_oauth.get_authorize_url()
    logger.info(f"Redirecting to Spotify's authorization URL: {auth_url}")
    return RedirectResponse(auth_url)

@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get('code')
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    token_info = sp_oauth.get_access_token(code)

    if token_info:
        logger.info("Access token obtained successfully!")
        return RedirectResponse(url="/")
    else:
        raise HTTPException(status_code=401, detail="Could not authenticate with Spotify")

import json

def convert_lists_to_strings(metadata):
    """
    Convert lists in the metadata to JSON strings before storing them in ChromaDB.
    Convert None values to empty strings.
    """
    new_metadata = {}
    for key, value in metadata.items():
        if value is None:
            new_metadata[key] = ""  # Convert None to empty string
        elif isinstance(value, list):
            new_metadata[key] = json.dumps(value)
        elif isinstance(value, dict):
            new_metadata[key] = convert_lists_to_strings(value)  # Recursively handle nested dictionaries
        else:
            new_metadata[key] = value
    return new_metadata


def convert_strings_to_lists(metadata):
    """
    Convert JSON strings in the metadata back to lists after retrieving them from ChromaDB.
    """
    new_metadata = {}
    for key, value in metadata.items():
        try:
            # Try to convert the string back to a list
            new_metadata[key] = json.loads(value) if isinstance(value, str) else value
        except json.JSONDecodeError:
            # If it's not a valid JSON string, keep the value as is
            new_metadata[key] = value
    return new_metadata


@app.get("/search")
async def search(query: str, k: int = Query(default=5, description="Number of results to fetch")):
    try:
        sp = get_spotify_client()
        user_id = sp.current_user()['id']  # Get the current user's ID

        # Get text collection for this user
        text_store = get_text_collection(user_id)
        audio_store = get_audio_collection(user_id)

        # Perform similarity search in text collection
        text_results = text_store.similarity_search(query, k=k)

        # Retrieve corresponding audio features and analysis based on track IDs
        audio_results = []
        for text_result in text_results:
            track_id = text_result.metadata['track_id']
            audio_result = audio_store.get([track_id])  # Retrieve audio data by track ID

            # Log the audio_result for debugging purposes
            logger.info(f"Audio result for track_id {track_id}: {audio_result}")

            # Check if audio_result exists and is a non-empty list
            if audio_result and isinstance(audio_result, list) and len(audio_result) > 0:
                audio_metadata = audio_result[0].metadata
                if audio_metadata:
                    # Convert JSON strings back to lists in audio metadata
                    audio_metadata = convert_strings_to_lists(audio_metadata)
                audio_results.append(audio_metadata)
            else:
                logger.warning(f"No valid audio data found for track_id {track_id}.")
                audio_results.append(None)

        # Combine text and audio data for final output
        combined_results = []
        for text_result, audio_result in zip(text_results, audio_results):
            combined_results.append({
                "text": text_result.page_content,
                "metadata": text_result.metadata,
                "audio": audio_result
            })
            # print(f"---------------------------Combined Result: {combined_results}")
        
        # response_text = format_response(combined_results)
        # return {"results": response_text}
        return {"results": combined_results}
    
    except HTTPException as e:
        if e.status_code == 307:
            return RedirectResponse(url="/login")
        raise e
    except SpotifyException as e:
        if e.http_status == 429:
            return JSONResponse(status_code=429, content={"message": "Rate limit exceeded, please try again later."})
        else:
            return JSONResponse(status_code=500, content={"message": "An error occurred during the search process."})





@app.get("/store_embeddings")
async def store_embeddings(limit: int = Query(default=50, description="Number of liked songs to fetch")):
    try:
        sp = get_spotify_client()
                
                # Get the current user's ID as early as possible
        user_id = sp.current_user()['id']  # Get the current user's ID

                # Get the text collection
        text_store = get_text_collection(user_id)
                        
                # Get the current number of songs in the collection
        curr_number_of_songs = text_store._collection.count()
        
        # Determine the offset for the Spotify API request
        if curr_number_of_songs >= limit:
            offset = curr_number_of_songs + limit
        else:
            offset = 0

        liked_songs = sp.current_user_saved_tracks(limit=limit, offset=offset)
        
        user_id = sp.current_user()['id']  # Get the current user's ID

        # Get or create vector stores for text and audio data
        text_store = get_text_collection(user_id)
        audio_store = get_audio_collection(user_id)

        text_documents = []
        audio_documents = []
        ids = []

        for item in liked_songs['items']:
            track = item['track']
            track_id = track['id']
            track_info = {
                "id": track_id,
                "name": track['name'],
                "album": track['album']['name'],
                "artists": [artist['name'] for artist in track['artists']],
                "url": track['external_urls']['spotify']
            }

            # Convert lists to JSON strings in track_info
            track_info = convert_lists_to_strings(track_info)

            # Handle potential None values in track_info
            track_info = filter_none_metadata(track_info)

            song_lyrics = ""
            artist_name = json.loads(track_info["artists"])[0]  # Get the first artist's name
            try: 
                song = genius.search_song(track_info["name"], artist_name)
            except HTTPException as e:
                e.__traceback__()



            # if song:
            #     song_lyrics = song.lyrics or ""

            # Create the document for the text collection
            text_doc = Document(
                page_content=f"{track_info['name']} by {json.loads(track_info['artists'])} from {track_info['album']}\nLyrics: {song_lyrics}",
                metadata={"url": track_info["url"], "track_id": track_id},
            )
            text_documents.append(text_doc)
            ids.append(track_id)  # Use track ID as the document ID for both collections

            # Get audio features and analysis
            audio_data = sp.audio_features([track_id])[0]  # Fetching audio features for the track
            
            # Convert lists to JSON strings in audio_data
            audio_data = convert_lists_to_strings(audio_data)

            # Handle potential None values in audio_data
            audio_data = filter_none_metadata(audio_data)

            # Combine the track_info and audio features into a single metadata dictionary
            combined_metadata = {**track_info, **audio_data, "lyrics": song_lyrics}

            # Handle potential None values in combined_metadata
            combined_metadata = filter_none_metadata(combined_metadata)

            # Create the document for the audio collection
            audio_doc = Document(
                page_content="Audio features and analysis data",
                metadata=combined_metadata,
            )
            audio_documents.append(audio_doc)

        # Store the documents in the respective vector stores
        text_store.add_documents(documents=text_documents, ids=ids)
        audio_store.add_documents(documents=audio_documents, ids=ids)
        
        logger.info(f"Number of songs embedded for user {user_id}: {len(text_documents)}")

        return {"message": f"Successfully embedded {len(text_documents)} songs for user {user_id}"}
    except HTTPException as e:
        if e.status_code == 307:
            return RedirectResponse(url="/login")
        raise e
    except SpotifyException as e:
        if e.http_status == 429:
            return JSONResponse(status_code=429, content={"message": "Rate limit exceeded, please try again later."})
        else:
            return JSONResponse(status_code=500, content={"message": "An error occurred while embedding songs."})

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.post("/create_playlist")
async def create_playlist(query: str, k: int = Query(default=5, description="Number of results to fetch")):
    try:
        sp = get_spotify_client()
        user_id = sp.current_user()['id']  # Get the current user's ID

        # Create a new playlist with the query as the name
        playlist_name = query
        playlist_description = f"Playlist created based on the search query: {query}"
        new_playlist = sp.user_playlist_create(user_id, name=playlist_name, public=False, description=playlist_description)
        playlist_id = new_playlist['id']
        
        logger.info(f"Created new playlist: {playlist_name} with ID: {playlist_id}")

        # Search for songs and retrieve the results
        search_results = await search(query, k)
        recommendations = await get_recommendations(query, k)

        # Extract URIs of tracks from the search results
        search_uris = [
            f"spotify:track:{result['metadata']['track_id']}"
            for result in search_results['results'] if 'track_id' in result['metadata']
        ]

        # Extract URIs of tracks from the recommendations
        recommendation_uris = [
            f"spotify:track:{track['id']}"
            for track in recommendations['recommendations']
        ]

        # Combine URIs from both search and recommendations
        song_uris = search_uris + recommendation_uris


        # Add songs to the playlist
        if song_uris:
            sp.playlist_add_items(playlist_id, song_uris)
            logger.info(f"Added {len(song_uris)} songs to the playlist: {playlist_name}")
        logger.info(f"Created new playlist: {playlist_name} with ID: {playlist_id}")
        return {"message": f"Playlist '{playlist_name}' created and {len(song_uris)} songs added."}
    
    except HTTPException as e:
        if e.status_code == 307:
            return RedirectResponse(url="/login")
        raise e
    except SpotifyException as e:
        if e.http_status == 429:
            return JSONResponse(status_code=429, content={"message": "Rate limit exceeded, please try again later."})
        else:
            return JSONResponse(status_code=500, content={"message": "An error occurred while creating the playlist."})

@app.get("/get_recommendations")
async def get_recommendations(query: str, k: int = Query(default=5, description="Number of search results to fetch")):
    try:
        sp = get_spotify_client()
        user_id = sp.current_user()['id']  # Get the current user's ID
 
        # Step 1: Perform the search and retrieve results
        search_results = await search(query, k)
        seed_tracks = []
        seed_artists = []
        seed_genres = []
 
        for result in search_results['results']:
            metadata = result['metadata']
            if metadata and 'track_id' in metadata:
                seed_tracks.append(metadata['track_id'])
            if metadata and 'artists' in metadata:
                seed_artists.extend(metadata['artists'])  # Assuming artists' IDs are stored in metadata
 
        # Use only up to 5 seeds as required by Spotify API
        seed_tracks = seed_tracks[:5]
        seed_artists = seed_artists[:5]
 
        # Step 2: Get recommendations based on seeds
        recommendations = sp.recommendations(
            seed_tracks=seed_tracks,
            seed_artists=seed_artists,
            seed_genres=seed_genres,
            limit=k,  # Adjust the limit as needed
            market="US"  # Adjust the market as needed
        )
 
        # Step 3: Filter out tracks already liked by the user
        liked_songs = sp.current_user_saved_tracks(limit=50)
        liked_track_ids = {item['track']['id'] for item in liked_songs['items']}
 
        filtered_recommendations = [track for track in recommendations['tracks'] if track['id'] not in liked_track_ids]

        final_recommendations = filtered_recommendations[:k]
        return {"recommendations": final_recommendations}
        
 
    except HTTPException as e:
        if e.status_code == 307:
            return RedirectResponse(url="/login")
        raise e
    except SpotifyException as e:
        if e.http_status == 429:
            return JSONResponse(status_code=429, content={"message": "Rate limit exceeded, please try again later."})
        else:
            return JSONResponse(status_code=500, content={"message": "An error occurred while fetching recommendations."})


import nest_asyncio
import uvicorn
import subprocess
from backend import FastAPI
if __name__ == "__main__":
# Apply the nest_asyncio patch to allow running FastAPI in a Jupyter notebook
    nest_asyncio.apply()


    # Function to run the FastAPI server
    def run_fastapi():
        uvicorn.run(app, host="127.0.0.1", port=8235)

    # Run FastAPI server directly
    run_fastapi()

    # Start Streamlit app in a subprocess
    subprocess.run(["streamlit", "run", "run.py"])
