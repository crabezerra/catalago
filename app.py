from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

def db():
    return mysql.connector.connect(
        host="SERVIDOR",
        user="root",
        password="123456",
        database="sysloja"
    )

@app.route("/")
def home():
    conn = db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT 
            p.CodPro,
            p.DesPro,
            p.PcoVen,
            c.ordem
        FROM catalogo c
        JOIN produtos p ON p.CodPro = c.produto_id
        WHERE c.ativo = 1
        ORDER BY c.ordem
    """)

    dados = cur.fetchall()

    produtos = []

    for p in dados:
        produtos.append({
            "nome": p["DesPro"],
            "preco": f"R$ {p['PcoVen']:.2f}" if p["PcoVen"] else "R$ 0,00",
            "descricao": "",
            "imagem": f"/static/imagens/{p['CodPro']}.jpg"
        })

    return render_template("index.html", produtos=produtos)

if __name__ == "__main__":
    app.run(debug=True)