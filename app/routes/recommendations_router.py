import os
import logging
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import RedirectResponse, JSONResponse
from spotipy.exceptions import SpotifyException
from app.managers.spotify_manager import SpotifyManager



router = FastAPI()
sp = SpotifyManager()
auth_manager = sp.auth_manager 



@router.get("/get_recommendations")
async def get_recommendations(query: str, k: int = Query(default=5)):
    try:
        sp = auth_manager.get_spotify_client()
        user_id = sp.current_user()['id']
        search_results = await search(query, k)
        seed_tracks = []
        seed_artists = []
        seed_genres = []

        for result in search_results['results']:
            metadata = result['metadata']
            if metadata and 'track_id' in metadata:
                seed_tracks.append(metadata['track_id'])
            if metadata and 'artists' in metadata:
                seed_artists.extend(metadata['artists'])

        seed_tracks = seed_tracks[:5]
        seed_artists = seed_artists[:5]

        recommendations = sp.recommendations(
            seed_tracks=seed_tracks,
            seed_artists=seed_artists,
            seed_genres=seed_genres,
            limit=k,
            market="US"
        )

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
