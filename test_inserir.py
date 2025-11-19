from app import app

with app.test_client() as c:
    r = c.post('/inserir_exemplo')
    print('insert status', r.status_code)
    rd = c.get('/dados_despesas')
    print('dados_despesas status', rd.status_code)
    print(rd.get_data(as_text=True))
