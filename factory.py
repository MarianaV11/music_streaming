from fastapi import FastAPI
from starlette.middleware.wsgi import WSGIMiddleware
from starlette_graphene3 import GraphQLApp

from controller.streaming_controller_graphql import schema
from controller.streaming_controller_rest import router
from controller.streaming_controller_soap import soap_service
from database import Base, engine, init_db
from seed import seed_db


def create_app():
    app = FastAPI(title="Mini Music Streaming Service")

    @app.on_event("startup")
    def startup_event():
        print("→ Creating tables")
        Base.metadata.create_all(bind=engine)

        print("→ Initializing db")
        init_db()

        print("→ Inserting datas.")
        seed_db()
        
    # REST
    app.include_router(router, prefix="/api")

    # SOAP
    app.mount("/soap", WSGIMiddleware(soap_service))
    
    # GRAPHQL
    router.add_route("/graphql", GraphQLApp(schema=schema, graphiql=True))
    
    # GRPC 

    return app
