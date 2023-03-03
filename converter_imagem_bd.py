from PIL import Image
import os
import json
import mysql.connector

path = "C:/projetos/python/conversor_png_webp/imagens/"

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

# Cursor para executar comandos SQL
cursor = db.cursor()

# Seleciona todas as imagens que ainda não foram convertidas
try:
    cursor.execute("SELECT id, caminho_imagem FROM imagens WHERE convertida = 0 limit 10")
    imagens_nao_convertidas = cursor.fetchall()
except mysql.connector.Error as err:
    print("Erro ao executar comando SQL:", err)
    db.close()
    exit()

# Lista para armazenar os caminhos das imagens que serão convertidas
caminhos_a_converter = []

# Percorre cada imagem não convertida
for (id, caminho_imagem) in imagens_nao_convertidas:
    caminhos_a_converter.append(caminho_imagem)

# Lista para armazenar as imagens que foram convertidas com sucesso
imagens_convertidas = []

# Lista para armazenar as mensagens de erro durante a conversão
erros_conversao = []

# Looping para converter cada imagem
for imagens in caminhos_a_converter:
    converteu = True
    for caminho_imagem in json.loads(imagens):
        try:
            # Abre a imagem com a biblioteca Pillow
            imagem = Image.open( path + caminho_imagem)

            # Define o caminho e o nome do arquivo WebP
            caminho_webp = os.path.splitext(caminho_imagem)[0] + '.webp'
            
            # Salva a imagem no formato WebP
            imagem.save(path + caminho_webp, 'webp')

            # Adiciona o caminho da imagem convertida à lista de imagens convertidas
            imagens_convertidas.append(caminho_webp)
        except:
            converteu = False
            
    try:
        if converteu:
            cursor.execute("UPDATE imagens SET convertida = 1, caminho_imagem = %s WHERE caminho_imagem = %s", (json.dumps(imagens_convertidas), imagens,))
            db.commit()
            print(f"Grupo de imagens atualizado")
    except mysql.connector.Error as err:
        print(f"Erro ao atualizar tabela no banco de dados: {err}")
        db.rollback()

# Fecha a conexão com o banco de dados
db.close()
