import os
import yaml
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Settings:
    base_url: str
    browser: str
    headless: bool
    default_timeout: int
    username: str
    password: str
    env_name: str
    profile_name: str

def load_settings() -> Settings:
    env_name = os.getenv("ENVIRONMENT", "pantera").lower()
    profile_name = os.getenv("PROFILE", "agente").lower()

    config_path = Path(__file__).parent.parent / "config" / "settings.yaml"
    raw = yaml.safe_load(config_path.read_text())

    env_cfg = raw["environments"].get(env_name)
    if not env_cfg:
        raise Exception(f"ENVIRONMENT '{env_name}' no existe en settings.yaml")

    profile_cfg = env_cfg["profiles"].get(profile_name)
    if not profile_cfg:
        raise Exception(f"PROFILE '{profile_name}' no existe en environment '{env_name}'")

    return Settings(
        base_url=env_cfg["base_url"],
        browser=env_cfg["browser"],
        headless=env_cfg["headless"],
        default_timeout=env_cfg["default_timeout"],
        username=profile_cfg["username"],
        password=profile_cfg["password"],
        env_name=env_name,
        profile_name=profile_name,
    )
