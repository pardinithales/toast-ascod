#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar executável standalone do Classificador ASCOD/TOAST
"""

import os
import sys
import shutil
import subprocess

def create_executable():
    """Cria o executável usando PyInstaller"""
    
    print("🔨 Preparando para criar executável...")
    
    # Instala PyInstaller se não estiver instalado
    try:
        import PyInstaller
    except ImportError:
        print("📦 Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Cria o arquivo spec personalizado
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('ascod_classifier.py', '.'),
    ],
    hiddenimports=[
        'flask',
        'flask_cors',
        'requests',
        'json',
        'os',
        'sys'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ASCOD_TOAST_Classifier',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None
)
'''
    
    # Salva o arquivo spec
    with open('ascod_classifier.spec', 'w') as f:
        f.write(spec_content.strip())
    
    print("📝 Arquivo spec criado...")
    
    # Executa PyInstaller
    print("🚀 Criando executável...")
    subprocess.check_call([
        sys.executable, 
        "-m", 
        "PyInstaller",
        "--clean",
        "--noconfirm",
        "ascod_classifier.spec"
    ])
    
    # Copia o executável para a raiz
    exe_path = os.path.join("dist", "ASCOD_TOAST_Classifier.exe")
    if os.path.exists(exe_path):
        shutil.copy2(exe_path, "ASCOD_TOAST_Classifier.exe")
        print(f"✅ Executável criado com sucesso: ASCOD_TOAST_Classifier.exe")
        print(f"📍 Localização: {os.path.abspath('ASCOD_TOAST_Classifier.exe')}")
    else:
        print("❌ Erro ao criar executável")
        return False
    
    # Limpa arquivos temporários
    print("🧹 Limpando arquivos temporários...")
    for folder in ['build', 'dist', '__pycache__']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    
    if os.path.exists('ascod_classifier.spec'):
        os.remove('ascod_classifier.spec')
    
    print("\n✨ Processo concluído!")
    print("\n📋 Instruções de uso:")
    print("1. Execute ASCOD_TOAST_Classifier.exe")
    print("2. Acesse http://localhost:5000 no navegador")
    print("3. Configure a variável GEMINI_API_KEY se necessário")
    
    return True

if __name__ == "__main__":
    create_executable() 