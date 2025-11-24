import grpc
import streaming_pb2
import streaming_pb2_grpc

channel = grpc.insecure_channel("localhost:50051")
client = streaming_pb2_grpc.MusicServiceStub(channel)

# ============================================================
# 1) GetUsers
# ============================================================
print("\n=== 1) USERS ===")
resp = client.GetUsers(streaming_pb2.EmptyRequest())
for u in resp.users:
    print(f"{u.id} - {u.username} ({u.full_name}) age={u.age}")

# ============================================================
# 2) GetTracks
# ============================================================
print("\n=== 2) TRACKS ===")
resp = client.GetTracks(streaming_pb2.EmptyRequest())
for t in resp.tracks:
    print(f"{t.id} - {t.title} by {t.artist}")

# ============================================================
# 3) PlaylistsOfUser
# ============================================================
print("\n=== 3) PLAYLISTS OF USER 1 ===")
resp = client.PlaylistsOfUser(streaming_pb2.UserIdRequest(user_id=1))
for p in resp.playlists:
    print(f"{p.id} - {p.name} (owner: {p.owner.username})")
    for t in p.tracks:
        print(f"   • {t.id} - {t.title}")

# ============================================================
# 4) TracksOfPlaylist
# ============================================================
print("\n=== 4) TRACKS OF PLAYLIST 1 ===")
resp = client.TracksOfPlaylist(streaming_pb2.PlaylistIdRequest(playlist_id=1))
for t in resp.tracks:
    print(f"{t.id} - {t.title} by {t.artist}")

# ============================================================
# 5) PlaylistsContainingTrack
# ============================================================
print("\n=== 5) PLAYLISTS CONTAINING TRACK 1 ===")
resp = client.PlaylistsContainingTrack(streaming_pb2.TrackIdRequest(track_id=3))
for p in resp.playlists:
    print(f"{p.id} - {p.name} (owner: {p.owner.username})")

# ============================================================
# 6) TrackInfo
# ============================================================
print("\n=== 6) TRACK INFO (track_id = 1) ===")
resp = client.TrackInfo(streaming_pb2.TrackIdRequest(track_id=1))
t = resp.track
if t:
    print(f"ID: {t.id}")
    print(f"Title: {t.title}")
    print(f"File Path: {t.file_path}")
else:
    print("Track not found")
