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


class PlaylistInfo(ComplexModel):
    id = Integer
    name = Unicode


# ============================
#         SERVIÇO SOAP
# ============================
class MusicSoapService(ServiceBase):

    @rpc(_returns=Array(UserInfo))
    def getUsers(ctx):
        db = SessionLocal()
        users = db.query(User).all()
        return [UserInfo(id=u.id, username=u.username, full_name=u.full_name) for u in users]

    @rpc(_returns=Array(TrackInfo))
    def getTracks(ctx):
        db = SessionLocal()
        tracks = db.query(Track).all()
        return [TrackInfo(id=t.id, title=t.title) for t in tracks]

    @rpc(Integer, _returns=Array(PlaylistInfo))
    def playlistsOfUser(ctx, user_id):
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        return [PlaylistInfo(id=p.id, name=p.name) for p in user.playlists]

    @rpc(Integer, _returns=Array(TrackInfo))
    def tracksOfPlaylist(ctx, playlist_id):
        db = SessionLocal()
        playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
        if not playlist:
            return []
        return [TrackInfo(id=t.id, title=t.title) for t in playlist.tracks]

    @rpc(Integer, _returns=Array(PlaylistInfo))
    def playlistsContainingTrack(ctx, track_id):
        db = SessionLocal()
        track = db.query(Track).filter(Track.id == track_id).first()
        if not track:
            return []
        return [PlaylistInfo(id=p.id, name=p.name) for p in track.playlists]

    @rpc(Integer, _returns=TrackInfo)
    def trackInfo(ctx, track_id):
        db = SessionLocal()
        track = db.query(Track).filter(Track.id == track_id).first()
        if not track:
            return TrackInfo(id=None, title="Not found", artist="", duration=0)
        return TrackInfo(id=track.id, title=track.title)


# ============================
#       APLICAÇÃO SOAP
# ============================

soap_app = Application(
    [MusicSoapService],
    tns="http://example.com/music",  # ⬅ mesmo que xmlns:mus
    in_protocol=Soap11(),
    out_protocol=Soap11(),
)

soap_service = WsgiApplication(soap_app)
