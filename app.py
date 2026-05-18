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

                preco = row["PcoVen"].replace(",", ".")
                categoria = row["DesGru"]

                produtos.append({

                    "nome": row["DesPro"],

                    "categoria": categoria,

                    "preco":
                    f"R$ {float(preco):.2f}"
                    .replace(".", ","),

                    "imagem":
                    f"/static/imagens/{row['produto_id']}.jpg"
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