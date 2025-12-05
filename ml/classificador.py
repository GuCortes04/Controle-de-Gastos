"""
Módulo de classificação automática de categorias
Sistema Web de Controle de Gastos Pessoais
"""

import re
import json
import sqlite3
from difflib import SequenceMatcher

class ClassificadorCategorias:
    def __init__(self, db_path='database/controle_gastos.db'):
        self.db_path = db_path
        self.categorias = self._carregar_categorias()
        
        # Palavras-chave mais específicas para melhorar a classificação
        self.palavras_especificas = {
            'Alimentação': [
                'supermercado', 'mercado', 'hipermercado', 'extra', 'carrefour', 'pão de açúcar',
                'restaurante', 'lanchonete', 'pizzaria', 'hamburgueria', 'comida', 'lanche',
                'padaria', 'açougue', 'hortifruti', 'verdura', 'fruta', 'carne', 'peixe',
                'ifood', 'uber eats', 'delivery', 'entrega', 'marmita', 'buffet',
                'café', 'cafeteria', 'bar', 'pub', 'cerveja', 'bebida', 'refrigerante'
            ],
            'Transporte': [
                'uber', 'taxi', 'cabify', '99', 'combustível', 'gasolina', 'etanol', 'diesel',
                'ônibus', 'metro', 'metrô', 'trem', 'cptm', 'bilhete único', 'vale transporte',
                'estacionamento', 'zona azul', 'pedágio', 'multa', 'ipva', 'licenciamento',
                'mecânico', 'oficina', 'pneu', 'óleo', 'revisão', 'lavagem', 'carro',
                'moto', 'bicicleta', 'patinete', 'viagem', 'passagem', 'avião', 'rodoviária'
            ],
            'Moradia': [
                'aluguel', 'condomínio', 'água', 'luz', 'energia elétrica', 'gás', 'internet',
                'telefone', 'celular', 'tv', 'streaming', 'netflix', 'amazon prime',
                'seguro residencial', 'iptu', 'reforma', 'pintura', 'eletricista', 'encanador',
                'móveis', 'decoração', 'limpeza', 'faxina', 'produto de limpeza',
                'manutenção', 'portaria', 'zelador', 'administradora'
            ],
            'Saúde': [
                'farmácia', 'drogaria', 'remédio', 'medicamento', 'genérico',
                'médico', 'consulta', 'particular', 'convênio', 'plano de saúde',
                'dentista', 'ortodontia', 'aparelho', 'limpeza dental',
                'exame', 'laboratorio', 'raio-x', 'ultrassom', 'ressonância',
                'hospital', 'pronto socorro', 'emergência', 'cirurgia',
                'fisioterapia', 'psicólogo', 'terapia', 'academia', 'exercício'
            ],
            'Lazer': [
                'cinema', 'filme', 'teatro', 'show', 'concerto', 'festival',
                'viagem', 'hotel', 'pousada', 'hospedagem', 'turismo',
                'festa', 'balada', 'clube', 'diversão', 'entretenimento',
                'parque', 'zoológico', 'museu', 'exposição', 'evento',
                'jogo', 'videogame', 'steam', 'playstation', 'xbox',
                'livro', 'revista', 'jornal', 'spotify', 'youtube premium'
            ],
            'Educação': [
                'curso', 'faculdade', 'universidade', 'escola', 'colégio',
                'mensalidade', 'matrícula', 'material escolar', 'livro didático',
                'curso online', 'udemy', 'coursera', 'alura', 'treinamento',
                'certificação', 'prova', 'vestibular', 'enem', 'concurso',
                'idioma', 'inglês', 'espanhol', 'francês', 'alemão',
                'papelaria', 'caneta', 'caderno', 'mochila'
            ],
            'Vestuário': [
                'roupa', 'calça', 'camisa', 'camiseta', 'blusa', 'vestido',
                'sapato', 'tênis', 'sandália', 'bota', 'chinelo',
                'underwear', 'calcinha', 'sutiã', 'cueca', 'meia',
                'casaco', 'jaqueta', 'agasalho', 'short', 'bermuda',
                'acessório', 'bolsa', 'carteira', 'relógio', 'óculos',
                'loja', 'shopping', 'outlet', 'promoção', 'desconto',
                'lavanderia', 'lavagem a seco', 'costureira', 'ajuste'
            ],
            'Trabalho': [
                'material de escritório', 'notebook', 'computador', 'mouse', 'teclado',
                'impressora', 'papel', 'tinta', 'caneta', 'lápis',
                'software', 'licença', 'microsoft office', 'adobe',
                'coworking', 'escritório', 'aluguel comercial',
                'contador', 'contabilidade', 'imposto', 'darf',
                'viagem de trabalho', 'reembolso', 'combustível trabalho'
            ],
            'Investimento': [
                'aplicação', 'investimento', 'poupança', 'cdb', 'lci', 'lca',
                'tesouro direto', 'ação', 'fundo', 'previdência',
                'corretora', 'taxa de corretagem', 'custódia',
                'bitcoin', 'criptomoeda', 'ethereum', 'exchange'
            ]
        }
    
    def _carregar_categorias(self):
        """Carrega categorias do banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, palavras_chave FROM categoria")
            categorias = {}
            
            for row in cursor.fetchall():
                categoria_id, nome, palavras_chave_json = row
                palavras_chave = json.loads(palavras_chave_json) if palavras_chave_json else []
                categorias[categoria_id] = {
                    'nome': nome,
                    'palavras_chave': palavras_chave
                }
            
            conn.close()
            return categorias
        except Exception as e:
            print(f"Erro ao carregar categorias: {e}")
            return {}
    
    def classificar_transacao(self, descricao):
        """
        Classifica uma transação baseada na descrição
        Retorna o ID da categoria mais provável
        """
        if not descricao:
            return None
        
        descricao_limpa = self._limpar_texto(descricao)
        
        # Buscar por correspondência exata de palavras-chave
        categoria_id = self._buscar_correspondencia_exata(descricao_limpa)
        if categoria_id:
            return categoria_id
        
        # Buscar por similaridade de texto
        categoria_id = self._buscar_por_similaridade(descricao_limpa)
        if categoria_id:
            return categoria_id
        
        # Usar palavras-chave específicas mais abrangentes
        categoria_id = self._buscar_palavras_especificas(descricao_limpa)
        if categoria_id:
            return categoria_id
        
        # Se não encontrou nada, tentar aprender com transações similares
        categoria_id = self._aprender_de_historico(descricao_limpa)
        if categoria_id:
            return categoria_id
        
        return None  # Não classificado
    
    def _limpar_texto(self, texto):
        """Limpa e normaliza o texto para classificação"""
        # Converter para minúsculas
        texto = texto.lower().strip()
        
        # Remover caracteres especiais, manter apenas letras, números e espaços
        texto = re.sub(r'[^\w\s]', ' ', texto)
        
        # Remover espaços extras
        texto = re.sub(r'\s+', ' ', texto)
        
        return texto
    
    def _buscar_correspondencia_exata(self, descricao):
        """Busca correspondência exata com palavras-chave das categorias"""
        for categoria_id, categoria_info in self.categorias.items():
            palavras_chave = categoria_info['palavras_chave']
            
            for palavra in palavras_chave:
                if palavra.lower() in descricao:
                    return categoria_id
        
        return None
    
    def _buscar_palavras_especificas(self, descricao):
        """Busca usando palavras-chave específicas mais abrangentes"""
        pontuacoes = {}
        
        for nome_categoria, palavras in self.palavras_especificas.items():
            pontuacao = 0
            palavras_encontradas = 0
            
            for palavra in palavras:
                if palavra.lower() in descricao:
                    pontuacao += len(palavra)  # Palavras maiores têm mais peso
                    palavras_encontradas += 1
            
            if palavras_encontradas > 0:
                # Normalizar pontuação pela quantidade de palavras encontradas
                pontuacoes[nome_categoria] = pontuacao * palavras_encontradas
        
        if pontuacoes:
            # Retornar categoria com maior pontuação
            melhor_categoria = max(pontuacoes, key=pontuacoes.get)
            
            # Encontrar ID da categoria pelo nome
            for categoria_id, categoria_info in self.categorias.items():
                if categoria_info['nome'] == melhor_categoria:
                    return categoria_id
        
        return None
    
    def _buscar_por_similaridade(self, descricao):
        """Busca por similaridade de texto usando SequenceMatcher"""
        melhor_similaridade = 0
        melhor_categoria = None
        
        for categoria_id, categoria_info in self.categorias.items():
            palavras_chave = categoria_info['palavras_chave']
            
            for palavra in palavras_chave:
                similaridade = SequenceMatcher(None, descricao, palavra.lower()).ratio()
                
                if similaridade > melhor_similaridade and similaridade > 0.6:  # 60% de similaridade mínima
                    melhor_similaridade = similaridade
                    melhor_categoria = categoria_id
        
        return melhor_categoria
    
    def _aprender_de_historico(self, descricao):
        """Aprende com transações similares do histórico"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Buscar transações com descrições similares que já foram categorizadas
            cursor.execute("""
                SELECT descricao, categoria_id, COUNT(*) as frequencia
                FROM transacao 
                WHERE categoria_id IS NOT NULL
                GROUP BY descricao, categoria_id
                ORDER BY frequencia DESC
            """)
            
            transacoes_historico = cursor.fetchall()
            conn.close()
            
            melhor_similaridade = 0
            melhor_categoria = None
            
            for descricao_historico, categoria_id, frequencia in transacoes_historico:
                descricao_historico_limpa = self._limpar_texto(descricao_historico)
                similaridade = SequenceMatcher(None, descricao, descricao_historico_limpa).ratio()
                
                # Considerar tanto similaridade quanto frequência
                score = similaridade * (1 + frequencia * 0.1)  # Bonus por frequência
                
                if score > melhor_similaridade and similaridade > 0.7:  # 70% de similaridade para histórico
                    melhor_similaridade = score
                    melhor_categoria = categoria_id
            
            return melhor_categoria
            
        except Exception as e:
            print(f"Erro ao aprender do histórico: {e}")
            return None
    
    def sugerir_categoria_manual(self, descricao):
        """Sugere categorias para classificação manual"""
        if not descricao:
            return []
        
        descricao_limpa = self._limpar_texto(descricao)
        sugestoes = []
        
        # Calcular score para cada categoria
        for categoria_id, categoria_info in self.categorias.items():
            score = 0
            palavras_encontradas = []
            
            # Verificar palavras-chave da categoria
            for palavra in categoria_info['palavras_chave']:
                if palavra.lower() in descricao_limpa:
                    score += len(palavra)
                    palavras_encontradas.append(palavra)
            
            # Verificar palavras específicas
            nome_categoria = categoria_info['nome']
            if nome_categoria in self.palavras_especificas:
                for palavra in self.palavras_especificas[nome_categoria]:
                    if palavra.lower() in descricao_limpa:
                        score += len(palavra) * 1.5  # Peso maior para palavras específicas
                        if palavra not in palavras_encontradas:
                            palavras_encontradas.append(palavra)
            
            if score > 0:
                sugestoes.append({
                    'categoria_id': categoria_id,
                    'nome': nome_categoria,
                    'score': score,
                    'palavras_encontradas': palavras_encontradas,
                    'confianca': min(score / 20, 1.0)  # Normalizar confiança
                })
        
        # Ordenar por score e retornar top 3
        sugestoes.sort(key=lambda x: x['score'], reverse=True)
        return sugestoes[:3]
    
    def treinar_classificador(self, descricao, categoria_id):
        """Treina o classificador com uma nova associação"""
        try:
            # Extrair palavras importantes da descrição
            descricao_limpa = self._limpar_texto(descricao)
            palavras = descricao_limpa.split()
            
            # Filtrar palavras muito comuns (stop words básicas)
            stop_words = ['de', 'da', 'do', 'das', 'dos', 'em', 'na', 'no', 'para', 'com', 'por', 'a', 'o', 'e']
            palavras_relevantes = [p for p in palavras if len(p) > 2 and p not in stop_words]
            
            if not palavras_relevantes:
                return False
            
            # Atualizar palavras-chave da categoria no banco
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Buscar palavras-chave atuais
            cursor.execute("SELECT palavras_chave FROM categoria WHERE id = ?", (categoria_id,))
            resultado = cursor.fetchone()
            
            if resultado:
                palavras_atuais = json.loads(resultado[0]) if resultado[0] else []
                
                # Adicionar novas palavras relevantes (se não existirem)
                for palavra in palavras_relevantes:
                    if palavra not in palavras_atuais and len(palavra) > 3:
                        palavras_atuais.append(palavra)
                
                # Limitar a 50 palavras-chave por categoria
                if len(palavras_atuais) > 50:
                    palavras_atuais = palavras_atuais[-50:]
                
                # Atualizar no banco
                cursor.execute(
                    "UPDATE categoria SET palavras_chave = ? WHERE id = ?",
                    (json.dumps(palavras_atuais), categoria_id)
                )
                conn.commit()
            
            conn.close()
            
            # Recarregar categorias
            self.categorias = self._carregar_categorias()
            
            return True
            
        except Exception as e:
            print(f"Erro ao treinar classificador: {e}")
            return False
    
    def obter_estatisticas_classificacao(self):
        """Obtém estatísticas sobre a classificação automática"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total de transações
            cursor.execute("SELECT COUNT(*) FROM transacao")
            total_transacoes = cursor.fetchone()[0]
            
            # Transações classificadas
            cursor.execute("SELECT COUNT(*) FROM transacao WHERE categoria_id IS NOT NULL")
            transacoes_classificadas = cursor.fetchone()[0]
            
            # Transações por categoria
            cursor.execute("""
                SELECT c.nome, COUNT(t.id) as quantidade
                FROM categoria c
                LEFT JOIN transacao t ON c.id = t.categoria_id
                GROUP BY c.id, c.nome
                ORDER BY quantidade DESC
            """)
            
            por_categoria = cursor.fetchall()
            conn.close()
            
            taxa_classificacao = (transacoes_classificadas / total_transacoes * 100) if total_transacoes > 0 else 0
            
            return {
                'total_transacoes': total_transacoes,
                'transacoes_classificadas': transacoes_classificadas,
                'transacoes_nao_classificadas': total_transacoes - transacoes_classificadas,
                'taxa_classificacao': round(taxa_classificacao, 2),
                'por_categoria': [{'categoria': cat[0], 'quantidade': cat[1]} for cat in por_categoria]
            }
            
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return None

# Função utilitária para usar nas rotas do Flask
def classificar_automaticamente(descricao):
    """Função para ser chamada pelas rotas do Flask"""
    classificador = ClassificadorCategorias()
    return classificador.classificar_transacao(descricao)

def obter_sugestoes_categoria(descricao):
    """Função para obter sugestões de categoria"""
    classificador = ClassificadorCategorias()
    return classificador.sugerir_categoria_manual(descricao)