from typing import Optional

from pydantic import BaseModel


class TrackOut(BaseModel):
    id: int
    title: str
    artist: Optional[str] = None
    album: Optional[str] = None
    duration: Optional[int] = None
    file_path: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class UserOut(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class PlaylistOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    owner_id: int

    model_config = {
        "from_attributes": True
    }
