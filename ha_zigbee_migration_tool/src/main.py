import json
import logging
import os
from typing import List, Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from src.config import settings
from src.migration.migration_service import migration_service

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=f"[Migration Tool] %(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()

# Mount the 'static' directory for CSS, JS, etc.
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Point the Jinja2Templates to the 'templates' directory
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


class MigrationRequest(BaseModel):
    ieees: List[str]
    direction: str


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request) -> Any:
    try:
        options = _load_options()
        zha_devices = await migration_service.get_zha_devices(
            db_path=options.get("zha_db", settings.ZHA_DB_PATH),
            registry_path=options.get("zha_registry", settings.ZHA_REGISTRY_PATH),
            z2m_db_path=options.get("z2m_db", settings.Z2M_DB_PATH)
        )
        return templates.TemplateResponse("index.html", {
            "request": request,
            "zha_devices": zha_devices
        })
    except Exception as exc:
        logger.error(f"[Main] Error loading root page: {str(exc)}")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/migrate")
async def migrate(request: MigrationRequest) -> Any:
    try:
        options = _load_options()
        results = await migration_service.migrate_to_z2m(
            zha_db_path=options.get("zha_db", settings.ZHA_DB_PATH),
            zha_registry_path=options.get("zha_registry", settings.ZHA_REGISTRY_PATH),
            z2m_db_path=options.get("z2m_db", settings.Z2M_DB_PATH),
            selected_ieees=request.ieees,
            backup_dir=settings.CONFIG_DIR
        )
        return {"status": "success", "results": results}
    except Exception as exc:
        logger.error(f"[Main] Migration failed: {str(exc)}")
        raise HTTPException(status_code=500, detail=str(exc))


def _load_options() -> Dict[str, Any]:
    if not os.path.exists(settings.OPTIONS_PATH):
        return settings.DEFAULT_OPTIONS

    with open(settings.OPTIONS_PATH, 'r', encoding=settings.UTF8_ENCODING) as file:
        return json.load(file)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
