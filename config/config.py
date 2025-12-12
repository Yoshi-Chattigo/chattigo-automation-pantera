import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ENVIRONMENTS = {
        "pantera": "https://qa-pantera.chattigo.com/login/pages/login",
        "bugs": "https://qa-bugs.chattigo.com/login/pages/login",
        "support-bugs": "https://qa-support-bugs.chattigo.com/login/pages/login",
        "leones": "https://qa-leones.chattigo.com/login/pages/login"
    }
    
    # Default to pantera if not set
    BASE_URL = os.getenv("BASE_URL", ENVIRONMENTS["pantera"])
    USERNAME = os.getenv("USERNAME", "agente@auto.com")
    PASSWORD = os.getenv("PASSWORD", "Admin1234.")
    TIMEOUT = int(os.getenv("TIMEOUT", 10000))
    HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"
