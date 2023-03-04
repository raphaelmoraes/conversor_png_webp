from PIL import Image
import os
import json
import mysql.connector

#path da localização das imagens
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

# abre o cursor para a consulta no banco de dados
cursor = db.cursor()

# Seleciona todas as imagens que ainda não foram convertidas com o limite de 10
try:
    cursor.execute("SELECT caminho_imagem FROM imagens WHERE convertida = 0 limit 10")
    imagens_nao_convertidas = cursor.fetchall()
except mysql.connector.Error as err:
    print("Erro ao executar comando SQL:", err)
    db.close()
    exit()

# Looping para converter cada imagem
for imagens in imagens_nao_convertidas:
    
    # array para gravar as imagens convertidas
    imagens_convertidas = []
    
    #boolean de validação para saber se todo o grupo de imagens foi convertido antes de gravar
    converteu = True
    
    #o caminho das imagens no banco de dados foram armazenadas em formato de array (json) será necessário fazer um loop dentro da estrutura
    for caminho_imagem in json.loads(imagens[0]):
        try:
            print(caminho_imagem)
            # Abre a imagem com a biblioteca Pillow. Adicionado o path completo da imagem
            imagem = Image.open( path + caminho_imagem)

            # Define o caminho e o nome do arquivo WebP
            caminho_webp = os.path.splitext(caminho_imagem)[0] + '.webp'
            
            # Salva a imagem no formato WebP
            imagem.save(path + caminho_webp, 'webp')

            # Adiciona o caminho da imagem convertida à lista de imagens convertidas
            imagens_convertidas.append(caminho_webp)
        except:
            #caso ocorra algum erro na conversão
            converteu = False
            
    try:
        #caso tenha convertido todo o grupo de imagens
        if converteu:
            #realiza update no banco de dados atualizando o campo de convertido e atualiiza com os novas extensões das imagens
            cursor.execute("UPDATE imagens SET convertida = 1, caminho_imagem = %s WHERE caminho_imagem = %s", (json.dumps(imagens_convertidas), imagens[0],))
            db.commit()
            print(f"Grupo de imagens atualizado")
    except mysql.connector.Error as err:
        print(f"Erro ao atualizar tabela no banco de dados: {err}")
        db.rollback()

# Fecha a conexão com o banco de dados
cursor.close()
db.close()
