import os
import tempfile

from app import app, db, Transacao


def run_tests():
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            db.create_all()

        # Test index
        rv = client.get('/')
        assert rv.status_code == 200

        # Test add transaction
        rv = client.post('/adicionar', data={
            'tipo': 'Despesa',
            'categoria': '',
            'valor': '20.00',
            'data': '2025-02-01',
            'descricao': 'mercado unit test'
        }, follow_redirects=True)
        assert rv.status_code == 200

        with app.app_context():
            t = Transacao.query.filter_by(descricao='mercado unit test').first()
            assert t is not None

    os.close(db_fd)
    os.remove(db_path)


if __name__ == '__main__':
    run_tests()
    print('All tests passed')
