from fastapi import APIRouter, Query, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from managers.spotify_manager import SpotifyManager
from embedding_manager import EmbeddingManager
from utils import filter_none_metadata, convert_lists_to_strings, convert_strings_to_lists
from spotipy.exceptions import SpotifyException
from langchain_core.documents import Document
import logging

# Initialize logging
logger = logging.getLogger(__name__)

# Initialize routers
router = APIRouter()

# Initialize managers
auth_manager = SpotifyAuthManager()
spotify_manager = SpotifyManager(auth_manager)
embedding_manager = EmbeddingManager(model_name="BAAI/bge-m3")

@router.get("/lyrics")
async def lyrics(artist: str, title: str):
    try:
        song = genius.search_song(title, artist)
        if song:
            return {"lyrics": song.lyrics}
        else:
            raise HTTPException(status_code=404, detail="Lyrics not found")
    except HTTPException as e:
        raise e


@router.get("/store_embeddings")
async def store_embeddings(limit: int = Query(default=50)):
    try:
        sp = auth_manager.get_spotify_client()
        user_id = sp.current_user()['id']
        text_store = embedding_manager.get_text_collection(user_id)
        audio_store = embedding_manager.get_audio_collection(user_id)
        liked_songs = sp.current_user_saved_tracks(limit=limit)

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

            track_info = convert_lists_to_strings(track_info)
            track_info = filter_none_metadata(track_info)
            song_lyrics = ""

            text_doc = Document(
                page_content=f"{track_info['name']} by {json.loads(track_info['artists'])} from {track_info['album']}\nLyrics: {song_lyrics}",
                metadata={"url": track_info["url"], "track_id": track_id},
            )
            text_documents.append(text_doc)
            ids.append(track_id)

            audio_data = sp.audio_features([track_id])[0]
            audio_data = convert_lists_to_strings(audio_data)
            audio_data = filter_none_metadata(audio_data)
            combined_metadata = {**track_info, **audio_data, "lyrics": song_lyrics}

            combined_metadata = filter_none_metadata(combined_metadata)

            audio_doc = Document(
                page_content="Audio features and analysis data",
                metadata=combined_metadata,
            )
            audio_documents.append(audio_doc)

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

@router.get("/search")
async def search(query: str, k: int = Query(default=5)):
    try:
        sp = auth_manager.get_spotify_client()
        user_id = sp.current_user()['id']
        text_store = embedding_manager.get_text_collection(user_id)
        audio_store = embedding_manager.get_audio_collection(user_id)
        text_results = text_store.similarity_search(query, k=k)
        audio_results = []

        for text_result in text_results:
            track_id = text_result.metadata['track_id']
            audio_result = audio_store.get([track_id])
            if audio_result and isinstance(audio_result, list) and len(audio_result) > 0:
                audio_metadata = audio_result[0].metadata
                if audio_metadata:
                    audio_metadata = convert_strings_to_lists(audio_metadata)
                audio_results.append(audio_metadata)
            else:
                audio_results.append(None)

        combined_results = []
        for text_result, audio_result in zip(text_results, audio_results):
            combined_results.append({
                "text": text_result.page_content,
                "metadata": text_result.metadata,
                "audio": audio_result
            })
        
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

