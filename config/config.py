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

    class TestData:
        VIDEO_URL = "https://cdn.pixabay.com/video/2024/12/17/247208_large.mp4"
        PDF_URL = "https://web.seducoahuila.gob.mx/biblioweb/upload/Frankenstein%20o%20el%20moderno%20Prometeo-libro.pdf"
        IMAGE_URL = "https://cdn.pixabay.com/photo/2025/11/06/16/25/candles-9941198_1280.jpg"
        STATIC_URL = "https://chattigo.com/en/"
        DYNAMIC_URL = "https://chattigo.com/en/agent/"
