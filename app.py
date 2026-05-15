from flask import Flask, render_template
import csv

app = Flask(__name__)

@app.route("/")
def home():

    produtos = []

    with open("catalogo.csv", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["ativo"] == "1":

                produtos.append({
                    "nome": f"Produto {row['produto_id']}",
                    "preco": "R$ 0,00",
                    "descricao": "",
                    "imagem": f"/static/imagens/{row['produto_id']}.jpg"
                })

    return render_template("index.html", produtos=produtos)


if __name__ == "__main__":
    app.run(debug=True)