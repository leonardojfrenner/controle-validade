#!/usr/bin/env bash
# exit on error
set -o errexit

# Atualizar pip
python -m pip install --upgrade pip

# Limpar cache e arquivos temporários
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete
rm -rf .pytest_cache .coverage htmlcov .tox || true

# Remover e recriar ambiente virtual (opcional)
rm -rf .venv || true
python -m venv .venv
source .venv/bin/activate

# Instalar dependências
pip install --no-cache-dir -r requirements.txt

# Criar diretório static se não existir
mkdir -p static

# Limpar migrações existentes
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Reinstalar Django explicitamente
pip uninstall django -y
pip install django==5.1.4

# Fazer migrações
python manage.py makemigrations
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --no-input

echo "Build completed successfully!"