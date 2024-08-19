import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from fastapi import HTTPException


class SpotifyManager():
    def __init__(self):
        self.client_id = os.getenv('SPOTIPY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
        self.redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')
        self.scope = "user-top-read user-library-read playlist-read-private playlist-modify-public playlist-modify-private"
        self.sp_oauth = SpotifyOAuth(
                            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                            redirect_uri="http://localhost:8235/callback",
                            scope="user-top-read user-library-read playlist-read-private playlist-modify-public playlist-modify-private"
                        )

        self.sp = spotipy.Spotify(auth_manager=self.sp_oauth)
        self.username = self.sp.me()['id']
        self.token = self.sp_oauth.get_access_token()


        
    def get_spotify_client(self):
        token_info = self.sp_oauth.get_cached_token()

        if not token_info:
                raise HTTPException(status_code=307, detail="Redirecting to Spotify authorization", headers={"Location": "/login"})

        access_token = token_info['access_token']
        self.sp = spotipy.Spotify(auth=access_token)
        return self.sp
    
    def get_user_playlists(self):
        sp = self.get_spotify_client()
        playlists = sp.current_user_playlists()
        return playlists
    
    def get_playlist_tracks(self, playlist_id):
        sp = self.get_spotify_client()
        tracks = sp.playlist_tracks(playlist_id)
        return tracks
    
    def get_user_top_tracks(self):
        sp = self.get_spotify_client()
        top_tracks = sp.current_user_top_tracks()
        return top_tracks
    
    def get_user_saved_tracks(self):
        # neew work here 
        sp = self.get_spotify_client()
        saved_tracks = sp.current_user_saved_tracks()
        return saved_tracks
    
    def create_playlist(self, playlist_name):
        sp = self.get_spotify_client()
        playlist = sp.user_playlist_create(self.username, playlist_name)
        # tag the playlist created on behalf of the user
        sp.playlist_change_details(playlist['id'], description="moodify") 
        return playlist
    
    def add_tracks_to_playlist(self, playlist_id, track_uris):
        # cannot overwrite any users exciting playlist
        sp = self.get_spotify_client()
        # if playlist description is not moodify, then it is not created by moodify
        playlist = sp.playlist(playlist_id)
        if playlist['description'] != "moodify":
            raise HTTPException(status_code=403, detail="Cannot modify existing playlists")
        else:
            sp.playlist_add_items(playlist_id, track_uris)

    def get_access_token(self):
        token_info = self.sp_oauth.get_cached_token()

        if not token_info:
            raise HTTPException(status_code=307, detail="Redirecting to Spotify authorization", headers={"Location": "/login"})

        access_token = token_info['access_token']
        sp = spotipy.Spotify(auth=access_token)
        return sp
        
        

        