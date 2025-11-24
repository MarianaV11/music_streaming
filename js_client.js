import grpc from "@grpc/grpc-js";
import protoLoader from "@grpc/proto-loader";

const PROTO_PATH = "./streaming.proto";

// ====================================================
//   LOAD DO PROTO
// ====================================================
const packageDef = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});

const proto = grpc.loadPackageDefinition(packageDef).music;

// ====================================================
//   CLIENTE gRPC
// ====================================================
const client = new proto.MusicService(
  "localhost:50052",
  grpc.credentials.createInsecure()
);

// ====================================================
// 1) GetUsers
// ====================================================
client.GetUsers({}, (err, resp) => {
  console.log("\n=== 1) USERS ===");
  if (err) return console.error(err);
  resp.users.forEach((u) =>
    console.log(`${u.id} - ${u.username} (${u.full_name}) age=${u.age}`)
  );
});

// ====================================================
// 2) GetTracks
// ====================================================
client.GetTracks({}, (err, resp) => {
  console.log("\n=== 2) TRACKS ===");
  if (err) return console.error(err);
  resp.tracks.forEach((t) =>
    console.log(`${t.id} - ${t.title} by ${t.artist}`)
  );
});

// ====================================================
// 3) PlaylistsOfUser
// ====================================================
client.PlaylistsOfUser({ user_id: 1 }, (err, resp) => {
  console.log("\n=== 3) PLAYLISTS OF USER 1 ===");
  if (err) return console.error(err);
  resp.playlists.forEach((p) => {
    console.log(`${p.id} - ${p.name} (owner: ${p.owner?.username})`);
    if (p.tracks) {
      p.tracks.forEach((t) => console.log(`   • ${t.id} - ${t.title}`));
    }
  });
});

// ====================================================
// 4) TracksOfPlaylist
// ====================================================
client.TracksOfPlaylist({ playlist_id: 1 }, (err, resp) => {
  console.log("\n=== 4) TRACKS OF PLAYLIST 1 ===");
  if (err) return console.error(err);
  resp.tracks.forEach((t) =>
    console.log(`${t.id} - ${t.title} by ${t.artist}`)
  );
});

// ====================================================
// 5) PlaylistsContainingTrack
// ====================================================
client.PlaylistsContainingTrack({ track_id: 1 }, (err, resp) => {
  console.log("\n=== 5) PLAYLISTS CONTAINING TRACK 1 ===");
  if (err) return console.error(err);
  resp.playlists.forEach((p) =>
    console.log(`${p.id} - ${p.name} (owner: ${p.owner?.username})`)
  );
});

// ====================================================
// 6) TrackInfo
// ====================================================
client.TrackInfo({ track_id: 1 }, (err, resp) => {
  console.log("\n=== 6) TRACK INFO (1) ===");
  if (err) return console.error(err);

  const t = resp.track;
  if (!t) return console.log("Track not found");

  console.log(`ID: ${t.id}`);
  console.log(`Title: ${t.title}`);
  console.log(`Artist: ${t.artist}`);
  console.log(`File Path: ${t.file_path}`);
  console.log(`Duration: ${t.duration}`);
});
