from app import app, Transacao
import json

with app.app_context():
    total = Transacao.query.count()
    receitas = Transacao.query.filter_by(tipo='Receita').count()
    despesas = Transacao.query.filter_by(tipo='Despesa').count()
    ult = Transacao.query.order_by(Transacao.data.desc()).limit(10).all()
    ult_list = [{'id':t.id,'tipo':t.tipo,'categoria':t.categoria,'valor':t.valor,'data':t.data.strftime('%Y-%m-%d'),'descricao':t.descricao} for t in ult]
    print(json.dumps({'total':total,'receitas':receitas,'despesas':despesas,'ultimas':ult_list}, ensure_ascii=False))
