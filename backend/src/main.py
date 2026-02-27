from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import auth, graph, projects, ingestion
from src.api.routers import entities, relations, query, visualization, extraction
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
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    description="""
    Knowledge Graph Platform API
    
    ## Features
    - Graph project management
    - Entity and relation CRUD
    - Advanced query and visualization
    - Knowledge extraction pipeline
    - Graph algorithms (PageRank, Betweenness, Community Detection)
    """
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由注册
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(projects.graph_router)
app.include_router(graph.router)
app.include_router(ingestion.router)

# Phase 2: Query & Visualization Routes
app.include_router(entities.router)
app.include_router(relations.router)
app.include_router(query.router)
app.include_router(visualization.router)
app.include_router(extraction.router)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "0.2.0",
        "features": [
            "graph_management",
            "query",
            "visualization",
            "extraction"
        ]
    }


@app.get("/")
async def root():
    return {
        "message": "Knowledge Graph Platform API",
        "version": "0.2.0",
        "docs": "/docs"
    }
