#!/usr/bin/env bash
# exit on error
set -o errexit

# Criar pasta static se não existir
mkdir -p static

# Atualizar pip
python -m pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt

# Coletar arquivos estáticos e migrar banco de dados
python manage.py collectstatic --no-input
python manage.py migrate