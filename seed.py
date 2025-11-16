from database import SessionLocal, MEDIA_DIR
from models.streaming_model import User, Playlist, Track
import os

def seed_db():
    db = SessionLocal()
    try:
        if db.query(User).first():
            return

        # Usuários
        u1 = User(username="alice", full_name="Alice Silva")
        u2 = User(username="bob", full_name="Bob Pereira")
        db.add_all([u1, u2])
        db.commit()

        # Tracks automáticas: pega todos os MP3 da pasta MEDIA_DIR
        tracks = []
        for file in os.listdir(MEDIA_DIR):
            if file.lower().endswith(".mp3"):
                file_path = MEDIA_DIR / file
                title = os.path.splitext(file)[0]  # nome do arquivo sem extensão

                track = Track(
                    title=title,
                    artist="Desconhecido",
                    album="Desconhecido",
                    duration=0,  # pode ser calculado
                    file_path=str(file_path)
                )
                tracks.append(track)

        db.add_all(tracks)
        db.commit()

        # Playlists
        p1 = Playlist(name="Favoritas da Alice", description="Minhas preferidas", owner_id=u1.id)
        p2 = Playlist(name="Road trip", description="Músicas para viagem", owner_id=u1.id)
        p3 = Playlist(name="Chill do Bob", description="Relax", owner_id=u2.id)
        db.add_all([p1, p2, p3])
        db.commit()

        # Adiciona todas as músicas na playlist do Bob, por exemplo
        for t in tracks:
            p3.tracks.append(t)

        db.commit()

    finally:
        db.close()
