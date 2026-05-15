from flask import Flask, render_template
import csv
import os

app = Flask(__name__)

CSV_PATH = os.path.join(os.path.dirname(__file__), "catalogo.csv")


@app.route("/")
def home():

    produtos = []
    categorias_set = set()

    if not os.path.exists(CSV_PATH):
        return "catalogo.csv nao encontrado"

    with open(CSV_PATH, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file, delimiter=';')

        for row in reader:

            if row.get("ativo", "").strip() == "1":

                preco = row["PcoVen"].replace(",", ".")
                categoria = row["DesGru"]

                produtos.append({
                    "nome": row["DesPro"],
                    "categoria": categoria,
                    "preco": f"R$ {float(preco):.2f}".replace(".", ","),
                    "imagem": f"/static/imagens/{row['produto_id']}.jpg"
                })

                categorias_set.add(categoria)

    categorias = sorted(list(categorias_set))

    return render_template(
        "index.html",
        produtos=produtos,
        categorias=categorias
    )


if __name__ == "__main__":
    app.run(debug=True)