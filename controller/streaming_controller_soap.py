from spyne import Application, rpc, ServiceBase, Integer, Unicode, Array, ComplexModel
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

from database import SessionLocal
from models.streaming_model import User, Track, Playlist


# ============================
#   MODELOS DE RESPOSTA SOAP
# ============================

class UserInfo(ComplexModel):
    id = Integer
    username = Unicode
    full_name = Unicode


class TrackInfo(ComplexModel):
    id = Integer
    title = Unicode
    artist = Unicode
    duration = Integer  # segundos


class PlaylistInfo(ComplexModel):
    id = Integer
    name = Unicode


# ============================
#         SERVIÇO SOAP
# ============================

class MusicSoapService(ServiceBase):

    # ------------------------------
    #   /users (REST → list_users)
    # ------------------------------
    @rpc(_returns=Array(UserInfo))
    def list_users(ctx):
        db = SessionLocal()
        users = db.query(User).all()
        return [
            UserInfo(id=u.id, username=u.username, full_name=u.full_name)
            for u in users
        ]

    # ------------------------------
    #   /tracks (REST → list_tracks)
    # ------------------------------
    @rpc(_returns=Array(TrackInfo))
    def list_tracks(ctx):
        db = SessionLocal()
        tracks = db.query(Track).all()
        return [
            TrackInfo(id=t.id, title=t.title, artist=t.artist, duration=t.duration)
            for t in tracks
        ]

    # -------------------------------------------------------------
    #   /users/{id}/playlists (REST → playlists_of_user)
    # -------------------------------------------------------------
    @rpc(Integer, _returns=Array(PlaylistInfo))
    def get_playlists_of_user(ctx, user_id):
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        return [
            PlaylistInfo(id=p.id, name=p.name)
            for p in user.playlists
        ]

    # -------------------------------------------------------------
    #   /playlists/{id}/tracks (REST → tracks_of_playlist)
    # -------------------------------------------------------------
    @rpc(Integer, _returns=Array(TrackInfo))
    def get_tracks_of_playlist(ctx, playlist_id):
        db = SessionLocal()
        playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
        if not playlist:
            return []
        return [
            TrackInfo(id=t.id, title=t.title, artist=t.artist, duration=t.duration)
            for t in playlist.tracks
        ]

    # -------------------------------------------------------------
    #   /tracks/{id}/playlists (REST → playlists_containing_track)
    # -------------------------------------------------------------
    @rpc(Integer, _returns=Array(PlaylistInfo))
    def get_playlists_containing_track(ctx, track_id):
        db = SessionLocal()
        track = db.query(Track).filter(Track.id == track_id).first()
        if not track:
            return []
        return [
            PlaylistInfo(id=p.id, name=p.name)
            for p in track.playlists
        ]

    # -------------------------------------------------------------
    #   /stream/{id} (REST → retorna áudio)
    #   SOAP NÃO STREAMA → retornamos metadados
    # -------------------------------------------------------------
    @rpc(Integer, _returns=TrackInfo)
    def get_track_info(ctx, track_id):
        db = SessionLocal()
        track = db.query(Track).filter(Track.id == track_id).first()
        if not track:
            return TrackInfo(id=None, title="Not found", artist="", duration=0)

        return TrackInfo(
            id=track.id,
            title=track.title,
            artist=track.artist,
            duration=track.duration
        )


# ============================
#       APLICAÇÃO SOAP
# ============================

soap_app = Application(
    [MusicSoapService],
    tns="soap.users.service",
    in_protocol=Soap11(),
    out_protocol=Soap11(),
)

soap_service = WsgiApplication(soap_app)
