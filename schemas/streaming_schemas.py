from typing import Optional

from pydantic import BaseModel


class TrackOut(BaseModel):
    id: int
    title: str
    artist: Optional[str] = None

    file_path: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class UserOut(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    age: Optional[int] = None

    model_config = {
        "from_attributes": True
    }


class PlaylistOut(BaseModel):
    id: int
    name: str

    owner_id: int

    model_config = {
        "from_attributes": True
    }
