from database import SessionLocal, MEDIA_DIR
from models.streaming_model import User, Playlist, Track
import os

def seed_db():
    db = SessionLocal()
    try:
        if db.query(User).first():
            return

        u1 = User(username="Mariana", full_name="Mariana Vieira", age=22)
        u2 = User(username="Beatriz", full_name="Ana Beatriz Matos", age=21)
        u3 = User(username="Biel", full_name="João Gabriel", age=25)

        db.add_all([u1, u2, u3])
        db.commit()

        tracks = []
        for file in os.listdir(MEDIA_DIR):
            if file.lower().endswith(".mp3"):
                file_path = MEDIA_DIR / file
                title = os.path.splitext(file)[0]
                artist = title.split("-")[0]
    
                track = Track(
                    title=title,
                    artist=artist,
                    file_path=str(file_path)
                )
                tracks.append(track)

        db.add_all(tracks)
        db.commit()

        p1 = Playlist(name="Mari", owner_id=u1.id)
        p2 = Playlist(name="Bia",  owner_id=u2.id)
        p3 = Playlist(name="Biel",  owner_id=u3.id)
        db.add_all([p1, p2, p3])
        db.commit()

        for t in tracks:
            p3.tracks.append(t)
        
        p1.tracks.append(tracks[1])
        p2.tracks.append(tracks[0])

        db.commit()

    finally:
        db.close()
