web: gunicorn app:app --timeout 100000 --log-file=-
worker: celery worker --app=tasks.celery --concurrency=1