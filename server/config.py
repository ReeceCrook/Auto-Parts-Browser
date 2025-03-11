import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    JSON_COMPACT = False
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_IMPORTS = ("server.tasks.advance_scraper", "server.tasks.oreilly_scraper", "server.tasks.get_places",)
    broker_connection_retry_on_startup = True
    CELERY_TRACK_STARTED=True