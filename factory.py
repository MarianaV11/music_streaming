from fastapi import FastAPI

from controller.streaming_controller import router
from database import Base, engine, init_db
from seed import seed_db


def create_app():
    app = FastAPI(title="Mini Music Streaming Service")

    # 🔥 Evento executado 1 vez ao iniciar o servidor
    @app.on_event("startup")
    def startup_event():
        print("→ Criando tabelas do banco...")
        Base.metadata.create_all(bind=engine)

        print("→ Inicializando banco...")
        init_db()

        print("→ Inserindo dados iniciais...")
        seed_db()

    # Rotas
    app.include_router(router, prefix="/api")

    return app
