import sqlite3
import requests

DB = "../data/bruto.db"
LAT, LON = -21.97, -46.80

con = sqlite3.connect(DB)
con.execute("""CREATE TABLE IF NOT EXISTS raw_clima (
    data TEXT PRIMARY KEY, temp_max REAL, temp_min REAL,
    chuva_mm REAL, fonte TEXT)""")

def salvar(daily, fonte):
    for d, tmax, tmin, ch in zip(daily["time"], daily["temperature_2m_max"],
                                 daily["temperature_2m_min"], daily["precipitation_sum"]):
        con.execute("INSERT OR REPLACE INTO raw_clima VALUES (?,?,?,?,?)",
                    (d, tmax, tmin, ch, fonte))

campos = "temperature_2m_max,temperature_2m_min,precipitation_sum"

# histórico
h = requests.get("https://archive-api.open-meteo.com/v1/archive", params={
    "latitude": LAT, "longitude": LON, "daily": campos,
    "start_date": "2025-01-01", "end_date": "2026-11-05",
    "timezone": "America/Sao_Paulo"}, timeout=60).json()
salvar(h["daily"], "historico")

# previsão
p = requests.get("https://api.open-meteo.com/v1/forecast", params={
    "latitude": LAT, "longitude": LON, "daily": campos,
    "timezone": "America/Sao_Paulo"}, timeout=60).json()
salvar(p["daily"], "previsao")

con.commit()
print("Linhas salvas:", con.execute("SELECT COUNT(*) FROM raw_clima").fetchone()[0])