import os
import duckdb
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AgroClima")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

PG = ("dbname=agroclima user=postgres host=localhost "
      f"port={os.getenv('PG_PORT', '5432')} password={os.getenv('PG_PASSWORD', '')}")

# DuckDB lê direto do PostgreSQL (camada analítica)
con = duckdb.connect()
con.execute("INSTALL postgres; LOAD postgres;")
con.execute(f"ATTACH '{PG}' AS pg (TYPE postgres, READ_ONLY)")

CULTURAS = {"cafe": 1, "milho": 2}


def consulta(sql, params=None):
    cur = con.cursor().execute(sql, params or [])
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


@app.get("/clima")
def clima(dias: int = 30):
    r = consulta("""SELECT data, temp_min::DOUBLE AS temp_min,
                    temp_max::DOUBLE AS temp_max, chuva_mm::DOUBLE AS chuva_mm
                    FROM pg.public.clima_diario ORDER BY data DESC LIMIT ?""", [dias])
    return r[::-1]


@app.get("/precos")
def precos(cultura: str = "cafe", dias: int = 120):
    r = consulta("""SELECT data, preco::DOUBLE AS preco, unidade
                    FROM pg.public.preco_diario WHERE cultura_id = ?
                    ORDER BY data DESC LIMIT ?""", [CULTURAS[cultura], dias])
    return r[::-1]


@app.get("/safra")
def safra():
    return consulta("""SELECT c.nome AS cultura, s.ano, s.area_ha::DOUBLE AS area_ha,
                       s.producao_t::DOUBLE AS producao_t
                       FROM pg.public.safra s
                       JOIN pg.public.cultura c ON c.id = s.cultura_id
                       ORDER BY c.nome, s.ano""")


@app.get("/correlacao")
def correlacao(cultura: str = "cafe"):
    return consulta("""
        WITH p AS (SELECT date_trunc('month', data) AS mes, avg(preco) AS preco
                   FROM pg.public.preco_diario WHERE cultura_id = ? GROUP BY 1),
             c AS (SELECT date_trunc('month', data) AS mes, sum(chuva_mm) AS chuva_mm,
                   avg(temp_max) AS temp_max
                   FROM pg.public.clima_diario GROUP BY 1)
        SELECT p.mes::DATE AS mes, p.preco::DOUBLE AS preco,
               c.chuva_mm::DOUBLE AS chuva_mm, c.temp_max::DOUBLE AS temp_max
        FROM p JOIN c ON p.mes = c.mes ORDER BY p.mes""", [CULTURAS[cultura]])


@app.get("/alertas")
def alertas():
    lista = []
    prev = consulta("""SELECT data, temp_min::DOUBLE AS temp_min, chuva_mm::DOUBLE AS chuva_mm
                       FROM pg.public.clima_diario WHERE data >= current_date ORDER BY data""")
    for d in prev:
        if d["temp_min"] is not None and d["temp_min"] <= 4:
            lista.append({"tipo": "geada", "data": d["data"],
                          "descricao": f"Mínima de {d['temp_min']}°C: risco de geada"})
        if d["chuva_mm"] is not None and d["chuva_mm"] >= 20:
            lista.append({"tipo": "chuva forte", "data": d["data"],
                          "descricao": f"Previsão de {d['chuva_mm']} mm de chuva"})
    risco_clima = len(lista) > 0

    for nome, cid in {"café": 1, "milho": 2}.items():
        p = consulta("""SELECT preco::DOUBLE AS preco FROM pg.public.preco_diario
                        WHERE cultura_id = ? ORDER BY data DESC LIMIT 30""", [cid])
        if len(p) >= 2:
            var = (p[0]["preco"] / p[-1]["preco"] - 1) * 100
            if var >= 5:
                lista.append({"tipo": "preço em alta", "data": None,
                              "descricao": f"{nome}: +{var:.1f}% em 30 pregões"})
                if risco_clima:
                    lista.append({"tipo": "ação sugerida", "data": None,
                                  "descricao": f"{nome}: preço em alta e clima de risco na previsão. Avalie antecipar colheita ou venda."})
    return lista