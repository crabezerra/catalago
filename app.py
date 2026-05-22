from flask import Flask, render_template, request, jsonify
import csv
import os
import pymysql

app = Flask(__name__)

CSV_PATH = os.path.join(os.path.dirname(__file__), "catalogo.csv")

CEP_PATH = os.path.join(os.path.dirname(__file__), "CEP.txt")

# =========================
# VALIDAR CEP
# =========================
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
# TESTE MARIADB
# =========================
@app.route("/teste-db")
def teste_db():

    try:
        conexao = pymysql.connect(
            host="SERVIDOR",
            user="root",
            password="123456",
            database="sysloja",
            charset="utf8mb4"
        )

        cursor = conexao.cursor()

        cursor.execute("""
            SELECT CodPro, DesPro, PcoVen
            FROM produtos
            WHERE Inativo <> 1
            LIMIT 10
        """)

        produtos = cursor.fetchall()

        html = "<h1>Conectado com sucesso</h1>"

        for p in produtos:
            html += f"""
                <div>
                    {p[0]} - {p[1]} - R$ {p[2]}
                </div>
            """

        conexao.close()

        return html

    except Exception as e:
        return f"Erro: {e}"


# =========================
# HOME
# =========================
@app.route("/")
def home():

    categoria_selecionada = request.args.get("categoria", "TODOS")

    produtos = []
    categorias_set = set()

    if not os.path.exists(CSV_PATH):
        return "catalogo.csv nao encontrado"

    with open(CSV_PATH, newline="", encoding="utf-8-sig") as file:

        reader = csv.DictReader(file, delimiter=';')

        for row in reader:

            if row.get("ativo", "").strip() == "1":

                preco_venda = float(
                    row["PcoVen"]
                    .replace(".", "")
                    .replace(",", ".")
                )

                qnt_prom = int(row.get("QntProm", "0") or 0)

                pco_prom_str = row.get("PcoProm", "0")

                pco_prom = float(
                    pco_prom_str
                    .replace(".", "")
                    .replace(",", ".")
                ) if pco_prom_str else 0

                categoria = row["DesGru"]

                categorias_produto = [categoria]

                if qnt_prom > 0:
                    categorias_produto.append("PROMOÇÕES")

                percentual = 0

                if qnt_prom > 0 and pco_prom > 0:
                    percentual = round(
                        ((preco_venda - pco_prom) / preco_venda) * 100
                    )

                produtos.append({
                    "nome": row["DesPro"],
                    "categoria": ",".join(categorias_produto),
                    "preco": f"R$ {preco_venda:.2f}".replace(".", ","),
                    "preco_prom": f"R$ {pco_prom:.2f}".replace(".", ",") if pco_prom > 0 else "",
                    "qnt_prom": qnt_prom,
                    "desconto": percentual,
                    "imagem": f"/static/imagens/{row['produto_id']}.jpg"
                })

                for c in categorias_produto:
                    categorias_set.add(c)

        if categoria_selecionada != "TODOS":
            produtos = [
                p for p in produtos
                if categoria_selecionada in p["categoria"].split(",")
            ]

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