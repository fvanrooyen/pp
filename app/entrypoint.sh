#!/bin/sh

python manage.py createsuperuser --noinput --email 'pollingplace@gmail.com'
python manage.py collectstatic --no-input

exec "$@"