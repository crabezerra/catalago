from flask import Flask, render_template, request, jsonify
import csv
import os

app = Flask(__name__)

CSV_PATH = os.path.join(
    os.path.dirname(__file__),
    "catalogo.csv"
)

# =========================
# VALIDAR CEP
# =========================
CEP_PATH = os.path.join(
    os.path.dirname(__file__),
    "CEP.txt"
)

@app.route("/validar_cep")
def validar_cep():

    cep = request.args.get("cep", "")

    cep = cep.replace("-", "").strip()

    permitido = False

    with open(
        CEP_PATH,
        encoding="utf-8"
    ) as f:

        for linha in f:

            prefixo = linha.strip()

            if not prefixo:
                continue

            if cep.startswith(prefixo):

                permitido = True
                break

    return jsonify({
        "ok": permitido
    })

# =========================
# HOME
# =========================
@app.route("/")
def home():

    produtos = []
    categorias_set = set()

    if not os.path.exists(CSV_PATH):
        return "catalogo.csv nao encontrado"

    with open(
        CSV_PATH,
        newline="",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(
            file,
            delimiter=';'
        )

        for row in reader:

            if row.get("ativo", "").strip() == "1":

                preco_venda = float(
                     row["PcoVen"]
                     .replace(".", "")
                     .replace(",", ".")
                )

                qnt_prom = int(
                    row.get("QntProm", "0") or 0
                )

                pco_prom_str = row.get("PcoProm", "0")

                pco_prom = float(
                    pco_prom_str
                    .replace(".", "")
                    .replace(",", ".")
                ) if pco_prom_str else 0

                categoria = row["DesGru"]

                # CALCULA DESCONTO

                percentual = 0
                if qnt_prom > 0 and pco_prom > 0:
                    percentual = round(
                        ((preco_venda - pco_prom) / preco_venda) * 100
                    )              

                produtos.append({
                    "nome": row["DesPro"],
                    "categoria": categoria,
                    "preco": f"R$ {preco_venda:.2f}".replace(".", ","),
                    "preco_prom": f"R$ {pco_prom:.2f}".replace(".", ",") if pco_prom > 0 else "",
                    "qnt_prom": qnt_prom,
                    "desconto": percentual,
                    "imagem": f"/static/imagens/{row['produto_id']}.jpg"
                })

                categorias_set.add(categoria)

    categorias = sorted(list(categorias_set))

    return render_template(
        "index.html",
        produtos=produtos,
        categorias=categorias
    )

# =========================
# START
# =========================
if __name__ == "__main__":

    app.run(debug=True)