from app import app

with app.test_client() as c:
    rv = c.get('/dados_despesas')
    print('dados_despesas status:', rv.status_code)
    print(rv.get_data(as_text=True))
    rv2 = c.get('/debug_stats')
    print('debug_stats status:', rv2.status_code)
    print(rv2.get_data(as_text=True))
