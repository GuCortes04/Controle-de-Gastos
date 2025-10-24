@echo off
echo ========================================
echo   INSTALAR PYTHON - CONTROLE DE GASTOS
echo ========================================
echo.
echo Este script ajuda a instalar Python no Windows
echo.

REM Verificar se ja esta instalado
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python ja esta instalado!
    python --version
    echo.
    echo Execute EXECUTAR.bat para rodar o sistema
    pause
    exit /b 0
)

echo 📥 OPCOES DE INSTALACAO:
echo.
echo 1. DOWNLOAD OFICIAL (Recomendado)
echo    - Acesse: https://www.python.org/downloads/
echo    - Baixe Python 3.11 ou 3.12
echo    - IMPORTANTE: Marque "Add Python to PATH"
echo.
echo 2. MICROSOFT STORE (Mais facil)
echo    - Abra Microsoft Store
echo    - Procure "Python 3.11"
echo    - Clique Instalar
echo.
echo 3. WINGET (Se disponivel)
echo.

set /p opcao="Escolha opcao (1, 2 ou 3): "

if "%opcao%"=="1" (
    echo.
    echo Abrindo site oficial do Python...
    start https://www.python.org/downloads/
    echo.
    echo ⚠️  INSTRUCOES IMPORTANTES:
    echo    1. Baixe a versao mais recente
    echo    2. Durante instalacao MARQUE "Add Python to PATH"
    echo    3. Use "Customize installation" se necessario
    echo    4. Apos instalar, execute EXECUTAR.bat
    echo.
)

if "%opcao%"=="2" (
    echo.
    echo Abrindo Microsoft Store...
    start ms-windows-store://search/?query=python
    echo.
    echo ⚠️  INSTRUCOES:
    echo    1. Procure "Python 3.11" ou "Python 3.12"
    echo    2. Clique em "Instalar"
    echo    3. Aguarde instalacao completar
    echo    4. Apos instalar, execute EXECUTAR.bat
    echo.
)

if "%opcao%"=="3" (
    echo.
    echo Tentando instalar via winget...
    winget install Python.Python.3.11
    if %errorlevel% neq 0 (
        echo ❌ Winget nao disponivel, use opcao 1 ou 2
    ) else (
        echo ✅ Python instalado via winget!
    )
    echo.
)

echo.
echo 📋 APOS INSTALAR PYTHON:
echo    1. Feche este terminal
echo    2. Abra novo PowerShell ou cmd
echo    3. Execute: EXECUTAR.bat
echo    4. Ou digite: python run.py
echo.
echo 🎯 VERIFICAR INSTALACAO:
echo    python --version
echo    pip --version
echo.

pause