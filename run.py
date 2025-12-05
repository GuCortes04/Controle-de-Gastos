#!/usr/bin/env python3
"""
Sistema Web de Controle de Gastos Pessoais com Previsão Inteligente
Autor: Gustavo Cortes de Oliveira
Universidade Nove de Julho (Uni9)

Arquivo principal para inicializar o sistema
"""

import os
import sys
import subprocess
from pathlib import Path

def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    try:
        import flask
        import flask_sqlalchemy
        import sklearn
        import pandas
        import numpy
        print("✓ Todas as dependências estão instaladas")
        return True
    except ImportError as e:
        print(f"✗ Dependência faltando: {e}")
        print("Execute: pip install -r requirements.txt")
        return False

def inicializar_estrutura():
    """Inicializa a estrutura de diretórios necessária"""
    diretorios = [
        'database',
        'ml/models',
        'frontend/static/css',
        'frontend/static/js',
        'frontend/templates',
        'tests',
        'docs'
    ]
    
    for diretorio in diretorios:
        Path(diretorio).mkdir(parents=True, exist_ok=True)
        print(f"✓ Diretório {diretorio} criado/verificado")

def executar_aplicacao():
    """Executa a aplicação Flask"""
    print("\n" + "="*50)
    print("SISTEMA WEB DE CONTROLE DE GASTOS PESSOAIS")
    print("="*50)
    print("Autor: Gustavo Cortes de Oliveira")
    print("Instituição: Universidade Nove de Julho (Uni9)")
    print("="*50)
    
    # Verificar dependências
    if not verificar_dependencias():
        return False
    
    # Inicializar estrutura
    inicializar_estrutura()
    
    # Mudar para o diretório backend
    backend_dir = Path(__file__).parent / 'backend'
    os.chdir(backend_dir)
    
    print("\n🚀 Iniciando servidor Flask...")
    print("📊 Dashboard disponível em: http://localhost:5000")
    print("💰 Gerenciar transações: http://localhost:5000/transacoes")
    print("📈 Analytics: http://localhost:5000/dashboard")
    print("\nPressione Ctrl+C para parar o servidor")
    print("-"*50)
    
    try:
        # Importar e executar a aplicação
        from app import app, init_database
        
        # Inicializar banco de dados
        with app.app_context():
            init_database()
            print("✓ Banco de dados inicializado")
        
        # Executar aplicação
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n\n👋 Servidor interrompido pelo usuário")
        return True
    except Exception as e:
        print(f"\n❌ Erro ao executar aplicação: {e}")
        return False

def mostrar_ajuda():
    """Mostra informações de ajuda"""
    print("""
Sistema Web de Controle de Gastos Pessoais
==========================================

Uso: python run.py [opção]

Opções:
  --help, -h     Mostra esta ajuda
  --setup        Instala dependências
  --test         Executa testes
  --docs         Gera documentação

Sem argumentos: Executa a aplicação

Funcionalidades:
• CRUD completo para receitas e despesas
• Dashboard com gráficos interativos
• Classificação automática de categorias
• Previsão de gastos com Machine Learning
• Interface web responsiva com Bootstrap

Tecnologias:
• Backend: Python Flask + SQLAlchemy
• Frontend: HTML5 + Bootstrap + Chart.js
• ML: Scikit-learn + Pandas
• Banco: SQLite
    """)

def instalar_dependencias():
    """Instala as dependências do projeto"""
    print("📦 Instalando dependências...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✓ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def executar_testes():
    """Executa os testes do sistema"""
    print("🧪 Executando testes...")
    # Implementar testes futuramente
    print("⚠️  Testes ainda não implementados")

if __name__ == '__main__':
    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['--help', '-h']:
            mostrar_ajuda()
        elif arg == '--setup':
            instalar_dependencias()
        elif arg == '--test':
            executar_testes()
        elif arg == '--docs':
            print("📚 Documentação em desenvolvimento...")
        else:
            print(f"❌ Argumento desconhecido: {arg}")
            print("Use --help para ver as opções disponíveis")
    else:
        # Executar aplicação normalmente
        executar_aplicacao()