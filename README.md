# Controle de Validade - Sistema para Farmácias

## 📋 Sobre o Projeto

O Controle de Validade é um sistema web desenvolvido em Django para auxiliar farmácias no gerenciamento e controle de validade dos seus produtos. O sistema permite que as farmácias monitorem de forma eficiente os prazos de validade dos medicamentos e produtos, evitando perdas e garantindo a segurança dos clientes.

## 🚀 Funcionalidades

- Cadastro e gerenciamento de produtos
- Controle de datas de validade
- Dashboard com visão geral dos produtos
- Sistema de alertas para produtos próximos ao vencimento
- Autenticação personalizada para farmácias
- Interface em português do Brasil
- Sistema responsivo e seguro

## 🔧 Tecnologias Utilizadas

- Python
- Django
- PostgreSQL (Produção)
- SQLite (Desenvolvimento)
- WhiteNoise para arquivos estáticos
- Sistema de emails com SMTP
- Deploy na plataforma Render

## 💻 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)
- Virtualenv (recomendado)

## 🛠️ Instalação e Configuração

1. Clone o repositório:
``
git clone https://github.com/seu-usuario/controle-validade.git ``


## 🌐 Uso

1. Acesse o sistema através do navegador: `http://localhost:8000`
2. Faça login com suas credenciais de farmácia
3. Utilize o dashboard para gerenciar seus produtos e controlar as validades

## 🔒 Configurações de Segurança

O sistema possui configurações de segurança específicas para ambiente de produção:
- SSL/HTTPS forçado
- Cookies seguros
- Proteção contra XSS
- Headers de segurança configurados

## 📧 Configuração de Email

O sistema utiliza SMTP do Gmail para envio de emails. Para configurar:
1. Ative a autenticação de duas etapas no Gmail
2. Gere uma senha de aplicativo
3. Use estas credenciais nas variáveis de ambiente

## 🚀 Deploy

O projeto está configurado para deploy na plataforma Render. Para fazer o deploy:
1. Crie uma conta no Render
2. Configure um novo Web Service
3. Conecte com seu repositório Git
4. Configure as variáveis de ambiente necessárias
