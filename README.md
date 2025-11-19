# Sistema de Controle de Gastos Pessoais

Projeto simples em Flask para controlar receitas e despesas, com dashboard e previsão de gastos.

Como executar (Windows PowerShell):

```powershell
cd C:\Users\gugui\controle_gastos
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python .\app.py
```

Abra http://127.0.0.1:5000 no navegador.

Observações:
- O endpoint `/previsao` usa pandas e scikit-learn; seja paciente na primeira execução se esses pacotes não estiverem instalados.
- O arquivo de banco de dados SQLite está em `data/financas.db`.
 - Endpoints adicionais:
	 - `GET /treinar_classificador` — tenta treinar um classificador de categorias usando transações rotuladas no banco (mínimo 5 amostras).
	 - `POST /classificar` — recebe JSON {"descricao": "..."} e retorna a categoria predita.
	 - `GET /previsao` — agora retorna JSON com a previsão e métricas quando aplicável.
