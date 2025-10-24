@echo off
echo ========================================
echo  Sistema de Controle de Gastos Pessoais
echo  Universidade Nove de Julho (Uni9)
echo  Autor: Gustavo Cortes de Oliveira
echo ========================================
echo.

REM Verificar se Python esta instalado
echo Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ PYTHON NAO ENCONTRADO!
    echo.
    echo 📥 INSTALE O PYTHON PRIMEIRO:
    echo    1. Acesse: https://www.python.org/downloads/
    echo    2. Baixe Python 3.11 ou 3.12
    echo    3. Durante instalacao MARQUE "Add Python to PATH"
    echo    4. Reinstale e execute este arquivo novamente
    echo.
    echo 💡 ALTERNATIVA: Microsoft Store - procure "Python 3.11"
    echo.
    pause
    exit /b 1
)

echo ✅ Python encontrado!
python --version

REM Verificar pip
echo.
echo Verificando pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip nao encontrado, tentando instalar...
    python -m ensurepip --upgrade
)

echo ✅ pip encontrado!

REM Instalar dependencias
echo.
echo 📦 Instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar dependencias
    echo Execute manualmente: pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✅ Dependencias instaladas!

REM Executar aplicacao
echo.
echo 🚀 Iniciando servidor...
echo.
echo 🌐 Acesse em seu navegador:
echo    http://localhost:5000
echo.
echo 💡 Para parar o servidor: Ctrl+C
echo.
echo ========================================

python run.py

pause