from pathlib import Path
from functools import lru_cache
import yaml

_CONFIG_DIR = Path(__file__).parent.parent / "config"


@lru_cache(maxsize=None)
def load_settings() -> dict:
    with open(_CONFIG_DIR / "settings.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


@lru_cache(maxsize=None)
def load_prior_sources() -> dict:
    with open(_CONFIG_DIR / "prior_sources.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)
