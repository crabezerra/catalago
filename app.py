from flask import Flask, render_template, request, jsonify
import os
import pymysql

app = Flask(__name__)

db = pymysql.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    cursorclass=pymysql.cursors.DictCursor
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

    categoria_selecionada = request.args.get("categoria", "TODOS")

    conn = db
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            p.CodPro,
            p.DesPro,
            p.PcoVen,
            p.PcoProm,
            p.QntProm,
            p.Inativo,
            g.DesGru
        FROM produtos p
        LEFT JOIN cdgrupos g ON g.CodGru = p.CodGru
        WHERE p.Inativo = 0
    """)

    rows = cursor.fetchall()

    produtos = []
    categorias_set = set()

    for row in rows:

        preco_venda = float(row["PcoVen"] or 0)

        qnt_prom = row["QntProm"] or 0

        pco_prom = float(row["PcoProm"] or 0)

        categoria = row["DesGru"] or "SEM CATEGORIA"

        categorias_produto = [categoria]

        if qnt_prom > 0:
            categorias_produto.append("PROMOÇÕES")

        percentual = 0
        if qnt_prom > 0 and pco_prom > 0:
            percentual = round(((preco_venda - pco_prom) / preco_venda) * 100)

        produtos.append({
            "nome": row["DesPro"],
            "categoria": ",".join(categorias_produto),
            "preco": f"R$ {preco_venda:.2f}".replace(".", ","),
            "preco_prom": f"R$ {pco_prom:.2f}".replace(".", ",") if pco_prom > 0 else "",
            "qnt_prom": qnt_prom,
            "desconto": percentual,
            "imagem": f"/static/imagens/{row['CodPro']}.jpg"
        })

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