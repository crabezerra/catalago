from flask import Flask, render_template
import csv
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "catalogo.csv")

@app.route("/")
def home():

    produtos = []

    if not os.path.exists(CSV_PATH):
        return "catalogo.csv nao encontrado"

    with open(CSV_PATH, newline="", encoding="utf-8-sig") as file:

        reader = csv.DictReader(file, delimiter=';')

        for row in reader:

            if row.get("ativo", "").strip() == "1":

                preco = row["PcoVen"].replace(",", ".")

                produtos.append({
                    "nome": row["DesPro"],
                    "preco": f"R$ {float(preco):.2f}".replace(".", ","),
                    "descricao": "",
                    "imagem": f"/static/imagens/{row['produto_id']}.jpg"
                })

    return render_template("index.html", produtos=produtos)

if __name__ == "__main__":
    app.run()