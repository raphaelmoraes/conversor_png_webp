import mysql.connector

# Conexão com o banco de dados MySQL
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="conversao"
    )
except mysql.connector.Error as err:
    print("Erro ao conectar no banco de dados:", err)
    exit()
