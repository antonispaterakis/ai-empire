import os
from celery import Celery
from celery.schedules import crontab

redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

celery_app = Celery(
    'ai_empire',
    broker=redis_url,
    backend=redis_url,
    include=['tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Example: Schedule daily run at 9 AM UTC
celery_app.conf.beat_schedule = {
    'generate-daily-thread': {
        'task': 'tasks.generate_content',
        'schedule': crontab(hour=9, minute=0),
        'args': ('AI News', True) # topic="AI News", auto_post=True (or False)
    }
}
