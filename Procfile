release: python manage.py migrate --no-input
web: gunicorn job_bilby.wsgi --log-file -
