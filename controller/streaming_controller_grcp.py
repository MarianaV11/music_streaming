import grpc
from concurrent import futures
from database import SessionLocal
from models.streaming_model import User, Track, Playlist

import streaming_pb2
import streaming_pb2_grpc


class MusicService(streaming_pb2_grpc.MusicServiceServicer):

    def GetUsers(self, request, context):
        db = SessionLocal()
        return streaming_pb2.UsersResponse(
            users=[
                streaming_pb2.User(
                    id=u.id,
                    username=u.username,
                    full_name=u.full_name,
                    age=u.age
                ) for u in db.query(User).all()
            ]
        )

    def GetTracks(self, request, context):
        db = SessionLocal()
        return streaming_pb2.TracksResponse(
            tracks=[
                streaming_pb2.Track(
                    id=t.id,
                    title=t.title,
                    file_path=t.file_path,
                ) for t in db.query(Track).all()
            ]
        )

    def PlaylistsOfUser(self, request, context):
        db = SessionLocal()
        user = db.query(User).filter(User.id == request.user_id).first()
        return streaming_pb2.PlaylistsResponse(
            playlists=[
                streaming_pb2.Playlist(
                    id=p.id,
                    name=p.name,
                    owner=streaming_pb2.User(
                        id=user.id,
                        username=user.username,
                        full_name=user.full_name,
                        age=user.age
                    ),
                    tracks=[
                        streaming_pb2.Track(
                            id=t.id,
                            title=t.title,
                            file_path=t.file_path,
                        ) for t in p.tracks
                    ]
                ) for p in user.playlists
            ] if user else []
        )

    def TracksOfPlaylist(self, request, context):
        db = SessionLocal()
        playlist = db.query(Playlist).filter(Playlist.id == request.playlist_id).first()
        return streaming_pb2.TracksResponse(
            tracks=[
                streaming_pb2.Track(
                    id=t.id,
                    title=t.title,
                    file_path=t.file_path,
                ) for t in playlist.tracks
            ] if playlist else []
        )

    def PlaylistsContainingTrack(self, request, context):
        db = SessionLocal()
        track = db.query(Track).filter(Track.id == request.track_id).first()
        return streaming_pb2.PlaylistsResponse(
            playlists=[
                streaming_pb2.Playlist(
                    id=p.id,
                    name=p.name,
                    owner=streaming_pb2.User(
                        id=p.owner.id,
                        username=p.owner.username,
                        full_name=p.owner.full_name,
                        age=p.owner.age
                    )
                ) for p in track.playlists
            ] if track else []
        )

    def TrackInfo(self, request, context):
        db = SessionLocal()
        t = db.query(Track).filter(Track.id == request.track_id).first()
        if not t:
            return streaming_pb2.TrackResponse(track=None)

        return streaming_pb2.TrackResponse(
            track=streaming_pb2.Track(
                id=t.id,
                title=t.title,
                file_path=t.file_path,
            )
        )


def serve():
    print("running")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    streaming_pb2_grpc.add_MusicServiceServicer_to_server(MusicService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
