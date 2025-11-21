import graphene
from graphene import ObjectType, Int, String, Field, List
from database import SessionLocal
from models.streaming_model import User, Track, Playlist


# ====================================
#     TIPOS GRAPHQL (schemas)
# ====================================

class UserType(ObjectType):
    id = Int()
    username = String()
    full_name = String()
    age = Int()


class TrackType(ObjectType):
    id = Int()
    title = String()
    artist = String()
    file_path = String()
    duration = Int()


class PlaylistType(ObjectType):
    id = Int()
    name = String()
    owner = Field(lambda: UserType)
    tracks = List(lambda: TrackType)


# ====================================
#     ROOT QUERY (equivalente REST)
# ====================================

class Query(ObjectType):

    # /users
    users = List(UserType)

    # /tracks
    tracks = List(TrackType)

    # /users/{id}/playlists
    playlists_of_user = List(PlaylistType, user_id=Int(required=True))

    # /playlists/{id}/tracks
    tracks_of_playlist = List(TrackType, playlist_id=Int(required=True))

    # /tracks/{id}/playlists
    playlists_containing_track = List(PlaylistType, track_id=Int(required=True))

    # /stream/{id} → aqui só retornamos metadados
    track_info = Field(TrackType, track_id=Int(required=True))

    # ------------------------------
    #   IMPLEMENTAÇÃO DOS RESOLVERS
    # ------------------------------

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
