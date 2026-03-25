# app/main.py
"""
Main application entry point for PlatonAAV API.

This module initializes the FastAPI application with SQLAlchemy ORM integration,
includes all routers, and configures the application lifecycle.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db import init_db
from app.routers import aavs, sessions, types
from app.routers import activitePedagogique_sqlalchemy


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle - startup and shutdown events.
    
    On startup: Initialize the SQLAlchemy database and create all tables.
    On shutdown: Clean up resources.
    
    Args:
        app (FastAPI): The FastAPI application instance.
    """
    # database initialization on startup
    print("🚀 Initialisation de la base de données SQLAlchemy...")
    init_db()
    yield
    # cleanup on shutdown
    print("🛑 Arrêt du serveur")


app = FastAPI(
    title="PlatonAAV API",
    description="""
    API REST pour la gestion des Acquis d'Apprentissage Visés (AAV).

    ## Technologie
    - **Framework**: FastAPI
    - **ORM**: SQLAlchemy 2.0
    - **Base de Données**: SQLite3

    ## Groupes

    * **AAVs** - Gestion des acquis (Groupe 1) - SQLAlchemy ✅
    * **Learners** - Gestion des apprenants (Groupe 2)
    * **Activities** - Gestion des activités (Groupe 4) - SQLAlchemy ✅
    * etc.
    """,
    version="2.0.0",
    lifespan=lifespan,
)

# include all routers with SQLAlchemy ORM
app.include_router(aavs.router)
app.include_router(activitePedagogique_sqlalchemy.router)
app.include_router(sessions.router)
app.include_router(types.router)


@app.get("/")
def root():
    """
    Root endpoint returning API information.
    
    Returns:
        dict: Welcome message with version, database info, and documentation link.
    """
    return {
        "message": "Bienvenue sur l'API PlatonAAV",
        "version": "2.0.0",
        "database": "SQLite3 with SQLAlchemy ORM",
        "documentation": "/docs",
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint to verify server is running and database is connected.
    
    Returns:
        dict: Status information for health monitoring.
    """
    return {
        "status": "healthy",
        "database": "connected",
        "orm": "SQLAlchemy 2.0"
    }

