# Controle de Gastos Pessoais

Sistema web para controle de receitas e despesas com previsão inteligente usando Machine Learning.

**Acesse em:** https://gucortes04.github.io/Controle-de-Gastos/

## 🎯 Objetivo

Desenvolver um sistema web que permita o controle de receitas e despesas pessoais, com previsão de gastos futuros e categorização automática utilizando aprendizado de máquina.

## 🚀 Funcionalidades

- 💰 Dashboard financeiro com resumo de receitas, despesas e saldo
- 📊 Gráficos interativos de gastos por categoria e mês
- ➕ Cadastro rápido de transações com categorização automática
- 🤖 Machine Learning para previsão de gastos futuros
- 📈 Análise de padrões de gastos

## 🛠️ Tecnologias

- **Backend:** Python, Flask, SQLAlchemy, SQLite
- **Frontend:** HTML5, Bootstrap 5, Chart.js, JavaScript
- **ML:** Scikit-learn, Pandas, NumPy
- **Deploy:** GitHub Pages (estático), Flask (local)

## 🚀 Como Executar Localmente

### Pré-requisitos
- Python 3.8+
- pip

### Instalação

```bash
# Clonar repositório
git clone https://github.com/GuCortes04/Controle-de-Gastos.git
cd Controle-de-Gastos

# Instalar dependências
pip install -r requirements.txt

# Executar
python app.py
```

Acesse: http://localhost:5000

## 📁 Estrutura

```
├── app.py                    # Aplicação Flask
├── templates/
│   ├── index.html           # Template principal com Jinja2
│   └── index_clean.html     # Versão alternativa
├── static/                  # Assets estáticos
├── docs/
│   └── index.html           # Versão estática para GitHub Pages
├── data/
│   └── financas.db          # Banco SQLite
├── ml/                      # Modelos de Machine Learning
└── requirements.txt         # Dependências Python
```

## 📊 Funcionalidades Principais

### Dashboard
- Resumo financeiro (receitas, despesas, saldo)
- Gráficos de gastos mensais
- Últimas transações

### Transações
- Adicionar receitas e despesas
- Categorização automática
- Editar e excluir transações
- Filtros por tipo, categoria e período

### Machine Learning
- Classificação automática de categorias
- Previsão de gastos futuros
- Análise de padrões de gastos

## 🔧 API (Quando rodando localmente)

- `GET /transacoes_json` - Lista transações em JSON
- `GET /dados_despesas` - Dados de despesas mensais
- `POST /adicionar` - Adicionar nova transação
- `GET /excluir/<id>` - Excluir transação
- `POST /importar_csv` - Importar CSV
- `GET /exportar_csv` - Exportar para CSV

## 👨‍💻 Autor

**Gustavo Cortes de Oliveira**
- Universidade Nove de Julho (Uni9)
- Email: gustavocortes@uni9.edu.br

## 📝 Licença

Projeto acadêmico desenvolvido para a Universidade Nove de Julho (Uni9).

## 🙏 Agradecimentos

- Universidade Nove de Julho (Uni9)
- Comunidade open source
- Documentação das tecnologias utilizadas

---

**Status:** Em desenvolvimento
**Versão:** 1.0.0
**Última atualização:** Dezembro 2025
