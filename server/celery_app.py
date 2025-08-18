import os, ssl
from celery import Celery
from kombu import Queue
from server.config import Config
from server.app import create_app



def create_celery(app):
    celery = Celery(app.import_name)

    celery.config_from_object(app.config, namespace="CELERY")

    redis_url = app.config.get("CELERY_BROKER_URL") or os.getenv("REDIS_URL", "")
    if redis_url.startswith("rediss://"):
        celery.conf.broker_use_ssl = {"ssl_cert_reqs": ssl.CERT_NONE}
        celery.conf.redis_backend_use_ssl = {"ssl_cert_reqs": ssl.CERT_NONE}
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    return celery

flask_app = create_app()
celery = create_celery(flask_app)