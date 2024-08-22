from backend import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from app.managers.spotify_manager import SpotifyManager
import logging

router = APIRouter()
sp = SpotifyManager()
auth_manager = sp.sp_oauth
logger = logging.getLogger(__name__)

@router.get("/login")
async def login():
    auth_url = auth_manager.get_auth_url()
    logger.info(f"Redirecting to Spotify's authorization URL: {auth_url}")
    return RedirectResponse(auth_url)

@router.get("/callback")
async def callback(request: Request):
    code = request.query_params.get('code')
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    token_info = auth_manager.get_access_token(code)
    if token_info:
        logger.info("Access token obtained successfully!")
        return RedirectResponse(url="/")
    else:
        raise HTTPException(status_code=401, detail="Could not authenticate with Spotify")
