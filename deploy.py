#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Deploy Automatizado para Classificador ASCOD/TOAST
"""

import os
import sys
import subprocess
import shutil

def print_header(text):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def check_requirements():
    """Verifica requisitos do sistema"""
    print_header("Verificando Requisitos")
    
    # Verifica Python
    python_version = sys.version_info
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Verifica Git
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        print("✅ Git instalado")
    except:
        print("❌ Git não encontrado. Instale em: https://git-scm.com/")
        return False
    
    return True

def setup_git_repo():
    """Configura repositório Git"""
    print_header("Configurando Repositório Git")
    
    if not os.path.exists(".git"):
        subprocess.run(["git", "init"], check=True)
        print("✅ Repositório Git inicializado")
    
    # Adiciona todos os arquivos
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Deploy ASCOD/TOAST Classifier"], capture_output=True)
    print("✅ Arquivos commitados")
    
    return True

def deploy_render():
    """Deploy no Render"""
    print_header("Deploy no Render")
    
    print("📋 Instruções para deploy no Render:")
    print("1. Crie uma conta em https://render.com")
    print("2. Conecte seu GitHub")
    print("3. Crie um novo Web Service")
    print("4. Use estas configurações:")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: gunicorn app:app")
    print("5. Adicione a variável de ambiente GEMINI_API_KEY")
    print("\n🔗 URL do seu repo: Configure após criar no GitHub")

def deploy_vercel():
    """Deploy no Vercel"""
    print_header("Deploy no Vercel")
    
    print("📋 Para deploy no Vercel:")
    print("1. Instale Vercel CLI: npm i -g vercel")
    print("2. Execute: vercel")
    print("3. Siga as instruções no terminal")
    print("4. Configure GEMINI_API_KEY nas variáveis de ambiente")

def create_docker_compose():
    """Cria docker-compose.yml"""
    compose_content = """version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - FLASK_ENV=production
    volumes:
      - ./templates:/app/templates
      - ./static:/app/static
    restart: unless-stopped
"""
    
    with open("docker-compose.yml", "w") as f:
        f.write(compose_content)
    
    print("✅ docker-compose.yml criado")

def deploy_docker():
    """Deploy com Docker"""
    print_header("Deploy com Docker")
    
    create_docker_compose()
    
    print("📋 Para deploy com Docker:")
    print("1. Instale Docker: https://www.docker.com/")
    print("2. Configure GEMINI_API_KEY no arquivo .env")
    print("3. Execute: docker-compose up -d")
    print("4. Acesse: http://localhost:5000")

def create_windows_batch():
    """Cria arquivo batch para Windows"""
    batch_content = """@echo off
echo ====================================
echo  ASCOD/TOAST Classifier - Iniciando
echo ====================================
echo.

REM Verifica se a chave API está configurada
if "%GEMINI_API_KEY%"=="" (
    echo [AVISO] GEMINI_API_KEY nao configurada!
    echo Configure com: set GEMINI_API_KEY=sua_chave_aqui
    echo.
)

REM Inicia o servidor
echo Iniciando servidor...
python app.py

pause
"""
    
    with open("start_server.bat", "w") as f:
        f.write(batch_content)
    
    print("✅ start_server.bat criado")

def create_deployment_package():
    """Cria pacote de deployment"""
    print_header("Criando Pacote de Deployment")
    
    # Cria diretório de deploy
    deploy_dir = "ascod_toast_deploy"
    if os.path.exists(deploy_dir):
        shutil.rmtree(deploy_dir)
    os.makedirs(deploy_dir)
    
    # Copia arquivos necessários
    files_to_copy = [
        "app.py",
        "ascod_classifier.py",
        "requirements.txt",
        "Procfile",
        "runtime.txt",
        "README.md",
        "Dockerfile",
        "docker-compose.yml",
        "vercel.json",
        ".gitignore"
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, deploy_dir)
    
    # Copia diretórios
    for folder in ["templates", "static"]:
        if os.path.exists(folder):
            shutil.copytree(folder, os.path.join(deploy_dir, folder))
    
    # Cria arquivo zip
    shutil.make_archive("ascod_toast_deploy", 'zip', deploy_dir)
    shutil.rmtree(deploy_dir)
    
    print(f"✅ Pacote criado: ascod_toast_deploy.zip")
    print(f"📍 Localização: {os.path.abspath('ascod_toast_deploy.zip')}")

def main():
    """Função principal"""
    print_header("ASCOD/TOAST Classifier - Deploy Assistant")
    
    if not check_requirements():
        return
    
    # Cria arquivos auxiliares
    create_windows_batch()
    create_docker_compose()
    
    # Menu de opções
    print("\n🚀 Escolha uma opção de deploy:\n")
    print("1. Preparar para Render")
    print("2. Preparar para Vercel")
    print("3. Preparar para Docker")
    print("4. Criar pacote de deployment")
    print("5. Criar executável Windows (.exe)")
    print("6. Preparar todos")
    
    choice = input("\nEscolha (1-6): ")
    
    if choice == "1":
        setup_git_repo()
        deploy_render()
    elif choice == "2":
        deploy_vercel()
    elif choice == "3":
        deploy_docker()
    elif choice == "4":
        create_deployment_package()
    elif choice == "5":
        print("\n🔨 Para criar executável Windows:")
        print("Execute: python build_exe.py")
    elif choice == "6":
        setup_git_repo()
        deploy_render()
        print()
        deploy_vercel()
        print()
        deploy_docker()
        print()
        create_deployment_package()
    
    print("\n✨ Processo concluído!")
    print("\n📚 Documentação completa em README.md")

if __name__ == "__main__":
    main() 