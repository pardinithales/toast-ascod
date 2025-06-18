@echo off
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
