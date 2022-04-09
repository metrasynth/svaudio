release: django-admin migrate --noinput
web: gunicorn --bind :$PORT --workers 4 --worker-class uvicorn.workers.UvicornWorker config.wsgi:application
worker: celery -A beta-sunvox-audio worker -P prefork --loglevel=INFO
beat: celery -A beta-sunvox-audio beat --loglevel=INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
