import csv

DATA = "../data/"
MUNICIPIO_ID = 1
ARQUIVOS = [("pam_cafe.csv", "Café", 1), ("pam_milho.csv", "Milho", 2)]

def num(v):
    try:
        return float(v.strip())
    except ValueError:
        return None  # ".." ou "-" viram vazio

def ler(arquivo, palavra):
    with open(DATA + arquivo, encoding="utf-8-sig", newline="") as f:
        linhas = list(csv.reader(f, delimiter=";"))
    dados = {}  # ano -> {"area": x, "producao": y}
    for i, l in enumerate(linhas):
        if not l or not l[0].startswith("Variável -"):
            continue
        var = "area" if "Área colhida" in l[0] else "producao"
        anos, produtos = linhas[i + 2], linhas[i + 3]
        dado = next(r for r in linhas[i + 4:i + 8] if r and "São João da Boa Vista" in r[0])
        ano = None
        for j in range(1, len(produtos)):
            if j < len(anos) and anos[j].strip():
                ano = int(anos[j])
            if j < len(produtos) and palavra in produtos[j] and j < len(dado):
                dados.setdefault(ano, {})[var] = num(dado[j])
    return dados

linhas_saida = []
for arquivo, palavra, cultura_id in ARQUIVOS:
    for ano, v in sorted(ler(arquivo, palavra).items()):
        linhas_saida.append([MUNICIPIO_ID, cultura_id, ano, v.get("area"), v.get("producao")])

with open(DATA + "safra_limpa.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["municipio_id", "cultura_id", "ano", "area_ha", "producao_t"])
    w.writerows(linhas_saida)

print("Linhas geradas:", len(linhas_saida))