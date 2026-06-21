import pandas as pd
import mariadb
import sys

import os

PASTA = os.path.dirname(os.path.abspath(__file__))

ARQUIVO_EXCEL = os.path.join(
    PASTA,
    "Uploude_promo.xlsx"
)

CONFIG_DB = {
    "host": "192.168.1.240",
    "user": "root",
    "password": "123456",
    "database": "sysloja",
    "port": 3306
}


print("Conectando no banco...")

conn = mariadb.connect(
    host=CONFIG_DB["host"],
    user=CONFIG_DB["user"],
    password=CONFIG_DB["password"],
    database=CONFIG_DB["database"],
    port=CONFIG_DB["port"]
)

print("Banco conectado!")

try:

    print("Lendo planilha...")
    df = pd.read_excel(ARQUIVO_EXCEL)

    if "CodPro" not in df.columns:
        raise Exception("A coluna CodPro é obrigatória.")

    colunas = [c for c in df.columns if c != "CodPro"]

    if len(colunas) == 0:
        raise Exception("Nenhuma coluna para atualizar.")

    print(f"Colunas para atualização: {', '.join(colunas)}")
    print(f"Produtos na planilha: {len(df)}")

    conn = mariadb.connect(**CONFIG_DB)
    cursor = conn.cursor()

    set_clause = ", ".join(
        [f"`{col}` = ?" for col in colunas]
    )

    sql = f"""
        UPDATE produtos
        SET {set_clause}
        WHERE CodPro = ?
    """

    atualizados = 0

    for _, row in df.iterrows():

        valores = []

        for col in colunas:

            valor = row[col]

            if pd.isna(valor):
                valor = None

            valores.append(valor)

        valores.append(int(row["CodPro"]))

        cursor.execute(sql, tuple(valores))

        atualizados += cursor.rowcount

    conn.commit()

    print()
    print("Importação concluída.")
    print(f"Registros atualizados: {atualizados}")

except Exception as e:
    print(f"ERRO: {e}")
    sys.exit(1)

finally:
    try:
        conn.close()
    except:
        pass