import json
import os
from typing import List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from .config.config import Settings
from .config.logging_config import LoggingManager, get_logger
from .migration.migration_service import MigrationService


settings = Settings()
logging_manager = LoggingManager(settings)
logging_manager.setup_logging()
logger = get_logger(__name__)

migration_service = MigrationService(settings)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup complete.")
    yield
    logger.info("Application shutdown.")

app = FastAPI(lifespan=lifespan)

# Mount static files and templates
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

class MigrationRequest(BaseModel):
    ieees: List[str]
    direction: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request) -> Any:
    try:
        logger.info("Fetching device list for UI.")
        options = _load_options()
        zha_devices = await migration_service.get_zha_devices(
            db_path=options.get("zha_db", settings.ZHA_DB_PATH),
            registry_path=options.get("zha_registry", settings.ZHA_REGISTRY_PATH),
            z2m_db_path=options.get("z2m_db", settings.Z2M_DB_PATH)
        )
        logger.info(f"Found {len(zha_devices)} devices to display.")
        return templates.TemplateResponse("index.html", {"request": request, "zha_devices": zha_devices})
    except Exception as exc:
        logger.error(f"Error loading root page: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))

@app.get("/health")
async def health_check():
    """Standard health check endpoint."""
    return JSONResponse(content={"status": "ok"})

@app.websocket("/api")
async def websocket_endpoint(websocket: WebSocket):
    """Accept and hold the WebSocket connection for Ingress health checks."""
    await websocket.accept()
    try:
        while True:
            # Keep the connection alive by waiting for messages
            await websocket.receive_text()
    except Exception:
        # Connection closed by the client (Ingress)
        logger.debug("Ingress WebSocket connection closed.")

@app.post("/migrate")
async def migrate(request: MigrationRequest) -> Any:
    try:
        logger.info(f"Received migration request for {len(request.ieees)} devices.")
        options = _load_options()
        results = await migration_service.migrate_to_z2m(
            zha_db_path=options.get("zha_db", settings.ZHA_DB_PATH),
            zha_registry_path=options.get("zha_registry", settings.ZHA_REGISTRY_PATH),
            z2m_db_path=options.get("z2m_db", settings.Z2M_DB_PATH),
            selected_ieees=request.ieees,
            backup_dir=settings.CONFIG_DIR
        )
        logger.info("Migration process completed.")
        return {"status": "success", "results": results}
    except Exception as exc:
        logger.error(f"Migration failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))

def _load_options() -> Dict[str, Any]:
    if not os.path.exists(settings.OPTIONS_PATH):
        logger.warning("options.json not found, using default paths.")
        return settings.DEFAULT_OPTIONS
    with open(settings.OPTIONS_PATH, 'r', encoding=settings.UTF8_ENCODING) as file:
        return json.load(file)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_config=logging_manager.get_uvicorn_log_config()
    )
