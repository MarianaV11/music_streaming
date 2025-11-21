from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db
from models.streaming_model import Playlist, Track, User
from schemas.streaming_schemas import PlaylistOut, TrackOut, UserOut

router = APIRouter()


@router.get("/users", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db)):
    """
    List of all users.
    """
    return db.query(User).all()


@router.get("/tracks", response_model=List[TrackOut])
def list_tracks(db: Session = Depends(get_db)):
    """
    List all the tracks available in db.
    """
    return db.query(Track).all()


@router.get("/users/{user_id}/playlists", response_model=List[PlaylistOut])
def playlists_of_user(user_id: int, db: Session = Depends(get_db)):
    """
    List all the playlists of a specific user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user.playlists


@router.get("/playlists/{playlist_id}/tracks", response_model=List[TrackOut])
def tracks_of_playlist(playlist_id: int, db: Session = Depends(get_db)):
    """
    List all the musics(tracks) in a playlist.
    """
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist não encontrada")
    return playlist.tracks


@router.get("/tracks/{track_id}/playlists", response_model=List[PlaylistOut])
def playlists_containing_track(track_id: int, db: Session = Depends(get_db)):
    """
    Return all the playlists that contain a specific track.
    """
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Música não encontrada")
    return track.playlists


@router.get("/stream/{track_id}")
async def stream_track(track_id: int, request: Request, db: Session = Depends(get_db)):
    """
    Return the music by it's id.
    """
    track = db.query(Track).filter(Track.id == track_id).first()

    if not track:
        raise HTTPException(status_code=404, detail="Música não encontrada")

    if not track.file_path:
        raise HTTPException(status_code=404, detail="Arquivo de áudio não disponível")

    path = Path(track.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    file_size = path.stat().st_size
    range_header = request.headers.get("range")

    if range_header:
        # Ex: bytes=1000-5000
        byte1, byte2 = range_header.replace("bytes=", "").split("-")
        start = int(byte1)
        end = int(byte2) if byte2 else file_size - 1
    else:
        start = 0
        end = file_size - 1

    def iterfile():
        with open(path, "rb") as f:
            f.seek(start)
            remaining = end - start + 1
            chunk_size = 1024 * 1024  # 1 MB
            while remaining > 0:
                chunk = f.read(min(chunk_size, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk

    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(end - start + 1),
        "Content-Type": "audio/mpeg",
    }

    return StreamingResponse(iterfile(), status_code=206, headers=headers)
