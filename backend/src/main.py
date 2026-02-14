from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import auth, graph, projects, ingestion
from src.config import settings
from src.infrastructure.persistence.neo4j.client import Neo4jClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    await Neo4jClient.connect()
    try:
        yield
    finally:
        await Neo4jClient.disconnect()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 璺敱娉ㄥ唽
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(projects.graph_router)
app.include_router(graph.router)
app.include_router(ingestion.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
