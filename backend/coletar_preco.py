import sqlite3
import yfinance as yf

con = sqlite3.connect("../data/bruto.db")
con.execute("""CREATE TABLE IF NOT EXISTS raw_preco (
    data TEXT, cultura TEXT, preco REAL, unidade TEXT, fonte TEXT,
    PRIMARY KEY (data, cultura))""")

ATIVOS = {"café": ("KC=F", "US¢/lb"), "milho": ("ZC=F", "US¢/bushel")}

for cultura, (ticker, unidade) in ATIVOS.items():
    hist = yf.Ticker(ticker).history(start="2025-01-01")
    for data, linha in hist.iterrows():
        con.execute("INSERT OR REPLACE INTO raw_preco VALUES (?,?,?,?,?)",
                    (data.strftime("%Y-%m-%d"), cultura, float(linha["Close"]),
                     unidade, "Yahoo Finance"))
    print(cultura, "->", len(hist), "dias")

con.commit()
print("Total:", con.execute("SELECT COUNT(*) FROM raw_preco").fetchone()[0])