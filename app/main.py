from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.v1.routers import api_router

app = FastAPI()
app.add_route("/graphql", GraphQLApp(schema=schema))

app.include_router(api_router, prefix="/app/v1")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)