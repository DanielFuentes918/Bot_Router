import os
from dotenv import load_dotenv

class Config:
    # Configuraciones desde las variables de entorno
    def __init__(self):
        load_dotenv()
        self.PROD_URL = os.getenv("PROD_URL")  # Webhook de producción
        self.DEV_URL = os.getenv("DEV_URL")  # Webhook de desarrollo
        self.PROD_BOT_PHONENUMBER = os.getenv("PROD_BOT_PHONENUMBER")  # Número de producción
        self.DEV_BOT_PHONENUMBER = os.getenv("DEV_BOT_PHONENUMBER")  # Número de desarrollo
        self.PROD_VERIFY_TOKEN = os.getenv("PROD_VERIFY_TOKEN")  # Verify token para producción
        self.DEV_VERIFY_TOKEN = os.getenv("DEV_VERIFY_TOKEN")  # Verify token para desarrollo
        self.repo_path = os.getenv("repo_path")