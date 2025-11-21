from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base, playlist_tracks


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)

    playlists = relationship("Playlist", back_populates="owner")


class Track(Base):
    __tablename__ = "tracks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=True)

    file_path = Column(Text, nullable=True)

    playlists = relationship(
        "Playlist", secondary=playlist_tracks, back_populates="tracks"
    )


class Playlist(Base):
    __tablename__ = "playlists"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="playlists")
    tracks = relationship(
        "Track", secondary=playlist_tracks, back_populates="playlists"
    )
