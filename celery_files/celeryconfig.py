from celery import Celery
from celery.schedules import crontab

celery = Celery(
    "tasks",
    broker="amqp://guest@localhost:5672//",
    backend="rpc://"
)

celery.conf.beat_schedule = {
    'run-every-hour': {
        'task': 'celery_files.tasks.hourly_task',
        'schedule': crontab(minute=0),
    }
}