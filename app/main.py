import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.database import init_database, DatabaseError
from app.routers import (
    alerts, reports, comparaison, metrics, dashboard, 
    aavs, sessions, types, activitePedagogique,
    attempts, exerciseEngine, learners, navigation,
    ontologies, promptFabricationAAV, remediation, statuts
)

app = FastAPI(
    title="Group 7 — Quality Metrics AAV",
    description="Analytics and reporting API for pedagogical teams.",
    version="1.0.0"
)

# ============================================
# DATABASE INITIALIZATION
# ============================================
@app.on_event("startup")
def startup():
    """Creates all tables on startup (common + Group 7)."""
    init_database()
# ============================================
# ROUTERS
# ============================================
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(comparaison.router, prefix="/metrics/compare", tags=["comparisons"])
app.include_router(metrics.router, prefix="/metrics/aav", tags=["metrics"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(aavs.router, prefix="/aavs", tags=["aavs"])
app.include_router(activitePedagogique.router, prefix="/activites", tags=["activitePedagogique"])
app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
app.include_router(types.router, prefix="/types", tags=["types"])

# Missing routers from other groups
app.include_router(attempts.router, prefix="/attempts", tags=["attempts"])
app.include_router(exerciseEngine.router, tags=["exerciseEngine"])  # routes already include /aavs & /exercises paths
app.include_router(learners.router, prefix="/learners", tags=["learners"])
app.include_router(navigation.router, prefix="/navigation", tags=["navigation"])
app.include_router(ontologies.router, prefix="/ontologies", tags=["ontologies"])
app.include_router(promptFabricationAAV.router, prefix="/promptFabricationAAV", tags=["promptFabricationAAV"])
app.include_router(remediation.router, prefix="/remediation", tags=["remediation"])
app.include_router(statuts.router, tags=["statuts"])  # routes already start with /learning-status
# ============================================
# GESTIONNAIRES D'EXCEPTIONS GLOBAUX
# ============================================

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handles HTTP 404, 400, etc. errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles Pydantic validation errors (422)."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Les données fournies sont invalides",
            "details": errors,
            "path": str(request.url)
        }
    )

@app.exception_handler(DatabaseError)
async def database_exception_handler(request: Request, exc: DatabaseError):
    """Handles database errors."""
    error_msg = str(exc)
    
    # Check if it's a 404 from HTTPException
    if "404:" in error_msg:
        status_code = 404
        detail = error_msg.replace("404: ", "")
    else:
        status_code = 500
        detail = error_msg
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": "database_error" if status_code != 404 else "not_found",
            "message": detail if status_code == 404 else "Une erreur est survenue lors de l'accès aux données",
            "details": {"error": str(exc)} if status_code != 404 else {},
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catches all unhandled exceptions."""
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "Une erreur interne est survenue",
            "details": str(exc),
            "path": str(request.url)
        }
    )

