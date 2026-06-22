import logging
import os
from dotenv import load_dotenv

load_dotenv()

from backend.services.config import load_settings

cfg = load_settings()
logging.basicConfig(
    level=cfg["logging"]["level"],
    format=cfg["logging"]["format"],
)

import uvicorn
from backend.api.app import app

if __name__ == "__main__":
    app_cfg = cfg["app"]
    # Railway (and most PaaS providers) inject PORT; fall back to settings.yaml
    port = int(os.environ.get("PORT", app_cfg["port"]))
    uvicorn.run(
        "backend.api.app:app",
        host="0.0.0.0",
        port=port,
        reload=app_cfg["debug"],
        log_level=cfg["logging"]["level"].lower(),
    )
