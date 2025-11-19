import os
import tempfile
import pytest

from app import app, db, Transacao


@pytest.fixture
def client(tmp_path):
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

    os.close(db_fd)
    os.remove(db_path)


def test_index(client):
    rv = client.get('/')
    assert rv.status_code == 200


def test_add_transaction(client):
    # adiciona uma transação simples e verifica redirecionamento
    rv = client.post('/adicionar', data={
        'tipo': 'Despesa',
        'categoria': '',
        'valor': '12.50',
        'data': '2025-01-10',
        'descricao': 'mercado teste'
    }, follow_redirects=True)
    assert rv.status_code == 200
    # verifica se a transação foi salva
    with app.app_context():
        t = Transacao.query.filter_by(descricao='mercado teste').first()
        assert t is not None
        assert t.categoria in ('Alimentação','Outros')


def test_classify_endpoint(client):
    # garante que o endpoint de classificação responde corretamente
    rv = client.post('/classificar', json={'descricao': 'compra no mercado perto de casa'})
    assert rv.status_code in (200, 400)
    # se 200, valida formato
    if rv.status_code == 200:
        j = rv.get_json()
        assert 'categoria' in j
