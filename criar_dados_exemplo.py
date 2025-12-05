"""
Script para popular o banco de dados com dados de exemplo
Para fins de teste e demonstração do sistema
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Adicionar o caminho do backend ao sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def criar_dados_exemplo():
    """Cria dados de exemplo para demonstração"""
    try:
        from app import app, db, Categoria, Transacao
        import json
        
        with app.app_context():
            # Verificar se já existem dados
            if Transacao.query.count() > 0:
                print("⚠️  Banco já possui dados. Execute apenas uma vez.")
                return
            
            print("🔄 Criando dados de exemplo...")
            
            # Buscar categorias existentes
            categorias = {cat.nome: cat.id for cat in Categoria.query.all()}
            
            # Dados de exemplo para transações
            exemplos_transacoes = [
                # Alimentação
                ("Supermercado Extra", "despesa", "Alimentação", lambda: random.uniform(80, 150)),
                ("Restaurante Japonês", "despesa", "Alimentação", lambda: random.uniform(45, 80)),
                ("iFood - Pizza", "despesa", "Alimentação", lambda: random.uniform(25, 45)),
                ("Padaria do Bairro", "despesa", "Alimentação", lambda: random.uniform(8, 20)),
                ("Mercado Carrefour", "despesa", "Alimentação", lambda: random.uniform(90, 180)),
                ("Lanche McDonald's", "despesa", "Alimentação", lambda: random.uniform(15, 30)),
                
                # Transporte
                ("Uber para trabalho", "despesa", "Transporte", lambda: random.uniform(12, 25)),
                ("Gasolina Posto Shell", "despesa", "Transporte", lambda: random.uniform(60, 120)),
                ("Bilhete Único", "despesa", "Transporte", lambda: random.uniform(20, 40)),
                ("Estacionamento Shopping", "despesa", "Transporte", lambda: random.uniform(8, 15)),
                
                # Moradia
                ("Aluguel Apartamento", "despesa", "Moradia", lambda: 1200),
                ("Conta de Luz - CPFL", "despesa", "Moradia", lambda: random.uniform(80, 150)),
                ("Conta de Água - SABESP", "despesa", "Moradia", lambda: random.uniform(45, 80)),
                ("Internet Vivo Fibra", "despesa", "Moradia", lambda: 89.90),
                ("Condomínio", "despesa", "Moradia", lambda: 320),
                
                # Saúde
                ("Farmácia Droga Raia", "despesa", "Saúde", lambda: random.uniform(25, 60)),
                ("Consulta Médica", "despesa", "Saúde", lambda: random.uniform(150, 300)),
                ("Plano de Saúde Unimed", "despesa", "Saúde", lambda: 280),
                ("Academia Smart Fit", "despesa", "Saúde", lambda: 79.90),
                
                # Lazer
                ("Cinema Cinemark", "despesa", "Lazer", lambda: random.uniform(18, 35)),
                ("Netflix Assinatura", "despesa", "Lazer", lambda: 25.90),
                ("Viagem - Hotel", "despesa", "Lazer", lambda: random.uniform(200, 500)),
                ("Bar com Amigos", "despesa", "Lazer", lambda: random.uniform(40, 100)),
                
                # Vestuário
                ("Loja Renner", "despesa", "Vestuário", lambda: random.uniform(60, 200)),
                ("Tênis Nike", "despesa", "Vestuário", lambda: random.uniform(200, 400)),
                ("Calça Jeans", "despesa", "Vestuário", lambda: random.uniform(80, 150)),
                
                # Educação
                ("Curso Online Udemy", "despesa", "Educação", lambda: random.uniform(30, 80)),
                ("Livros Amazon", "despesa", "Educação", lambda: random.uniform(40, 120)),
                
                # Receitas
                ("Salário", "receita", None, lambda: 3500),
                ("Freelance Desenvolvemento", "receita", None, lambda: random.uniform(500, 1200)),
                ("Rendimento Poupança", "receita", None, lambda: random.uniform(15, 35)),
            ]
            
            # Criar transações para os últimos 6 meses
            data_atual = datetime.now().date()
            
            for i in range(6):  # 6 meses
                mes_base = data_atual.replace(day=1) - timedelta(days=30*i)
                
                # Para cada mês, criar várias transações
                for _ in range(random.randint(15, 30)):  # 15-30 transações por mês
                    # Escolher uma transação de exemplo aleatória
                    desc_base, tipo, categoria_nome, valor_func = random.choice(exemplos_transacoes)
                    
                    # Gerar data aleatória no mês
                    dia = random.randint(1, 28)
                    data_transacao = mes_base.replace(day=dia)
                    
                    # Adicionar variação na descrição
                    if random.random() < 0.3:  # 30% de chance de variação
                        desc_base += f" - {random.choice(['Centro', 'Shopping', 'Online', 'Promoção'])}"
                    
                    # Obter categoria ID se aplicável
                    categoria_id = None
                    if categoria_nome and categoria_nome in categorias:
                        categoria_id = categorias[categoria_nome]
                    
                    # Criar transação
                    transacao = Transacao(
                        descricao=desc_base,
                        valor=round(valor_func(), 2),
                        data=data_transacao,
                        tipo=tipo,
                        categoria_id=categoria_id
                    )
                    
                    db.session.add(transacao)
            
            # Salvar no banco
            db.session.commit()
            
            # Estatísticas
            total_transacoes = Transacao.query.count()
            total_receitas = db.session.query(db.func.sum(Transacao.valor)).filter_by(tipo='receita').scalar() or 0
            total_despesas = db.session.query(db.func.sum(Transacao.valor)).filter_by(tipo='despesa').scalar() or 0
            
            print(f"✅ Dados de exemplo criados com sucesso!")
            print(f"📊 Estatísticas:")
            print(f"   • Total de transações: {total_transacoes}")
            print(f"   • Total de receitas: R$ {total_receitas:.2f}")
            print(f"   • Total de despesas: R$ {total_despesas:.2f}")
            print(f"   • Saldo: R$ {(total_receitas - total_despesas):.2f}")
            print()
            print("🚀 Agora você pode testar:")
            print("   • Dashboard com gráficos")
            print("   • Classificação automática")
            print("   • Previsão de gastos (ML)")
            print("   • Análise de padrões")
            
    except Exception as e:
        print(f"❌ Erro ao criar dados de exemplo: {e}")

if __name__ == '__main__':
    criar_dados_exemplo()