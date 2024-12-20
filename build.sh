#!/usr/bin/env bash
# exit on error
set -o errexit

# Instalar dependências
pip install -r requirements.txt

# Criar diretório static se não existir
mkdir -p static

# Limpar migrações existentes (opcional, use com cautela)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Fazer migrações do zero
python manage.py makemigrations core
python manage.py migrate core zero
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --no-input