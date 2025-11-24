import graphene
from graphene import ObjectType, Int, String, Field, List
from database import SessionLocal
from models.streaming_model import User, Track, Playlist


# ====================================
#        TIPOS GRAPHQL (Schemas)
# ====================================

class TrackType(ObjectType):
    id = Int()
    title = String()
    artist = String()
    file_path = String()
    duration = Int()


class PlaylistType(ObjectType):
    id = Int()
    name = String()

    # dono da playlist
    owner = Field(lambda: UserType)

    # músicas da playlist
    tracks = List(lambda: TrackType)


class UserType(ObjectType):
    id = Int()
    username = String()
    full_name = String()
    age = Int()

    # playlists deste usuário
    playlists = List(lambda: PlaylistType)


# ====================================
#        ROOT QUERY
# ====================================

class Query(ObjectType):

    users = List(UserType)
    tracks = List(TrackType)

    playlists_of_user = List(PlaylistType, user_id=Int(required=True))
    tracks_of_playlist = List(TrackType, playlist_id=Int(required=True))

    playlists_containing_track = List(PlaylistType, track_id=Int(required=True))

    track_info = Field(TrackType, track_id=Int(required=True))

    # -----------------------------------

    def resolve_users(root, info):
        db = SessionLocal()
        return db.query(User).all()

    def resolve_tracks(root, info):
        db = SessionLocal()
        return db.query(Track).all()

    def resolve_playlists_of_user(root, info, user_id):
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        return user.playlists if user else []

    def resolve_tracks_of_playlist(root, info, playlist_id):
        db = SessionLocal()
        playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
        return playlist.tracks if playlist else []

    def resolve_playlists_containing_track(root, info, track_id):
        db = SessionLocal()
        track = db.query(Track).filter(Track.id == track_id).first()
        return track.playlists if track else []

    def resolve_track_info(root, info, track_id):
        db = SessionLocal()
        return db.query(Track).filter(Track.id == track_id).first()


schema = graphene.Schema(query=Query)
