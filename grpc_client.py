import grpc
from google.protobuf.empty_pb2 import Empty

import music_pb2
import music_pb2_grpc


class MusicClient:
    def __init__(self):
        self.channel = grpc.insecure_channel("localhost:50051")
        self.stub = music_pb2_grpc.MusicServiceStub(self.channel)

    def list_users(self):
        response = self.stub.ListUsers(Empty())
        return response.users

    def list_tracks(self):
        response = self.stub.ListTracks(Empty())
        return response.tracks

    def playlists_of_user(self, user_id):
        request = music_pb2.UserId(id=user_id)
        response = self.stub.PlaylistsOfUser(request)
        return response.playlists

    def tracks_of_playlist(self, playlist_id):
        request = music_pb2.PlaylistId(id=playlist_id)
        response = self.stub.TracksOfPlaylist(request)
        return response.tracks

    def playlists_containing_track(self, track_id):
        request = music_pb2.TrackId(id=track_id)
        response = self.stub.PlaylistsContainingTrack(request)
        return response.playlists

    def track_info(self, track_id):
        request = music_pb2.TrackId(id=track_id)
        return self.stub.TrackInfo(request)


if __name__ == "__main__":
    client = MusicClient()

    print("\n=== USERS ===")
    for u in client.list_users():
        print(f"{u.id} - {u.username}")

    print("\n=== TRACKS ===")
    for t in client.list_tracks():
        print(f"{t.id} - {t.title}")

    print("\n=== PLAYLISTS OF USER 1 ===")
    for p in client.playlists_of_user(1):
        print(p.name)

    print("\n=== TRACK INFO (ID 1) ===")
    t = client.track_info(1)
    print(f"{t.id} - {t.title} - {t.artist}")
