import csv
from flask import Flask, render_template
import pymysql

app = Flask(__name__)

db = pymysql.connect(
    host="SERVIDOR",
    user="root",
    password="123456",
    database="sysloja",
    cursorclass=pymysql.cursors.DictCursor
)

CSV_PATH = "catalogo.csv"


def ler_catalogo():
    ativos = set()

    with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")

        for row in reader:
            if row.get("ativo", "").strip() == "1":
                try:
                    ativos.add(int(row["CodPro"]))
                except:
                    pass

    return ativos


@app.route("/")
def home():

    ativos = ler_catalogo()

    # =========================
    # GRUPOS (CATEGORIAS)
    # =========================
    with db.cursor() as cursor:
        cursor.execute("SELECT CodGru, DesGru FROM cdgrupos")
        grupos = {
            g["CodGru"]: g["DesGru"]
            for g in cursor.fetchall()
        }

    # =========================
    # PRODUTOS
    # =========================
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM produtos")
        rows = cursor.fetchall()

    produtos = []
    categorias_set = set()

    for p in rows:
        try:
            cod = int(p["CodPro"])

            if cod not in ativos:
                continue

            # =========================
            # PREÇOS (NUMÉRICO LIMPO)
            # =========================
            def parse_price(v):
                if v is None:
                    return 0.0
                return float(
                    str(v)
                    .replace(".", "")
                    .replace(",", ".")
                )

            preco = parse_price(p.get("PcoVen", 0))
            preco_prom = parse_price(p.get("PcoProm", 0))
            qnt_prom = int(p.get("QntProm") or 0)

            # =========================
            # CATEGORIA
            # =========================
            codgru = p.get("CodGru")
            nome_categoria = grupos.get(codgru, "SEM CATEGORIA")

            categorias_produto = [nome_categoria]

            if qnt_prom > 0:
                categorias_produto.append("PROMOÇÕES")

            # =========================
            # DESCONTO
            # =========================
            desconto = 0
            if qnt_prom > 0 and preco > 0 and preco_prom > 0:
                desconto = round(((preco - preco_prom) / preco) * 100)

            # =========================
            # MONTA PRODUTO FINAL
            # =========================
            produtos.append({
                "CodPro": cod,
                "nome": p.get("DesPro", ""),

                "preco": preco,
                "preco_prom": preco_prom,
                "qnt_prom": qnt_prom,
                "desconto": desconto,

                "categoria": ",".join(categorias_produto),
                "imagem": f"/static/imagens/{cod}.jpg"
            })

            for c in categorias_produto:
                categorias_set.add(c)

        except:
            pass

    categorias = ["TODOS"] + sorted(categorias_set)

    return render_template(
        "index.html",
        produtos=produtos,
        categorias=categorias,
        catalogo_versao="1.0"
    )


if __name__ == "__main__":
    app.run(debug=True)