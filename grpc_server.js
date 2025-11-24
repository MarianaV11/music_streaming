import grpc from "@grpc/grpc-js";
import protoLoader from "@grpc/proto-loader";
import { Sequelize, DataTypes } from "sequelize";

const PROTO_PATH = "./streaming.proto";

// ==============================================
//   CARREGA O PROTO
// ==============================================

const pkgDef = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});

const proto = grpc.loadPackageDefinition(pkgDef).music;

// ==============================================
//   BANCO DE DADOS
// ==============================================

const sequelize = new Sequelize({
  dialect: "sqlite",
  storage: "./music_service.db",
  logging: false,
});

const User = sequelize.define(
  "User",
  {
    username: DataTypes.STRING,
    full_name: DataTypes.STRING,
    age: DataTypes.INTEGER,
  },
  { timestamps: false }
);

const Track = sequelize.define(
  "Track",
  {
    title: DataTypes.STRING,
    artist: DataTypes.STRING,
    file_path: DataTypes.STRING,
  },
  { timestamps: false }
);

const Playlist = sequelize.define(
  "Playlist",
  {
    name: DataTypes.STRING,
    owner_id: DataTypes.INTEGER, // certifique-se de que essa coluna exista no DB
  },
  { timestamps: false }
);

// ==============================================
//   RELACIONAMENTOS
// ==============================================

// Usuário → Playlist
User.hasMany(Playlist, { foreignKey: "owner_id" });
Playlist.belongsTo(User, { foreignKey: "owner_id" });

// Playlist ↔ Track
Playlist.belongsToMany(Track, {
  through: "playlist_tracks",
  foreignKey: "playlist_id",
  otherKey: "track_id",
  timestamps: false, // desativa createdAt/updatedAt
});

Track.belongsToMany(Playlist, {
  through: "playlist_tracks",
  foreignKey: "track_id",
  otherKey: "playlist_id",
  timestamps: false,
});

// ==============================================
//   IMPLEMENTAÇÃO DOS ENDPOINTS
// ==============================================

const service = {
  async GetUsers(_, callback) {
    const users = await User.findAll();
    callback(null, { users });
  },

  async GetTracks(_, callback) {
    const tracks = await Track.findAll();
    callback(null, { tracks });
  },

  async PlaylistsOfUser({ user_id }, callback) {
    const whereClause = {};
    if (user_id != null) {
      whereClause.owner_id = user_id;
    }

    const playlists = await Playlist.findAll({
      where: whereClause,
      include: [
        { model: User, attributes: ["id", "username", "full_name", "age"] },
        { model: Track, attributes: ["id", "title", "artist", "file_path"] },
      ],
    });

    callback(null, { playlists });
  },

  async TracksOfPlaylist({ playlist_id }, callback) {
    const playlist = await Playlist.findByPk(playlist_id);
    const tracks = playlist
      ? await playlist.getTracks({
          attributes: ["id", "title", "artist", "file_path"],
        })
      : [];
    callback(null, { tracks });
  },

  async PlaylistsContainingTrack({ track_id }, callback) {
    const track = await Track.findByPk(track_id);
    const playlists = track
      ? await track.getPlaylists({
          include: [
            { model: User, attributes: ["id", "username", "full_name"] },
          ],
        })
      : [];
    callback(null, { playlists });
  },

  async TrackInfo({ track_id }, callback) {
    const track = await Track.findByPk(track_id);
    callback(null, { track });
  },
};

// ==============================================
//   SERVIDOR gRPC
// ==============================================

function start() {
  const server = new grpc.Server();

  server.addService(proto.MusicService.service, service);
  server.bindAsync(
    "localhost:50052",
    grpc.ServerCredentials.createInsecure(),
    () => {
      server.start();
      console.log("🔥 Servidor gRPC JS rodando em: localhost:50052");
    }
  );
}

start();
