from factory import create_app
from database import Base, engine, init_db
from seed import seed_db

app = create_app()

# uvicorn main:app --reload
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)

    init_db()
    seed_db()
