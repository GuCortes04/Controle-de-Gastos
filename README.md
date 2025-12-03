# Sistema Web de Controle de Gastos Pessoais

## 📋 Informações do Projeto

**Nome:** Sistema Web de Controle de Gastos Pessoais com Previsão Inteligente de Despesas  
**Autor:** Gustavo Cortes de Oliveira  
**Instituição:** Universidade Nove de Julho (Uni9)  
**Período:** 3 meses  
**Metodologia:** Ágil (Scrum/Kanban)  

## 🎯 Objetivos

### Objetivo Geral
Desenvolver um sistema web que permita o controle de receitas e despesas pessoais, com previsão de gastos futuros e categorização automática utilizando aprendizado de máquina.

### Objetivos Específicos
- ✅ Criar um CRUD completo para gerenciamento de receitas e despesas
- ✅ Gerar gráficos e relatórios financeiros em um dashboard
- ✅ Implementar um modelo de previsão de gastos mensais
- ✅ Classificar automaticamente as transações por categoria

## 🚀 Funcionalidades

### 📊 Dashboard Financeiro
- Resumo de receitas, despesas e saldo mensal
- Gráficos de gastos por categoria
- Gráfico de distribuição (pizza) dos gastos
- Previsão de gastos futuros
- Últimas transações

### 💰 Gerenciamento de Transações
- Cadastro de receitas e despesas
- Edição e exclusão de transações
- Filtros por tipo, categoria e período
- Classificação automática de categorias

### 🤖 Inteligência Artificial
- **Classificação Automática:** Sistema inteligente que categoriza transações baseado na descrição
- **Previsão de Gastos:** Modelo de Machine Learning que prevê gastos futuros usando regressão linear
- **Análise de Padrões:** Identifica padrões de gastos por categoria, dia da semana e mês

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.8+**
- **Flask** - Framework web
- **SQLAlchemy** - ORM para banco de dados
- **SQLite** - Banco de dados
- **Scikit-learn** - Machine Learning
- **Pandas** - Manipulação de dados
- **NumPy** - Computação científica

### Frontend
- **HTML5** - Estrutura
- **Bootstrap 5** - Framework CSS
- **Chart.js** - Gráficos interativos
- **Bootstrap Icons** - Ícones
- **JavaScript** - Interatividade

### Machine Learning
- **Regressão Linear** - Previsão de gastos
- **Classificação por Similaridade** - Categorização automática
- **Análise de Padrões** - Insights financeiros

## 📁 Estrutura do Projeto

```
controle-gastos/
├── backend/
│   └── app.py                 # Aplicação Flask principal
├── frontend/
│   ├── templates/
│   │   ├── base.html         # Template base
│   │   ├── index.html        # Página inicial
│   │   ├── dashboard.html    # Dashboard
│   │   └── transacoes.html   # Gerenciar transações
│   └── static/
│       ├── css/
│       │   └── style.css     # Estilos personalizados
│       └── js/               # Scripts JavaScript
├── ml/
│   ├── previsao_gastos.py    # Modelo de previsão
│   └── classificador.py     # Classificação automática
├── database/
│   └── controle_gastos.db    # Banco SQLite (gerado automaticamente)
├── tests/                    # Testes (futuros)
├── docs/                     # Documentação adicional
├── requirements.txt          # Dependências Python
└── run.py                   # Arquivo principal de execução
```

## 🚀 Como Executar

### 🔥 MÉTODO MAIS FÁCIL (Windows)

**Duplo-clique nos arquivos .bat:**

1. **Se Python NÃO estiver instalado:**
   - Execute: `INSTALAR_PYTHON.bat`
   - Siga as instruções na tela

2. **Para executar o sistema:**
   - Execute: `EXECUTAR.bat`
   - O sistema abrirá automaticamente

### 🛠️ MÉTODO MANUAL

#### 1. Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

#### 2. Instalação Python (se necessário)
**Windows:**
- Download: https://www.python.org/downloads/
- **IMPORTANTE:** Marque "Add Python to PATH" durante instalação
- **OU** Microsoft Store: procure "Python 3.11"

#### 3. Instalação do Projeto
```bash
# Navegar para o projeto
cd controle-gastos

# Instalar dependências
pip install -r requirements.txt
```

#### 4. Execução
```bash
# Executar o sistema
python run.py

# OU executar com opções
python run.py --setup    # Instalar dependências
python run.py --help     # Ver ajuda
```

### 4. Acesso
- **Página Inicial:** http://localhost:5000
- **Dashboard:** http://localhost:5000/dashboard
- **Transações:** http://localhost:5000/transacoes

## 📖 Manual de Uso

### Cadastrando uma Transação
1. Acesse a página "Transações"
2. Clique em "Nova Transação"
3. Preencha os dados:
   - **Descrição:** Descreva a transação (ex: "Supermercado Extra")
   - **Valor:** Valor da transação
   - **Data:** Data da transação
   - **Tipo:** Receita ou Despesa
4. O sistema automaticamente categorizará a transação
5. Clique em "Salvar"

### Visualizando o Dashboard
1. Acesse o "Dashboard"
2. Visualize:
   - Cards de resumo (receitas, despesas, saldo)
   - Gráfico de gastos por categoria
   - Gráfico de distribuição dos gastos
   - Últimas transações
3. Para gerar previsão, clique em "Gerar Previsão"

### Classificação Automática
O sistema automaticamente categoriza novas transações baseado em:
- Palavras-chave na descrição
- Similaridade com transações anteriores
- Padrões aprendidos pelo sistema

## 🤖 Sistema de Machine Learning

### Classificação Automática de Categorias

#### Como Funciona
1. **Análise de Texto:** O sistema analisa a descrição da transação
2. **Correspondência de Palavras-chave:** Busca palavras específicas para cada categoria
3. **Similaridade de Texto:** Compara com transações anteriores
4. **Aprendizado:** Melhora com o tempo baseado nas correções do usuário

#### Categorias Disponíveis
- **Alimentação:** Supermercados, restaurantes, delivery
- **Transporte:** Uber, combustível, transporte público
- **Moradia:** Aluguel, contas básicas, manutenção
- **Saúde:** Farmácia, consultas, exames
- **Lazer:** Cinema, viagens, entretenimento
- **Educação:** Cursos, livros, material escolar
- **Vestuário:** Roupas, calçados, acessórios
- **Outros:** Demais categorias

### Previsão de Gastos

#### Modelo Utilizado
- **Algoritmo:** Regressão Linear (Scikit-learn)
- **Features:** Mês, quantidade de transações, gastos anteriores, médias móveis
- **Saída:** Previsão mensal com intervalo de confiança

#### Como Funciona
1. **Coleta de Dados:** Analisa histórico de transações
2. **Preparação:** Cria features temporais e estatísticas
3. **Treinamento:** Treina modelo com dados históricos
4. **Previsão:** Gera previsão para próximos meses
5. **Validação:** Calcula métricas de erro (MAE, RMSE)

#### Requisitos
- Mínimo 4 meses de dados para treinamento
- Dados consistentes de transações
- Categorização das transações

## 🔧 API Endpoints

### Transações
- `GET /api/transacoes` - Lista todas as transações
- `POST /api/transacoes` - Cria nova transação
- `PUT /api/transacoes/{id}` - Atualiza transação
- `DELETE /api/transacoes/{id}` - Remove transação

### Dashboard
- `GET /api/dashboard/resumo` - Resumo financeiro
- `GET /api/dashboard/gastos-por-categoria` - Gastos por categoria

### Machine Learning
- `GET /api/ml/previsao` - Previsão próximo mês
- `GET /api/ml/previsao-multipla?meses=3` - Múltiplas previsões
- `GET /api/ml/padroes` - Análise de padrões
- `POST /api/ml/sugestoes-categoria` - Sugestões de categoria

### Categorias
- `GET /api/categorias` - Lista categorias
- `POST /api/categorias/{id}/treinar` - Treina classificador

## 📊 Banco de Dados

### Tabelas Principais

#### Categoria
- `id` (INTEGER, PK)
- `nome` (STRING)
- `palavras_chave` (TEXT/JSON)

#### Transacao
- `id` (INTEGER, PK)
- `descricao` (STRING)
- `valor` (FLOAT)
- `data` (DATE)
- `tipo` (STRING) - 'receita' ou 'despesa'
- `categoria_id` (INTEGER, FK)

## 🎨 Interface do Usuário

### Design
- **Framework:** Bootstrap 5
- **Tema:** Moderno e responsivo
- **Cores:** Azul para receitas, vermelho para despesas
- **Ícones:** Bootstrap Icons

### Responsividade
- Funciona em desktop, tablet e mobile
- Layout adaptável para diferentes tamanhos de tela
- Navegação touch-friendly

## ⚡ Performance e Otimização

### Backend
- Cache de consultas frequentes
- Índices no banco de dados
- Paginação para listas grandes

### Frontend
- Carregamento assíncrono de dados
- Gráficos otimizados com Chart.js
- Compressão de assets

### Machine Learning
- Modelo leve e eficiente
- Cache de previsões
- Treinamento incremental

## 🔒 Segurança

### Medidas Implementadas
- Validação de entrada de dados
- Sanitização de dados do usuário
- CORS configurado adequadamente
- SQL injection protection (SQLAlchemy)

### Recomendações Futuras
- Autenticação de usuários
- HTTPS em produção
- Backup automático do banco
- Logs de auditoria

## 🧪 Testes

### Tipos de Teste (Planejados)
- **Unitários:** Funções individuais
- **Integração:** APIs e banco de dados
- **Machine Learning:** Acurácia dos modelos
- **Frontend:** Interface do usuário

### Ferramentas
- **pytest** - Testes Python
- **Coverage** - Cobertura de código
- **Selenium** - Testes automatizados de UI

## 📈 Métricas e Monitoramento

### KPIs do Sistema
- Taxa de classificação automática correta
- Acurácia da previsão de gastos
- Tempo de resposta das APIs
- Satisfação do usuário

### Monitoramento
- Logs de aplicação
- Métricas de performance
- Alertas de erro
- Dashboard de admin (futuro)

## 🚀 Roadmap Futuro

### Versão 2.0
- [ ] Multi-usuário com autenticação
- [ ] Sincronização com bancos (Open Banking)
- [ ] Alertas e notificações
- [ ] Aplicativo mobile
- [ ] Relatórios avançados em PDF
- [ ] Backup na nuvem

### Melhorias de ML
- [ ] Modelos mais sofisticados (Random Forest, XGBoost)
- [ ] Detecção de anomalias nos gastos
- [ ] Recomendações personalizadas
- [ ] Análise de sentimento nas descrições
- [ ] Previsão de receitas

### Integração
- [ ] API para apps externos
- [ ] Webhooks para automação
- [ ] Integração com assistentes virtuais
- [ ] Exportação para Excel/CSV
- [ ] Importação de extratos bancários

## 🤝 Contribuição

### Como Contribuir
1. Fork do projeto
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Abra um Pull Request

### Padrões de Código
- **Python:** PEP 8
- **JavaScript:** ES6+
- **HTML/CSS:** Indentação 2 espaços
- **Commits:** Conventional Commits

## 📞 Suporte

### Contato
- **Desenvolvedor:** Gustavo Cortes de Oliveira
- **Instituição:** Universidade Nove de Julho (Uni9)
- **Email:** [gustavocortes@uni9.edu.br]

### Issues Conhecidos
- Previsão requer mínimo 4 meses de dados
- Classificação melhora com uso contínuo
- Performance pode degradar com muitos dados

## 📜 Licença

Este projeto foi desenvolvido como trabalho acadêmico para a Universidade Nove de Julho (Uni9).

## 🙏 Agradecimentos

- Universidade Nove de Julho (Uni9)
- Professores orientadores
- Comunidade open source
- Documentação das tecnologias utilizadas

---

**Última atualização:** Outubro 2025  
**Versão:** 1.0.0  
**Status:** Em desenvolvimento
