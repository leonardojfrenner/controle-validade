#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Criar diretório static se não existir
mkdir -p static

python manage.py migrate --noinput
python manage.py collectstatic --no-input