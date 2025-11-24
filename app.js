// ================================================
//   IMPORTS
// ================================================
import express from "express";
import { Sequelize, DataTypes } from "sequelize";
import { ApolloServer } from "@apollo/server";
import { expressMiddleware } from "@apollo/server/express4";
import { createServer } from "http";
import soap from "soap";
import fs from "fs";

// ================================================
//   BANCO DE DADOS — SOMENTE LEITURA
// ================================================
const sequelize = new Sequelize({
  dialect: "sqlite",
  storage: "./music_service.db",
  logging: false,
});

// =============== MODELS ===============

// NÃO usar timestamps — banco não tem createdAt/updatedAt
const User = sequelize.define(
  "User",
  {
    username: { type: DataTypes.STRING, allowNull: false, unique: true },
    full_name: { type: DataTypes.STRING },
    age: { type: DataTypes.INTEGER },
  },
  { timestamps: false }
);

const Track = sequelize.define(
  "Track",
  {
    title: { type: DataTypes.STRING, allowNull: false },
    artist: { type: DataTypes.STRING },
    file_path: { type: DataTypes.TEXT },
  },
  { timestamps: false }
);

const Playlist = sequelize.define(
  "Playlist",
  {
    name: { type: DataTypes.STRING, allowNull: false },
  },
  { timestamps: false }
);

// Relações
User.hasMany(Playlist, { foreignKey: "owner_id" });
Playlist.belongsTo(User, { foreignKey: "owner_id" });

Playlist.belongsToMany(Track, {
  through: "playlist_tracks",
  timestamps: false,
  foreignKey: "playlist_id",
  otherKey: "track_id",
});

Track.belongsToMany(Playlist, {
  through: "playlist_tracks",
  timestamps: false,
  foreignKey: "track_id",
  otherKey: "playlist_id",
});

// ================================================
//   GRAPHQL
// ================================================
const typeDefs = `
  type User {
    id: ID!
    username: String!
    full_name: String
    age: Int
    playlists: [Playlist]
  }

  type Track {
    id: ID!
    title: String!
    artist: String
    file_path: String
    playlists: [Playlist]
  }

  type Playlist {
    id: ID!
    name: String!
    owner: User
    tracks: [Track]
  }

  type Query {
    users: [User]
    tracks: [Track]
    playlists_of_user(user_id: Int!): [Playlist]
    tracks_of_playlist(playlist_id: Int!): [Track]
    playlists_containing_track(track_id: Int!): [Playlist]
    track_info(track_id: Int!): Track
  }
`;

const resolvers = {
  Query: {
    users: () => User.findAll(),
    tracks: () => Track.findAll(),

    playlists_of_user: (_, { user_id }) =>
      Playlist.findAll({ where: { owner_id: user_id } }),

    tracks_of_playlist: async (_, { playlist_id }) => {
      const pl = await Playlist.findByPk(playlist_id);
      return pl ? pl.getTracks() : [];
    },

    playlists_containing_track: async (_, { track_id }) => {
      const tr = await Track.findByPk(track_id);
      return tr ? tr.getPlaylists() : [];
    },

    track_info: (_, { track_id }) => Track.findByPk(track_id),
  },

  Playlist: {
    owner: (playlist) => User.findByPk(playlist.owner_id),
    tracks: (playlist) => playlist.getTracks(),
  },

  User: {
    playlists: (user) => Playlist.findAll({ where: { owner_id: user.id } }),
  },

  Track: {
    playlists: (track) => track.getPlaylists(),
  },
};

// ================================================
//   SOAP COMPLETO (6 MÉTODOS)
// ================================================
const soapService = {
  MusicService: {
    MusicPort: {
      async getUsers() {
        const users = await User.findAll({ include: Playlist });
        return { users: JSON.stringify(users) };
      },

      async getTracks() {
        const tracks = await Track.findAll({ include: Playlist });
        return { tracks: JSON.stringify(tracks) };
      },

      async playlistsOfUser(args) {
        const playlists = await Playlist.findAll({
          where: { owner_id: args.user_id },
          include: [User, Track],
        });

        return { playlists: JSON.stringify(playlists) };
      },

      async tracksOfPlaylist(args) {
        const playlist = await Playlist.findByPk(args.playlist_id);
        const tracks = playlist ? await playlist.getTracks() : [];
        return { tracks: JSON.stringify(tracks) };
      },

      async playlistsContainingTrack(args) {
        const track = await Track.findByPk(args.track_id);
        const playlists = track ? await track.getPlaylists() : [];
        return { playlists: JSON.stringify(playlists) };
      },

      async trackInfo(args) {
        const track = await Track.findByPk(args.track_id, {
          include: Playlist,
        });
        return { track: JSON.stringify(track) };
      },
    },
  },
};

// WSDL COMPLETO
const wsdl = `<definitions name="MusicService"
  targetNamespace="http://example.com/music"
  xmlns="http://schemas.xmlsoap.org/wsdl/"
  xmlns:tns="http://example.com/music"
  xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
  xmlns:xsd="http://www.w3.org/2001/XMLSchema">

  <!-- TYPES (vazio, permitido em RPC) -->
  <types>
    <xsd:schema targetNamespace="http://example.com/music"/>
  </types>

  <!-- MESSAGES -->
  <message name="getUsersRequest"/>
  <message name="getUsersResponse">
    <part name="users" type="xsd:string"/>
  </message>

  <message name="getTracksRequest"/>
  <message name="getTracksResponse">
    <part name="tracks" type="xsd:string"/>
  </message>

  <message name="playlistsOfUserRequest">
    <part name="user_id" type="xsd:int"/>
  </message>
  <message name="playlistsOfUserResponse">
    <part name="playlists" type="xsd:string"/>
  </message>

  <message name="tracksOfPlaylistRequest">
    <part name="playlist_id" type="xsd:int"/>
  </message>
  <message name="tracksOfPlaylistResponse">
    <part name="tracks" type="xsd:string"/>
  </message>

  <message name="playlistsContainingTrackRequest">
    <part name="track_id" type="xsd:int"/>
  </message>
  <message name="playlistsContainingTrackResponse">
    <part name="playlists" type="xsd:string"/>
  </message>

  <message name="trackInfoRequest">
    <part name="track_id" type="xsd:int"/>
  </message>
  <message name="trackInfoResponse">
    <part name="track" type="xsd:string"/>
  </message>

  <!-- PORT TYPE -->
  <portType name="MusicPortType">

    <operation name="getUsers">
      <input message="tns:getUsersRequest"/>
      <output message="tns:getUsersResponse"/>
    </operation>

    <operation name="getTracks">
      <input message="tns:getTracksRequest"/>
      <output message="tns:getTracksResponse"/>
    </operation>

    <operation name="playlistsOfUser">
      <input message="tns:playlistsOfUserRequest"/>
      <output message="tns:playlistsOfUserResponse"/>
    </operation>

    <operation name="tracksOfPlaylist">
      <input message="tns:tracksOfPlaylistRequest"/>
      <output message="tns:tracksOfPlaylistResponse"/>
    </operation>

    <operation name="playlistsContainingTrack">
      <input message="tns:playlistsContainingTrackRequest"/>
      <output message="tns:playlistsContainingTrackResponse"/>
    </operation>

    <operation name="trackInfo">
      <input message="tns:trackInfoRequest"/>
      <output message="tns:trackInfoResponse"/>
    </operation>

  </portType>

  <!-- BINDING -->
  <binding name="MusicBinding" type="tns:MusicPortType">
    <soap:binding style="rpc" transport="http://schemas.xmlsoap.org/soap/http"/>

    <operation name="getUsers">
      <soap:operation soapAction="getUsers"/>
      <input>
        <soap:body use="encoded" namespace="http://example.com/music"
                   encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
      </input>
      <output>
        <soap:body use="encoded" namespace="http://example.com/music"
                   encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
      </output>
    </operation>

    <operation name="getTracks">
      <soap:operation soapAction="getTracks"/>
      <input>
        <soap:body use="encoded" namespace="http://example.com/music"
                   encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
      </input>
      <output>
        <soap:body use="encoded" namespace="http://example.com/music"
                   encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
      </output>
    </operation>

    <operation name="playlistsOfUser">
      <soap:operation soapAction="playlistsOfUser"/>
      <input>
        <soap:body use="encoded" namespace="http://example.com/music"
                   encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
      </input>
      <output>
        <soap:body use="encoded" namespace="http://example.com/music"
                   encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
      </output>
    </operation>

    <operation name="tracksOfPlaylist">
      <soap:operation soapAction="tracksOfPlaylist"/>
      <input>
        <soap:body use="encoded" namespace="http://example.com/music"
                   encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
      </input>
      <output>
        <soap:body use="encoded" namespace="http://example.com/music"
                   encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
      </output>
    </operation>

    <operation name="playlistsContainingTrack">
      <soap:operation soapAction="playlistsContainingTrack"/>
      <input>
        <soap:body use="encoded" namespace="http://example.com/music"
                   encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
      </input>
      <output>
        <soap:body use="encoded" namespace="http://example.com/music"
                   encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
      </output>
    </operation>

    <operation name="trackInfo">
      <soap:operation soapAction="trackInfo"/>
      <input>
        <soap:body use="encoded" namespace="http://example.com/music"
                   encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
      </input>
      <output>
        <soap:body use="encoded" namespace="http://example.com/music"
                   encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
      </output>
    </operation>

  </binding>

  <!-- SERVICE -->
  <service name="MusicService">
    <port name="MusicPort" binding="tns:MusicBinding">
      <soap:address location="http://localhost:3000/soap"/>
    </port>
  </service>

</definitions>
`;

// ================================================
//   REST
// ================================================
const restRouter = express.Router();

restRouter.get("/users", async (_, res) => {
  res.json(await User.findAll());
});

restRouter.get("/tracks", async (_, res) => {
  res.json(await Track.findAll());
});

restRouter.get("/playlists/:id/tracks", async (req, res) => {
  try {
    const { id } = req.params;

    const playlist = await Playlist.findByPk(id);

    if (!playlist) {
      return res.status(404).json({ error: "Playlist não encontrada" });
    }

    const tracks = await playlist.getTracks({
      attributes: ["id", "title", "artist", "file_path"],
    });

    return res.json(tracks);
  } catch (err) {
    console.error(err);
    return res
      .status(500)
      .json({ error: "Erro ao buscar músicas da playlist" });
  }
});

restRouter.get("/tracks/:track_id/playlists", async (req, res) => {
  try {
    const { track_id } = req.params;

    const track = await Track.findByPk(track_id);
    if (!track) {
      return res.status(404).json({ error: "Música não encontrada" });
    }

    const playlists = await track.getPlaylists({
      attributes: ["id", "name", "owner_id"],
    });

    return res.json(playlists);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Erro ao buscar playlists da música" });
  }
});

// ================================================
//   STREAM DE ÁUDIO
// ================================================
restRouter.get("/stream/:track_id", async (req, res) => {
  const { track_id } = req.params;

  try {
    const track = await Track.findByPk(track_id);

    if (!track) {
      return res.status(404).json({ error: "Música não encontrada" });
    }

    if (!track.file_path) {
      return res.status(404).json({ error: "Arquivo de áudio não disponível" });
    }

    const mediaPath = track.file_path;

    if (!fs.existsSync(mediaPath)) {
      return res.status(404).json({ error: "Arquivo não encontrado" });
    }

    const fileSize = fs.statSync(mediaPath).size;
    const range = req.headers.range;

    let start = 0;
    let end = fileSize - 1;

    if (range) {
      const [rStart, rEnd] = range.replace(/bytes=/, "").split("-");
      start = parseInt(rStart, 10);
      end = rEnd ? parseInt(rEnd, 10) : fileSize - 1;

      if (start >= fileSize) {
        return res.status(416).send("Requested range not satisfiable");
      }
    }

    const chunkSize = end - start + 1;
    const file = fs.createReadStream(mediaPath, { start, end });

    res.writeHead(range ? 206 : 200, {
      "Content-Range": `bytes ${start}-${end}/${fileSize}`,
      "Accept-Ranges": "bytes",
      "Content-Length": chunkSize,
      "Content-Type": "audio/mpeg",
    });

    file.pipe(res);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Erro interno" });
  }
});

// ================================================
//   APP PRINCIPAL
// ================================================
async function startServer() {
  await sequelize.authenticate();
  console.log("📦 Banco conectado (somente leitura)!");

  const app = express();

  app.use(express.json());

  // REST
  app.use("/api", restRouter);

  // SOAP
  soap.listen(app, "/soap", soapService, wsdl);

  // GRAPHQL
  const graphServer = new ApolloServer({ typeDefs, resolvers });
  await graphServer.start();
  app.use("/graphql", expressMiddleware(graphServer));

  const httpServer = createServer(app);

  httpServer.listen(3000, () => {
    console.log("🚀 Servidor rodando em http://localhost:3000");
    console.log("🔹 GraphQL:  http://localhost:3000/graphql");
    console.log("🔹 REST USERS:  http://localhost:3000/api/users");
    console.log("🔹 REST TRACKS: http://localhost:3000/api/tracks");
    console.log("🔹 SOAP:        http://localhost:3000/soap?wsdl");
  });
}

startServer();
