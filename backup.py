# Crie um arquivo chamado backup.py na raiz do projeto com o seguinte conteúdo:
from django.core import management
import json

# Fazer o backup dos dados
data = management.call_command('dumpdata', exclude=['auth.permission', 'contenttypes', 'admin.logentry'], indent=2, natural_foreign=True, natural_primary=True)

# Salvar o arquivo com codificação específica
with open('backups/dados.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)