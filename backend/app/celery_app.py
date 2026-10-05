import os
from celery import Celery

celery = Celery("ore_modeler", broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"), backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"))
