"""
Módulo de Machine Learning para previsão de gastos
Sistema Web de Controle de Gastos Pessoais
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import LabelEncoder
import joblib
import os
from datetime import datetime, timedelta
import sqlite3

class PrevisaoGastos:
    def __init__(self, db_path='database/controle_gastos.db'):
        self.db_path = db_path
        self.modelo = LinearRegression()
        self.label_encoder = LabelEncoder()
        self.modelo_treinado = False
        
    def carregar_dados(self):
        """Carrega dados do banco SQLite e prepara para ML"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Query para buscar transações com suas categorias
            query = """
            SELECT t.id, t.descricao, t.valor, t.data, t.tipo, c.nome as categoria
            FROM transacao t
            LEFT JOIN categoria c ON t.categoria_id = c.id
            WHERE t.tipo = 'despesa'
            ORDER BY t.data
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if len(df) == 0:
                return None
            
            # Converter data para datetime
            df['data'] = pd.to_datetime(df['data'])
            
            # Criar features temporais
            df['ano'] = df['data'].dt.year
            df['mes'] = df['data'].dt.month
            df['dia_semana'] = df['data'].dt.dayofweek
            df['dia_mes'] = df['data'].dt.day
            
            # Agrupar por mês para previsão mensal
            df_mensal = df.groupby([df['data'].dt.year, df['data'].dt.month]).agg({
                'valor': 'sum',
                'id': 'count'  # quantidade de transações
            }).reset_index()
            
            df_mensal.columns = ['ano', 'mes', 'total_gastos', 'qtd_transacoes']
            
            # Criar uma coluna de data mensal
            df_mensal['data_mensal'] = pd.to_datetime(df_mensal[['ano', 'mes']].assign(day=1))
            
            # Criar features adicionais
            df_mensal['gastos_por_transacao'] = df_mensal['total_gastos'] / df_mensal['qtd_transacoes']
            
            # Criar lag features (valores dos meses anteriores)
            df_mensal = df_mensal.sort_values('data_mensal')
            df_mensal['gastos_mes_anterior'] = df_mensal['total_gastos'].shift(1)
            df_mensal['gastos_2_meses_antes'] = df_mensal['total_gastos'].shift(2)
            df_mensal['gastos_3_meses_antes'] = df_mensal['total_gastos'].shift(3)
            
            # Média móvel dos últimos 3 meses
            df_mensal['media_3_meses'] = df_mensal['total_gastos'].rolling(window=3).mean()
            
            # Remover linhas com NaN (devido aos lags)
            df_mensal = df_mensal.dropna()
            
            return df_mensal
            
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return None
    
    def treinar_modelo(self):
        """Treina o modelo de previsão"""
        df = self.carregar_dados()
        
        if df is None or len(df) < 4:  # Precisa de pelo menos 4 meses de dados
            print("Dados insuficientes para treinar o modelo (mínimo 4 meses)")
            return False
        
        try:
            # Features para o modelo
            features = [
                'mes', 'qtd_transacoes', 'gastos_por_transacao',
                'gastos_mes_anterior', 'gastos_2_meses_antes', 'gastos_3_meses_antes',
                'media_3_meses'
            ]
            
            X = df[features]
            y = df['total_gastos']
            
            # Dividir dados em treino e teste (80/20)
            if len(df) > 6:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42, shuffle=False
                )
            else:
                # Se poucos dados, usar todos para treino
                X_train, y_train = X, y
                X_test, y_test = None, None
            
            # Treinar modelo
            self.modelo.fit(X_train, y_train)
            
            # Avaliar modelo se temos dados de teste
            if X_test is not None:
                y_pred = self.modelo.predict(X_test)
                mae = mean_absolute_error(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                
                print(f"Modelo treinado com sucesso!")
                print(f"MAE: R$ {mae:.2f}")
                print(f"RMSE: R$ {rmse:.2f}")
            else:
                print("Modelo treinado com dados limitados")
            
            self.modelo_treinado = True
            self.salvar_modelo()
            return True
            
        except Exception as e:
            print(f"Erro ao treinar modelo: {e}")
            return False
    
    def prever_proximo_mes(self):
        """Faz previsão para o próximo mês"""
        if not self.modelo_treinado:
            if not self.carregar_modelo():
                if not self.treinar_modelo():
                    return None
        
        df = self.carregar_dados()
        if df is None or len(df) == 0:
            return None
        
        try:
            # Pegar dados do último mês para criar features
            ultimo_mes = df.iloc[-1]
            
            # Calcular estatísticas dos últimos meses
            ultimos_3_meses = df.tail(3)
            media_qtd_transacoes = ultimos_3_meses['qtd_transacoes'].mean()
            media_gastos_por_transacao = ultimos_3_meses['gastos_por_transacao'].mean()
            
            # Próximo mês
            proxima_data = ultimo_mes['data_mensal'] + pd.DateOffset(months=1)
            proximo_mes = proxima_data.month
            
            # Criar features para previsão
            features_previsao = np.array([[
                proximo_mes,
                media_qtd_transacoes,
                media_gastos_por_transacao,
                ultimo_mes['total_gastos'],  # gastos_mes_anterior
                df.iloc[-2]['total_gastos'] if len(df) > 1 else ultimo_mes['total_gastos'],  # gastos_2_meses_antes
                df.iloc[-3]['total_gastos'] if len(df) > 2 else ultimo_mes['total_gastos'],  # gastos_3_meses_antes
                ultimo_mes['media_3_meses']
            ]])
            
            previsao = self.modelo.predict(features_previsao)[0]
            
            # Adicionar margem de erro (intervalo de confiança simples)
            margem_erro = previsao * 0.15  # 15% de margem
            
            return {
                'previsao': max(0, previsao),  # Não pode ser negativo
                'minimo': max(0, previsao - margem_erro),
                'maximo': previsao + margem_erro,
                'data_previsao': proxima_data.strftime('%Y-%m'),
                'confianca': self._calcular_confianca(df)
            }
            
        except Exception as e:
            print(f"Erro ao fazer previsão: {e}")
            return None
    
    def prever_multiplos_meses(self, num_meses=3):
        """Faz previsão para múltiplos meses"""
        previsoes = []
        
        for i in range(num_meses):
            if i == 0:
                previsao = self.prever_proximo_mes()
            else:
                # Para meses futuros, usar uma abordagem mais simples
                # baseada na tendência dos dados históricos
                df = self.carregar_dados()
                if df is None:
                    break
                
                # Calcular tendência dos últimos 6 meses
                tendencia = self._calcular_tendencia(df)
                previsao_base = previsoes[-1]['previsao'] if previsoes else self.prever_proximo_mes()['previsao']
                
                if previsao_base:
                    previsao_ajustada = previsao_base * (1 + tendencia)
                    margem_erro = previsao_ajustada * 0.2  # Maior margem para meses mais distantes
                    
                    data_base = datetime.now() + timedelta(days=30 * (i + 1))
                    
                    previsao = {
                        'previsao': max(0, previsao_ajustada),
                        'minimo': max(0, previsao_ajustada - margem_erro),
                        'maximo': previsao_ajustada + margem_erro,
                        'data_previsao': data_base.strftime('%Y-%m'),
                        'confianca': max(0.3, 0.8 - (i * 0.15))  # Confiança diminui com o tempo
                    }
                else:
                    break
            
            if previsao:
                previsoes.append(previsao)
        
        return previsoes
    
    def _calcular_confianca(self, df):
        """Calcula nível de confiança baseado na quantidade de dados"""
        num_meses = len(df)
        if num_meses >= 12:
            return 0.9
        elif num_meses >= 6:
            return 0.7
        elif num_meses >= 3:
            return 0.5
        else:
            return 0.3
    
    def _calcular_tendencia(self, df):
        """Calcula tendência de crescimento/decrescimento dos gastos"""
        if len(df) < 3:
            return 0
        
        # Pegar últimos 6 meses ou todos se menos de 6
        ultimos_meses = df.tail(min(6, len(df)))
        
        # Calcular diferença percentual média entre meses consecutivos
        diferencas = []
        for i in range(1, len(ultimos_meses)):
            mes_atual = ultimos_meses.iloc[i]['total_gastos']
            mes_anterior = ultimos_meses.iloc[i-1]['total_gastos']
            if mes_anterior > 0:
                diferenca = (mes_atual - mes_anterior) / mes_anterior
                diferencas.append(diferenca)
        
        return np.mean(diferencas) if diferencas else 0
    
    def salvar_modelo(self):
        """Salva o modelo treinado"""
        try:
            os.makedirs('ml/models', exist_ok=True)
            joblib.dump(self.modelo, 'ml/models/modelo_previsao.pkl')
            print("Modelo salvo com sucesso!")
        except Exception as e:
            print(f"Erro ao salvar modelo: {e}")
    
    def carregar_modelo(self):
        """Carrega modelo previamente treinado"""
        try:
            if os.path.exists('ml/models/modelo_previsao.pkl'):
                self.modelo = joblib.load('ml/models/modelo_previsao.pkl')
                self.modelo_treinado = True
                return True
            return False
        except Exception as e:
            print(f"Erro ao carregar modelo: {e}")
            return False
    
    def analisar_padroes_gastos(self):
        """Analisa padrões nos gastos para insights"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Análise por categoria
            query_categoria = """
            SELECT c.nome as categoria, 
                   AVG(t.valor) as gasto_medio,
                   SUM(t.valor) as gasto_total,
                   COUNT(t.id) as frequencia
            FROM transacao t
            JOIN categoria c ON t.categoria_id = c.id
            WHERE t.tipo = 'despesa'
            GROUP BY c.nome
            ORDER BY gasto_total DESC
            """
            
            df_categoria = pd.read_sql_query(query_categoria, conn)
            
            # Análise por dia da semana
            query_dia_semana = """
            SELECT strftime('%w', t.data) as dia_semana,
                   AVG(t.valor) as gasto_medio,
                   COUNT(t.id) as frequencia
            FROM transacao t
            WHERE t.tipo = 'despesa'
            GROUP BY strftime('%w', t.data)
            """
            
            df_dia_semana = pd.read_sql_query(query_dia_semana, conn)
            
            # Análise por mês
            query_mes = """
            SELECT strftime('%m', t.data) as mes,
                   AVG(t.valor) as gasto_medio,
                   SUM(t.valor) as gasto_total
            FROM transacao t
            WHERE t.tipo = 'despesa'
            GROUP BY strftime('%m', t.data)
            ORDER BY gasto_total DESC
            """
            
            df_mes = pd.read_sql_query(query_mes, conn)
            conn.close()
            
            return {
                'por_categoria': df_categoria.to_dict('records'),
                'por_dia_semana': df_dia_semana.to_dict('records'),
                'por_mes': df_mes.to_dict('records')
            }
            
        except Exception as e:
            print(f"Erro ao analisar padrões: {e}")
            return None

# Função utilitária para usar nas rotas do Flask
def obter_previsao_gastos():
    """Função para ser chamada pelas rotas do Flask"""
    previsao_ml = PrevisaoGastos()
    return previsao_ml.prever_proximo_mes()

def obter_multiplas_previsoes(meses=3):
    """Função para obter previsões de múltiplos meses"""
    previsao_ml = PrevisaoGastos()
    return previsao_ml.prever_multiplos_meses(meses)

def analisar_padroes():
    """Função para análise de padrões"""
    previsao_ml = PrevisaoGastos()
    return previsao_ml.analisar_padroes_gastos()