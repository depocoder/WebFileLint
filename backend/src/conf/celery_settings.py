from django.conf import settings

CELERY_BROKER_URL = f"amqp://{settings.AMQP_HOST}:5672"
CELERY_BEAT_SCHEDULE = {
    "check_linter_every_minute": {
        "task": "checker.tasks.regular_checking",
        "schedule": 60,
    },
}
CELERY_TIMEZONE = "Europe/Moscow"
