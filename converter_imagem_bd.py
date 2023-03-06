from PIL import Image
from conexao import db
import os
import json
import mysql.connector
import shutil

####### CONFIGURACOES  ##########
#Path da localização das imagens
path = "C:/projetos/python/conversor_png_webp/imagens/"

#Remover as imagens originais após a conversão
salvar_originais = True
#################################


#cursor para a consulta no banco de dados
cursor = db.cursor()

#Seleciona todas as imagens que ainda não foram convertidas com o limite de 10
try:
    cursor.execute("SELECT id, img FROM imagens WHERE convertido = 0 limit 10")
    imagens_nao_convertidas = cursor.fetchall()
except mysql.connector.Error as err:
    print("Erro ao executar comando SQL:", err)
    db.close()
    exit()

for (id, imagens) in imagens_nao_convertidas:
    
    # array para gravar as imagens convertidas
    imagens_convertidas = []
    
    #boolean de validação para saber se todo o grupo de imagens foi convertido antes de gravar
    converteu = True
    
    #o caminho das imagens no banco de dados foram armazenadas em formato de array (json) será necessário fazer um loop dentro da estrutura
    for imagem_original in json.loads(imagens):
        try:
            print("Convertendo: " + imagem_original)
            # Abre a imagem com a biblioteca Pillow. Adicionado o path completo da imagem
            imagem = Image.open(path + imagem_original)

            # Define o caminho e o nome do arquivo WebP
            caminho_webp = os.path.splitext(imagem_original)[0] + '.webp'
            
            # Salva a imagem no formato WebP
            imagem.save(path + caminho_webp, 'webp')

            # Adiciona o caminho da imagem convertida à lista de imagens convertidas
            imagens_convertidas.append(caminho_webp)
        except:
            #caso ocorra algum erro na conversão
            converteu = False
            
    try:
        #Caso tenha convertido todo o grupo de imagens
        if converteu:
            #Realiza update no banco de dados atualizando o campo convertido, campo img com as novas imagens e img_original no id correspondente
            cursor.execute("UPDATE imagens SET convertido = 1, img = %s, img_original = %s WHERE id = %s", (json.dumps(imagens_convertidas), imagens, id))
            #db.commit()
            print(f"Imagens atualizadas no BD: {imagens}")
            
            #após atualizar o banco de dados, remove as imagens originais, caso configurado
            if salvar_originais:
                
                if not os.path.exists(path + "backup/"):
                    os.makedirs(path + "backup/")
                
                for imagem in json.loads(imagens):
                    imagem_split = imagem.split("/")
                    
                    if not os.path.exists(path + imagem_split[0]):
                        os.makedirs(path + imagem_split[0])

                    os.rename(path + imagem, path + "backup/" + imagem)
                        

                    print(f"Imagem removida: {imagem}")
        
        print(f"..........................")

    except mysql.connector.Error as err:
        print(f"Erro ao atualizar tabela no banco de dados: {err}")
        db.rollback()

# Fecha o cursor e a conexão com o banco de dados
cursor.close()
db.close()
