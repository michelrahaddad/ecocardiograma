web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --worker-class sync --max-requests 1000 --max-requests-jitter 100 --preload main:app
