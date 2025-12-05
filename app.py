from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import logging
import io
import csv
from werkzeug.utils import secure_filename

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
# Caminho absoluto do banco de dados SQLite (evita problemas com diretórios relativos no Windows)
data_dir = os.path.join(basedir, 'data')
# garantir que o diretório de dados exista o quanto antes
os.makedirs(data_dir, exist_ok=True)
db_file = os.path.join(data_dir, 'financas.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_file.replace('\\','/')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# configurar logging básico para capturar requisições e erros
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Helper: formatar números para moeda brasileira (R$ 1.234,56)
def format_brl(value):
    try:
        v = float(value or 0)
    except Exception:
        try:
            # attempt to coerce strings with comma decimal
            v = float(str(value).replace('.', '').replace(',', '.'))
        except Exception:
            v = 0.0
    # Python's format uses ',' as thousands sep and '.' as decimal; swap for BRL
    s = f"{v:,.2f}"
    # swap thousand and decimal separators: '1,234.56' -> '1.234,56'
    s = s.replace(',', 'X').replace('.', ',').replace('X', '.')
    return f"R$ {s}"

# register filter
app.jinja_env.filters['brl'] = format_brl


@app.before_request
def log_request_info():
    logger.info("Request: %s %s", request.method, request.path)


@app.after_request
def add_cors_headers(response):
    # Allow local dev tools (Live Server) to fetch JSON endpoints from Flask.
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

# ------------------------------
# MODELO DO BANCO DE DADOS
# ------------------------------
class Transacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20))  # Receita ou Despesa
    categoria = db.Column(db.String(50))
    valor = db.Column(db.Float)
    data = db.Column(db.Date)
    descricao = db.Column(db.String(200))

    def __init__(self, tipo, categoria, valor, data, descricao):
        self.tipo = tipo
        self.categoria = categoria
        self.valor = valor
        self.data = data
        self.descricao = descricao


def classify_categoria(descricao: str) -> str:
    """Classificador simples por palavras-chave que retorna uma categoria baseada na descrição."""
    if not descricao:
        return 'Outros'
    texto = descricao.lower()
    palavras_chave = {
        'aliment': 'Alimentação',
        'mercado': 'Alimentação',
        'supermercado': 'Alimentação',
        'transporte': 'Transporte',
        'ônibus': 'Transporte',
        'uber': 'Transporte',
        'combustível': 'Transporte',
        'gasolina': 'Transporte',
        'aluguel': 'Moradia',
        'luz': 'Moradia',
        'água': 'Moradia',
        'internet': 'Moradia',
        'salário': 'Salário',
        'receita': 'Receita',
        'restaurante': 'Lazer',
        'cinema': 'Lazer',
        'academia': 'Saúde',
        'farmácia': 'Saúde'
    }
    for chave, categoria in palavras_chave.items():
        if chave in texto:
            return categoria
    return 'Outros'


def get_model_paths():
    """Retorna caminhos para o vetorizar e modelo salvo."""
    vec_path = os.path.join(data_dir, 'vectorizer.joblib')
    model_path = os.path.join(data_dir, 'classifier.joblib')
    return vec_path, model_path


def train_classifier(force: bool = False) -> dict:
    """Treina um classificador simples (TF-IDF + MultinomialNB) usando transações existentes.
    Retorna um dicionário com status e números de amostras usadas."""
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import make_pipeline
    from joblib import dump

    transacoes = Transacao.query.filter(Transacao.categoria != None).all()
    # Use only those with non-empty descricao and categoria
    dados = [(t.descricao or '', t.categoria) for t in transacoes if (t.descricao and t.categoria)]
    if len(dados) < 5:
        return {'status': 'error', 'message': 'Poucos dados rotulados para treinar (min 5).', 'n_samples': len(dados)}

    df = pd.DataFrame(dados, columns=['descricao', 'categoria'])
    X = df['descricao'].values
    y = df['categoria'].values

    pipeline = make_pipeline(TfidfVectorizer(), MultinomialNB())
    pipeline.fit(X, y)

    vec_path, model_path = get_model_paths()
    # salva o pipeline inteiro
    dump(pipeline, model_path)
    return {'status': 'ok', 'n_samples': len(df)}


def predict_with_model(descricao: str) -> str:
    """Prediz categoria usando o modelo salvo; se não existir, tenta treinar.
    Se tudo falhar, usa o classificador heurístico."""
    from joblib import load
    vec_path, model_path = get_model_paths()
    try:
        if not os.path.exists(model_path):
            res = train_classifier()
            if res.get('status') != 'ok':
                return classify_categoria(descricao)
        model = load(model_path)
        pred = model.predict([descricao])[0]
        return pred
    except Exception:
        return classify_categoria(descricao)


@app.route('/treinar_classificador', methods=['GET'])
def treinar_classificador():
    res = train_classifier()
    return jsonify(res)


@app.route('/classificar', methods=['POST'])
def classificar_endpoint():
    data = request.get_json() or {}
    descricao = data.get('descricao', '')
    if not descricao:
        return jsonify({'status': 'error', 'message': 'descricao obrigatória'}), 400
    cat = predict_with_model(descricao)
    return jsonify({'status': 'ok', 'categoria': cat})


# ------------------------------
# (inicialização movida para o final do arquivo)
# ------------------------------

# ------------------------------
# ROTA PRINCIPAL
# ------------------------------
@app.route('/')
def index():
    transacoes = Transacao.query.order_by(Transacao.data.desc()).all()
    
    receitas = sum(t.valor for t in transacoes if t.tipo == 'Receita')
    despesas = sum(t.valor for t in transacoes if t.tipo == 'Despesa')
    saldo = receitas - despesas

    return render_template('index.html', transacoes=transacoes, saldo=saldo, receitas=receitas, despesas=despesas)

# ------------------------------
# ADICIONAR TRANSAÇÃO
# ------------------------------
@app.route("/adicionar", methods=["GET", "POST"])
def adicionar():
    # Accept GET to avoid HTTP 405 if the browser navigates to /adicionar.
    if request.method == 'GET':
        return redirect(url_for('index'))

    tipo = request.form.get('tipo')
    categoria = request.form.get('categoria') or "Sem categoria"
    try:
        valor = float(request.form.get('valor') or 0)
    except Exception:
        valor = 0.0
    data_raw = request.form.get('data')
    try:
        data = datetime.strptime(data_raw, "%Y-%m-%d") if data_raw else datetime.utcnow()
    except Exception:
        data = datetime.utcnow()
    descricao = request.form.get('descricao') or ''

    nova = Transacao(
        tipo=tipo,
        categoria=categoria,
        valor=valor,
        data=data,
        descricao=descricao
    )

    db.session.add(nova)
    db.session.commit()

    return redirect("/")

# ------------------------------
# EXCLUIR TRANSAÇÃO
# ------------------------------
@app.route('/excluir/<int:id>')
def excluir(id):
    transacao = Transacao.query.get(id)
    db.session.delete(transacao)
    db.session.commit()
    return redirect(url_for('index'))

# ------------------------------
# PREVISÃO DE GASTOS (MACHINE LEARNING)
# ------------------------------
@app.route('/previsao')
def previsao():
    # imports pesados colocados aqui para evitar lentidão/erros na inicialização
    import pandas as pd
    import numpy as np
    from sklearn.linear_model import LinearRegression

    transacoes = Transacao.query.filter_by(tipo='Despesa').order_by(Transacao.data.asc()).all()

    if len(transacoes) < 3:
        return "Poucos dados para gerar previsão."

    df = pd.DataFrame([(t.data, t.valor) for t in transacoes], columns=['data', 'valor'])
    # garantir que a coluna 'data' seja datetime
    df['data'] = pd.to_datetime(df['data'])
    df['mes'] = df['data'].dt.month
    df_grouped = df.groupby('mes')['valor'].sum().reset_index()

    X = np.array(df_grouped['mes']).reshape(-1, 1)
    y = np.array(df_grouped['valor'])

    modelo = LinearRegression()
    modelo.fit(X, y)

    proximo_mes = np.array([[df_grouped['mes'].max() + 1]])
    previsao = modelo.predict(proximo_mes)[0]

    return f"Previsão de gastos para o próximo mês: R$ {previsao:.2f}"


@app.route('/dados_despesas')
def dados_despesas():
    """Retorna JSON com despesas acumuladas por mês para alimentar gráficos no frontend."""
    transacoes = Transacao.query.filter_by(tipo='Despesa').order_by(Transacao.data.asc()).all()
    import pandas as pd

    if not transacoes:
        return jsonify({'meses': [], 'valores': []})

    df = pd.DataFrame([(t.data, t.valor) for t in transacoes], columns=['data', 'valor'])
    # garantir que a coluna 'data' seja datetime
    df['data'] = pd.to_datetime(df['data'])
    df['mes'] = df['data'].dt.strftime('%Y-%m')
    df_grouped = df.groupby('mes')['valor'].sum().reset_index()

    meses = df_grouped['mes'].tolist()
    valores = df_grouped['valor'].tolist()
    return jsonify({'meses': meses, 'valores': valores})


@app.route('/inserir_exemplo', methods=['POST', 'GET'])
def inserir_exemplo():
    """Insere algumas transações de exemplo no banco para fins de demonstração/debug."""
    # Apenas para facilitar demonstrações locais
    with app.app_context():
        exemplo = [
            Transacao('Receita', 'Salario', 2000.0, datetime.strptime('2025-01-01', '%Y-%m-%d'), 'Salário exemplo'),
            Transacao('Despesa', 'Alimentação', 150.0, datetime.strptime('2025-01-15', '%Y-%m-%d'), 'Supermercado exemplo'),
            Transacao('Despesa', 'Transporte', 60.0, datetime.strptime('2025-02-03', '%Y-%m-%d'), 'Uber exemplo'),
            Transacao('Despesa', 'Lazer', 90.0, datetime.strptime('2025-03-10', '%Y-%m-%d'), 'Cinema exemplo')
        ]
        for t in exemplo:
            db.session.add(t)
        db.session.commit()
    return redirect(url_for('index'))


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


@app.route('/debug_stats')
def debug_stats():
    """Retorna contagens e últimas transações para depuração do frontend."""
    total = Transacao.query.count()
    receitas = Transacao.query.filter_by(tipo='Receita').count()
    despesas = Transacao.query.filter_by(tipo='Despesa').count()
    ultimas = Transacao.query.order_by(Transacao.data.desc()).limit(5).all()
    ult = [{'id': t.id, 'tipo': t.tipo, 'categoria': t.categoria, 'valor': t.valor, 'data': t.data.strftime('%Y-%m-%d'), 'descricao': t.descricao} for t in ultimas]
    return jsonify({'total': total, 'receitas': receitas, 'despesas': despesas, 'ultimas': ult})


@app.route('/transacoes_json')
def transacoes_json():
    """Retorna todas as transações em JSON (para carregamento no frontend)."""
    transacoes = Transacao.query.order_by(Transacao.data.desc()).all()
    out = []
    for t in transacoes:
        out.append({
            'id': t.id,
            'tipo': t.tipo,
            'categoria': t.categoria,
            'valor': t.valor,
            'data': t.data.strftime('%Y-%m-%d') if t.data else None,
            'descricao': t.descricao
        })
    return jsonify({'transacoes': out})


# ------------------------------
# CSV Export / Import
# ------------------------------
@app.route('/exportar_csv')
def exportar_csv():
    transacoes = Transacao.query.order_by(Transacao.data.asc()).all()
    si = io.StringIO()
    writer = csv.writer(si)
    # header
    writer.writerow(['id', 'tipo', 'categoria', 'valor', 'data', 'descricao'])
    for t in transacoes:
        data_str = t.data.strftime('%Y-%m-%d') if t.data else ''
        writer.writerow([t.id, t.tipo, t.categoria or '', f"{t.valor}", data_str, t.descricao or ''])
    output = si.getvalue()
    resp = Response(output, mimetype='text/csv')
    resp.headers['Content-Disposition'] = 'attachment; filename=transacoes.csv'
    return resp


@app.route('/importar_csv', methods=['POST'])
def importar_csv():
    # Expect multipart/form-data with file input named 'file'
    f = request.files.get('file')
    if not f:
        return redirect(url_for('index'))
    filename = secure_filename(f.filename)
    # read CSV from stream
    stream = io.StringIO(f.stream.read().decode('utf-8'))
    reader = csv.DictReader(stream)
    created = 0
    for row in reader:
        try:
            tipo = row.get('tipo') or row.get('type') or 'Despesa'
            categoria = row.get('categoria') or row.get('category') or ''
            valor = float(row.get('valor') or row.get('value') or 0)
            data_raw = row.get('data') or row.get('date') or ''
            # try multiple date formats
            data_obj = None
            if data_raw:
                try:
                    data_obj = datetime.strptime(data_raw, '%Y-%m-%d')
                except Exception:
                    try:
                        data_obj = datetime.strptime(data_raw, '%d/%m/%Y')
                    except Exception:
                        data_obj = None
            descricao = row.get('descricao') or row.get('description') or ''
            nova = Transacao(tipo, categoria, valor, data_obj or datetime.utcnow(), descricao)
            db.session.add(nova)
            created += 1
        except Exception:
            # skip bad rows
            continue
    db.session.commit()
    return redirect(url_for('index'))


# ------------------------------
# INICIALIZAÇÃO
# ------------------------------
if __name__ == '__main__':
    # garantir diretório (já criado em import, mas reforça)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    with app.app_context():
        db.create_all()
    # permite alterar porta via variável de ambiente PORT (útil se 5000 estiver em uso)
    port = int(os.getenv('PORT', '5000'))
    host = os.getenv('HOST', '127.0.0.1')
    logger.info('Starting app on %s:%s', host, port)
    app.run(host=host, port=port, debug=True)
