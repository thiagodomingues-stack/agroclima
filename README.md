# AgroClima Integrado

Painel que cruza clima, preço de mercado e safra para apoiar decisões de
plantio, colheita e venda de café e milho em São João da Boa Vista (SP).

## Problema
Produtores decidem sem cruzar clima e preço. O painel mostra os dois juntos
e gera alertas (geada, chuva forte, preço em alta).

## Arquitetura
Fontes -> Python (coleta) -> SQLite (bruto) -> Apache Hop (ETL) -> PostgreSQL (tratado)
-> DuckDB + FastAPI (análise e API) -> React (painel)

## Fontes de dados
- Open-Meteo (API): histórico e previsão do tempo
- Yahoo Finance via yfinance (API): contratos futuros de café e milho (em dólar, bolsa)
- IBGE/SIDRA, Produção Agrícola Municipal (CSV): área e produção por ano

## Bancos de dados
- SQLite: dados brutos das APIs (data/bruto.db)
- PostgreSQL: dados tratados e consolidados (banco agroclima)
- DuckDB: consultas analíticas lendo o PostgreSQL

## Como rodar
1. Instale Python 3.11+, Node 18+, Java 21, PostgreSQL e Apache Hop.
2. pip install duckdb fastapi uvicorn requests psycopg2-binary yfinance
3. No PostgreSQL, crie o banco agroclima e rode backend/schema.sql.
4. Coleta (pasta backend): python coletar_clima.py, python coletar_preco.py, python limpar_safra.py
5. Apache Hop: abra e rode hop/carga_safra.hpl, carga_clima.hpl e carga_preco.hpl. Crie a conexão pg_agroclima (PostgreSQL, localhost:5432, banco agroclima, usuário postgres e a sua senha). Os pipelines apontam para pastas do computador onde foram criados:ajuste o caminho do arquivo no CSV file
   input (safra) e no Table input (clima e preço, arquivo data/bruto.db).
6. Backend (pasta backend):
   set PG_PASSWORD=suasenha
   python -m uvicorn main:app --reload
7. Frontend (pasta frontend): npm install e npm run dev, depois abra http://localhost:5173

## Limitações
- O preço é de contratos futuros de bolsa em dólar (referência de mercado),
  não o preço pago ao produtor em reais.
- Os alertas usam a previsão do tempo carregada no banco. Para ficarem atuais,
  rode coletar_clima.py e o pipeline carga_clima de novo.
- Os dados de safra do IBGE do último ano são preliminares.

## Endpoints
/clima, /precos, /safra, /correlacao, /alertas (documentação em /docs)

## Equipe
Thiago Mafra Domingues e Matheus Gabriel de Melo Tesch
