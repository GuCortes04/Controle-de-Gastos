from app import app, dados_despesas, debug_stats

with app.app_context():
    r = dados_despesas()
    try:
        print('dados_despesas:', r.get_data(as_text=True))
    except Exception as e:
        print('dados_despesas error:', e)
    r2 = debug_stats()
    try:
        print('debug_stats:', r2.get_data(as_text=True))
    except Exception as e:
        print('debug_stats error:', e)
