from flask import Flask, render_template, request, jsonify
import os
import json

app = Flask(__name__)

# =========================
# CARREGAR JSONS
# =========================
BASE_DIR = os.path.dirname(__file__)

with open(os.path.join(BASE_DIR, "produtos.json"), encoding="utf-8") as f:
    PRODUTOS = json.load(f)

with open(os.path.join(BASE_DIR, "cdgrupos.json"), encoding="utf-8") as f:
    GRUPOS = json.load(f)

# mapa de grupos (CodGru -> DesGru)
GRUPO_MAP = {g["CodGru"]: g["DesGru"] for g in GRUPOS}

# =========================
# VALIDAR CEP
# =========================
CEP_PATH = os.path.join(BASE_DIR, "CEP.txt")

@app.route("/validar_cep")
def validar_cep():

    cep = request.args.get("cep", "")
    cep = cep.replace("-", "").strip()

    permitido = False

    with open(CEP_PATH, encoding="utf-8") as f:
        for linha in f:
            prefixo = linha.strip()

            if not prefixo:
                continue

            if cep.startswith(prefixo):
                permitido = True
                break

    return jsonify({"ok": permitido})

# =========================
# HOME
# =========================
@app.route("/")
def home():

    categoria_selecionada = request.args.get("categoria", "TODOS")

    rows = PRODUTOS

    produtos = []
    categorias_set = set()

    for row in rows:

        # ignora produtos inativos
        if row.get("Inativo", 0) != 0:
            continue

        preco_venda = float(row.get("PcoVen") or 0)
        pco_prom = float(row.get("PcoProm") or 0)
        qnt_prom = row.get("QntProm") or 0

        categoria = GRUPO_MAP.get(row.get("CodGru"), "SEM CATEGORIA")

        categorias_produto = [categoria]

        if qnt_prom > 0:
            categorias_produto.append("PROMOÇÕES")

        percentual = 0
        if qnt_prom > 0 and pco_prom > 0 and preco_venda > 0:
            percentual = round(((preco_venda - pco_prom) / preco_venda) * 100)

        produtos.append({
            "nome": row.get("DesPro"),
            "codpro": row.get("CodPro"),
            "dtvencimento": row.get("dtvencimento") or "",
            "estatu": row.get("EstAtu") or 0,

            "categoria": ",".join(categorias_produto),

            "preco": f"R$ {preco_venda:.2f}".replace(".", ","),
            "preco_prom": f"R$ {pco_prom:.2f}".replace(".", ","),
    
            "qnt_prom": qnt_prom,
            "desconto": percentual,

            "imagem": f"/static/imagens/{row.get('CodPro')}.jpg"
        })
        
        # produtos.append({
        #     "nome": row.get("DesPro"),
        #     "categoria": ",".join(categorias_produto),
        #     "preco": f"R$ {preco_venda:.2f}".replace(".", ","),
        #     "preco_prom": f"R$ {pco_prom:.2f}".replace(".", ",") if pco_prom > 0 else "",
        #     "qnt_prom": qnt_prom,
        #     "desconto": percentual,
        #     "imagem": f"/static/imagens/{row.get('CodPro')}.jpg"
        # })

        for c in categorias_produto:
            categorias_set.add(c)

    categorias = sorted(list(categorias_set))

    return render_template(
        "index.html",
        produtos=produtos,
        categorias=categorias,
        catalogo_versao="1.0"
    )

# =========================
# START
# =========================
if __name__ == "__main__":
    app.run(debug=True)