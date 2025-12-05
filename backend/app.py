from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import json
import sys

# Adicionar o diretório ml ao path para importar os módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml'))

try:
    from previsao_gastos import obter_previsao_gastos, obter_multiplas_previsoes, analisar_padroes
    from classificador import classificar_automaticamente, obter_sugestoes_categoria
except ImportError as e:
    print(f"Aviso: Módulos ML não encontrados: {e}")
    # Funções fallback
    def obter_previsao_gastos():
        return None
    def obter_multiplas_previsoes(meses=3):
        return []
    def analisar_padroes():
        return None
    def classificar_automaticamente(descricao):
        return None
    def obter_sugestoes_categoria(descricao):
        return []

app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/controle_gastos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'

# Criar diretório do banco se não existir
os.makedirs('database', exist_ok=True)

db = SQLAlchemy(app)
CORS(app)

# Modelos do banco de dados
class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    palavras_chave = db.Column(db.Text)  # JSON com palavras-chave para classificação automática
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'palavras_chave': json.loads(self.palavras_chave) if self.palavras_chave else []
        }

class Transacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    tipo = db.Column(db.String(10), nullable=False)  # 'receita' ou 'despesa'
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=True)
    categoria = db.relationship('Categoria', backref=db.backref('transacoes', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao,
            'valor': self.valor,
            'data': self.data.strftime('%Y-%m-%d'),
            'tipo': self.tipo,
            'categoria': self.categoria.to_dict() if self.categoria else None
        }

# Rotas da API
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/transacoes')
def transacoes():
    return render_template('transacoes.html')

# API Routes
@app.route('/api/transacoes', methods=['GET'])
def get_transacoes():
    transacoes = Transacao.query.order_by(Transacao.data.desc()).all()
    return jsonify([t.to_dict() for t in transacoes])

@app.route('/api/transacoes', methods=['POST'])
def create_transacao():
    data = request.get_json()
    
    # Classificação automática de categoria
    categoria_id = classificar_categoria(data['descricao'])
    
    transacao = Transacao(
        descricao=data['descricao'],
        valor=float(data['valor']),
        data=datetime.strptime(data['data'], '%Y-%m-%d').date(),
        tipo=data['tipo'],
        categoria_id=categoria_id
    )
    
    db.session.add(transacao)
    db.session.commit()
    
    return jsonify(transacao.to_dict()), 201

@app.route('/api/transacoes/<int:id>', methods=['PUT'])
def update_transacao(id):
    transacao = Transacao.query.get_or_404(id)
    data = request.get_json()
    
    transacao.descricao = data['descricao']
    transacao.valor = float(data['valor'])
    transacao.data = datetime.strptime(data['data'], '%Y-%m-%d').date()
    transacao.tipo = data['tipo']
    transacao.categoria_id = classificar_categoria(data['descricao'])
    
    db.session.commit()
    
    return jsonify(transacao.to_dict())

@app.route('/api/transacoes/<int:id>', methods=['DELETE'])
def delete_transacao(id):
    transacao = Transacao.query.get_or_404(id)
    db.session.delete(transacao)
    db.session.commit()
    
    return '', 204

@app.route('/api/categorias', methods=['GET'])
def get_categorias():
    categorias = Categoria.query.all()
    return jsonify([c.to_dict() for c in categorias])

@app.route('/api/dashboard/resumo', methods=['GET'])
def get_resumo():
    # Total de receitas e despesas do mês atual
    hoje = datetime.now().date()
    primeiro_dia_mes = hoje.replace(day=1)
    
    receitas_mes = db.session.query(db.func.sum(Transacao.valor)).filter(
        Transacao.tipo == 'receita',
        Transacao.data >= primeiro_dia_mes
    ).scalar() or 0
    
    despesas_mes = db.session.query(db.func.sum(Transacao.valor)).filter(
        Transacao.tipo == 'despesa',
        Transacao.data >= primeiro_dia_mes
    ).scalar() or 0
    
    saldo_mes = receitas_mes - despesas_mes
    
    return jsonify({
        'receitas_mes': receitas_mes,
        'despesas_mes': despesas_mes,
        'saldo_mes': saldo_mes
    })

@app.route('/api/dashboard/gastos-por-categoria', methods=['GET'])
def get_gastos_por_categoria():
    hoje = datetime.now().date()
    primeiro_dia_mes = hoje.replace(day=1)
    
    gastos = db.session.query(
        Categoria.nome,
        db.func.sum(Transacao.valor).label('total')
    ).join(Transacao).filter(
        Transacao.tipo == 'despesa',
        Transacao.data >= primeiro_dia_mes
    ).group_by(Categoria.nome).all()
    
    return jsonify([{'categoria': g.nome, 'total': g.total} for g in gastos])

# Novas rotas para Machine Learning
@app.route('/api/ml/previsao', methods=['GET'])
def get_previsao_gastos():
    """Retorna previsão de gastos para o próximo mês"""
    try:
        previsao = obter_previsao_gastos()
        if previsao:
            return jsonify(previsao)
        else:
            return jsonify({
                'erro': 'Dados insuficientes para previsão',
                'previsao': 0,
                'minimo': 0,
                'maximo': 0,
                'confianca': 0
            })
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/ml/previsao-multipla', methods=['GET'])
def get_previsao_multipla():
    """Retorna previsões para múltiplos meses"""
    try:
        meses = request.args.get('meses', 3, type=int)
        previsoes = obter_multiplas_previsoes(meses)
        return jsonify(previsoes)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/ml/padroes', methods=['GET'])
def get_padroes_gastos():
    """Retorna análise de padrões de gastos"""
    try:
        padroes = analisar_padroes()
        if padroes:
            return jsonify(padroes)
        else:
            return jsonify({'erro': 'Dados insuficientes para análise'})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/ml/sugestoes-categoria', methods=['POST'])
def get_sugestoes_categoria():
    """Retorna sugestões de categoria para uma descrição"""
    try:
        data = request.get_json()
        descricao = data.get('descricao', '')
        
        if not descricao:
            return jsonify({'erro': 'Descrição é obrigatória'}), 400
        
        sugestoes = obter_sugestoes_categoria(descricao)
        return jsonify(sugestoes)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/categorias/<int:categoria_id>/treinar', methods=['POST'])
def treinar_classificador(categoria_id):
    """Treina o classificador com uma nova associação"""
    try:
        data = request.get_json()
        descricao = data.get('descricao', '')
        
        if not descricao:
            return jsonify({'erro': 'Descrição é obrigatória'}), 400
        
        # Importar aqui para evitar erro se módulo não estiver disponível
        from classificador import ClassificadorCategorias
        classificador = ClassificadorCategorias()
        
        sucesso = classificador.treinar_classificador(descricao, categoria_id)
        
        if sucesso:
            return jsonify({'mensagem': 'Classificador treinado com sucesso'})
        else:
            return jsonify({'erro': 'Erro ao treinar classificador'}), 500
            
    except ImportError:
        return jsonify({'erro': 'Módulo de classificação não disponível'}), 500
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

def classificar_categoria(descricao):
    """Classifica automaticamente a categoria baseada na descrição"""
    # Usar o sistema de ML para classificação
    categoria_id = classificar_automaticamente(descricao)
    if categoria_id:
        return categoria_id
    
    # Fallback para o sistema anterior
    descricao_lower = descricao.lower()
    
    categorias = Categoria.query.all()
    for categoria in categorias:
        if categoria.palavras_chave:
            palavras = json.loads(categoria.palavras_chave)
            for palavra in palavras:
                if palavra.lower() in descricao_lower:
                    return categoria.id
    
    return None  # Sem categoria definida

def init_database():
    """Inicializa o banco com dados básicos"""
    db.create_all()
    
    # Criar categorias padrão se não existirem
    if Categoria.query.count() == 0:
        categorias_default = [
            {'nome': 'Alimentação', 'palavras_chave': ['supermercado', 'restaurante', 'lanche', 'comida', 'padaria', 'açougue']},
            {'nome': 'Transporte', 'palavras_chave': ['uber', 'taxi', 'combustível', 'ônibus', 'metro', 'gasolina']},
            {'nome': 'Moradia', 'palavras_chave': ['aluguel', 'condomínio', 'água', 'luz', 'gás', 'internet']},
            {'nome': 'Saúde', 'palavras_chave': ['farmácia', 'médico', 'consulta', 'exame', 'remédio']},
            {'nome': 'Lazer', 'palavras_chave': ['cinema', 'teatro', 'show', 'viagem', 'festa', 'bar']},
            {'nome': 'Educação', 'palavras_chave': ['curso', 'livro', 'faculdade', 'escola', 'material']},
            {'nome': 'Vestuário', 'palavras_chave': ['roupa', 'calçado', 'sapato', 'camisa', 'calça']},
            {'nome': 'Outros', 'palavras_chave': []}
        ]
        
        for cat_data in categorias_default:
            categoria = Categoria(
                nome=cat_data['nome'],
                palavras_chave=json.dumps(cat_data['palavras_chave'])
            )
            db.session.add(categoria)
        
        db.session.commit()

if __name__ == '__main__':
    init_database()
    app.run(debug=True, port=5000)