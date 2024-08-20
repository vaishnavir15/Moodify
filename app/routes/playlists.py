
import os
import logging
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import RedirectResponse, JSONResponse
from spotipy.exceptions import SpotifyException

from app.managers.spotify_manager import SpotifyManager
from app.routes.recommendations_router import search, get_recommendations



router = FastAPI()
sp = SpotifyManager()
auth_manager = sp.auth_manager




@router.post("/create_playlist")
async def create_playlist(query: str, k: int = Query(default=5)):
    try:
        sp = auth_manager.get_spotify_client()
        user_id = sp.current_user()['id']
        playlist_name = query
        playlist_description = f"Playlist created based on the search query: {query}"
        new_playlist = sp.user_playlist_create(user_id, name=playlist_name, public=False, description=playlist_description)
        playlist_id = new_playlist['id']

        search_results = await search(query, k)
        recommendations = await get_recommendations(query, k)

        search_uris = [
            f"spotify:track:{result['metadata']['track_id']}"
            for result in search_results['results'] if 'track_id' in result['metadata']
        ]

        recommendation_uris = [
            f"spotify:track:{track['id']}"
            for track in recommendations['recommendations']
        ]

        song_uris = search_uris + recommendation_uris

        if song_uris:
            sp.playlist_add_items(playlist_id, song_uris)
            logger.info(f"Added {len(song_uris)} songs to the playlist: {playlist_name}")
        
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
