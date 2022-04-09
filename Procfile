release: django-admin migrate --noinput
web: gunicorn --bind :$PORT --workers 4 --worker-class uvicorn.workers.UvicornWorker config.asgi:application
worker: celery -A config.celery_app worker -P prefork --loglevel=INFO
beat: celery -A config.celery_app beat --loglevel=INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
