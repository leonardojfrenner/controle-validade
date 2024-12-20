#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Limpar migrações existentes (opcional, use com cuidado)
# find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

python manage.py makemigrations
python manage.py migrate --noinput
python manage.py collectstatic --no-input