import grpc
from concurrent import futures

from google.protobuf.empty_pb2 import Empty

import music_pb2
import music_pb2_grpc

from database import SessionLocal
from models.streaming_model import User, Track, Playlist


class MusicService(music_pb2_grpc.MusicServiceServicer):

    # ==========================
    #         USERS
    # ==========================
    def ListUsers(self, request, context):
        db = SessionLocal()
        users = db.query(User).all()

        response = music_pb2.UserList()

        for u in users:
            user = response.users.add()
            user.id = u.id
            user.username = u.username
            user.full_name = u.full_name or ""
            user.age = getattr(u, "age", 0)

        return response

    # ==========================
    #         TRACKS
    # ==========================
    def ListTracks(self, request, context):
        db = SessionLocal()
        tracks = db.query(Track).all()

        response = music_pb2.TrackList()

        for t in tracks:
            track = response.tracks.add()
            track.id = t.id
            track.title = t.title
            track.artist = t.artist or ""
            track.file_path = t.file_path or ""

        return response

    # ==========================
    #     PLAYLISTS OF USER
    # ==========================
    def PlaylistsOfUser(self, request, context):
        db = SessionLocal()
        user = db.query(User).filter(User.id == request.id).first()

        if not user:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("User not found")
            return music_pb2.PlaylistList()

        response = music_pb2.PlaylistList()

        for p in user.playlists:
            playlist = response.playlists.add()
            playlist.id = p.id
            playlist.name = p.name
            playlist.owner_id = p.owner_id

        return response

    # ==========================
    #     TRACKS OF PLAYLIST
    # ==========================
    def TracksOfPlaylist(self, request, context):
        db = SessionLocal()
        playlist = db.query(Playlist).filter(Playlist.id == request.id).first()

        if not playlist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Playlist not found")
            return music_pb2.TrackList()

        response = music_pb2.TrackList()

        for t in playlist.tracks:
            track = response.tracks.add()
            track.id = t.id
            track.title = t.title
            track.artist = t.artist or ""
            track.file_path = t.file_path or ""

        return response

    # ==========================
    #   PLAYLISTS CONTAINING TRACK
    # ==========================
    def PlaylistsContainingTrack(self, request, context):
        db = SessionLocal()
        track = db.query(Track).filter(Track.id == request.id).first()

        if not track:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Track not found")
            return music_pb2.PlaylistList()

        response = music_pb2.PlaylistList()

        for p in track.playlists:
            playlist = response.playlists.add()
            playlist.id = p.id
            playlist.name = p.name
            playlist.owner_id = p.owner_id

        return response

    # ==========================
    #         TRACK INFO
    # ==========================
    def TrackInfo(self, request, context):
        db = SessionLocal()
        t = db.query(Track).filter(Track.id == request.id).first()

        if not t:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Track not found")
            return music_pb2.Track()

        return music_pb2.Track(
            id=t.id,
            title=t.title,
            artist=t.artist or "",
            file_path=t.file_path or ""
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    music_pb2_grpc.add_MusicServiceServicer_to_server(MusicService(), server)
    server.add_insecure_port("[::]:50051")
    print("gRPC server running at 0.0.0.0:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
