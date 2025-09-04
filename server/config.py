import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    JSON_COMPACT = False

    REDIS_URL = os.environ.get('REDIS_URL', 'redis://red-d2hmkgv5r7bs738c36ng:6379')

    CELERY = {
        "broker_url": REDIS_URL,
        "result_backend": REDIS_URL,
        "imports": (
            "server.tasks.advance_scraper",
            "server.tasks.oreilly_scraper",
            "server.tasks.get_places",
        ),
        "task_track_started": True,
        "broker_connection_retry_on_startup": True,

        "task_soft_time_limit": os.getenv("CELERY_SOFT_TIME_LIMIT", 150),
        "task_time_limit": os.getenv("CELERY_HARD_TIME_LIMIT", 180),

        "worker_concurrency": os.getenv("CELERY_WORKER_CONCURRENCY", 1),
        "worker_prefetch_multiplier": os.getenv("CELERY_PREFETCH", 1),
    }
