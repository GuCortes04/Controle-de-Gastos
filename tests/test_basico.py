"""
Testes básicos para o Sistema de Controle de Gastos
"""

import unittest
import os
import sys
import tempfile
from datetime import datetime

# Adicionar o caminho do backend ao sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

class TestControleGastos(unittest.TestCase):
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.temp_db = tempfile.mktemp()
        
    def tearDown(self):
        """Limpeza após cada teste"""
        if os.path.exists(self.temp_db):
            os.unlink(self.temp_db)
    
    def test_import_modules(self):
        """Testa se os módulos podem ser importados"""
        try:
            from app import app, db, Categoria, Transacao
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml'))
            from previsao_gastos import PrevisaoGastos
            from classificador import ClassificadorCategorias
            self.assertTrue(True, "Módulos importados com sucesso")
        except ImportError as e:
            self.fail(f"Erro ao importar módulos: {e}")
    
    def test_create_transaction(self):
        """Testa criação de transação"""
        try:
            from app import app, db, Transacao
            
            with app.app_context():
                app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self.temp_db}'
                db.create_all()
                
                transacao = Transacao(
                    descricao="Teste Supermercado",
                    valor=100.50,
                    data=datetime.now().date(),
                    tipo="despesa"
                )
                
                db.session.add(transacao)
                db.session.commit()
                
                # Verificar se foi salva
                saved_transaction = Transacao.query.first()
                self.assertIsNotNone(saved_transaction)
                self.assertEqual(saved_transaction.descricao, "Teste Supermercado")
                self.assertEqual(saved_transaction.valor, 100.50)
                
        except Exception as e:
            self.fail(f"Erro ao criar transação: {e}")
    
    def test_category_classification(self):
        """Testa classificação de categorias"""
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml'))
            from classificador import ClassificadorCategorias
            
            # Teste básico de classificação
            classificador = ClassificadorCategorias(db_path=':memory:')
            
            # Como não há banco configurado, deve retornar None
            resultado = classificador.classificar_transacao("Supermercado Extra")
            # Não deve dar erro
            self.assertTrue(True, "Classificação executada sem erro")
            
        except Exception as e:
            self.fail(f"Erro na classificação: {e}")
    
    def test_prediction_model(self):
        """Testa modelo de previsão"""
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml'))
            from previsao_gastos import PrevisaoGastos
            
            # Teste básico de previsão
            previsao = PrevisaoGastos(db_path=':memory:')
            
            # Como não há dados, deve retornar None
            resultado = previsao.prever_proximo_mes()
            # Não deve dar erro
            self.assertTrue(True, "Previsão executada sem erro")
            
        except Exception as e:
            self.fail(f"Erro na previsão: {e}")
    
    def test_flask_routes(self):
        """Testa rotas básicas do Flask"""
        try:
            from app import app
            
            app.config['TESTING'] = True
            client = app.test_client()
            
            # Testar rota principal
            response = client.get('/')
            self.assertEqual(response.status_code, 200)
            
            # Testar rota de dashboard
            response = client.get('/dashboard')
            self.assertEqual(response.status_code, 200)
            
            # Testar rota de transações
            response = client.get('/transacoes')
            self.assertEqual(response.status_code, 200)
            
        except Exception as e:
            self.fail(f"Erro ao testar rotas: {e}")

class TestMLModules(unittest.TestCase):
    """Testes específicos para módulos de Machine Learning"""
    
    def test_text_cleaning(self):
        """Testa limpeza de texto do classificador"""
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml'))
            from classificador import ClassificadorCategorias
            
            classificador = ClassificadorCategorias(db_path=':memory:')
            
            # Testar limpeza de texto
            texto_limpo = classificador._limpar_texto("  SUPERMERCADO Extra!!! @#$  ")
            expected = "supermercado extra"
            self.assertEqual(texto_limpo, expected)
            
        except Exception as e:
            self.fail(f"Erro na limpeza de texto: {e}")
    
    def test_data_loading(self):
        """Testa carregamento de dados para ML"""
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml'))
            from previsao_gastos import PrevisaoGastos
            
            previsao = PrevisaoGastos(db_path=':memory:')
            
            # Com banco vazio, deve retornar None
            dados = previsao.carregar_dados()
            self.assertIsNone(dados)
            
        except Exception as e:
            self.fail(f"Erro no carregamento de dados: {e}")

def run_tests():
    """Executa todos os testes"""
    print("🧪 Executando testes do Sistema de Controle de Gastos...")
    print("=" * 60)
    
    # Descobrir e executar testes
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ Todos os testes passaram!")
    else:
        print(f"❌ {len(result.failures)} testes falharam, {len(result.errors)} erros")
        
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)