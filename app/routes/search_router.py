import os
import logging
from backend import FastAPI, HTTPException, Request, Query
from fastapi.responses import RedirectResponse, JSONResponse
from spotipy.exceptions import SpotifyException
from app.managers.spotify_manager import SpotifyManager
from app.utils.logging import get_logger


router = FastAPI()
sp = SpotifyManager()
auth_manager = sp.auth_manager 
logger = get_logger(__name__)

@router.get("/search")
async def search(query: str, k: int = Query(default=5, description="Number of results to fetch")):
    try:
        
        client = sp.get_spotify_client()
        user_id = client.current_user()['id']


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
