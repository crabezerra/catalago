from flask import Flask, render_template

app = Flask(__name__)

produtos = [
    {
        "nome": "Camisa Nike",
        "preco": "R$ 99,90",
        "imagem": "https://via.placeholder.com/300",
        "descricao": "Camisa esportiva premium"
    },
    {
        "nome": "Tênis Adidas",
        "preco": "R$ 249,90",
        "imagem": "https://via.placeholder.com/300",
        "descricao": "Tênis confortável para corrida"
    },
    {
        "nome": "Boné Puma",
        "preco": "R$ 59,90",
        "imagem": "https://via.placeholder.com/300",
        "descricao": "Boné ajustável original"
    }
]

@app.route("/")
def home():
    return render_template("index.html", produtos=produtos)

if __name__ == "__main__":
    app.run(debug=True)