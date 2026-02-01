import requests
import zipfile
from datetime import datetime
import os
from io import BytesIO


## CONFIGURAÇÃO

os.makedirs("./Data/logs", exist_ok = True)

RAW_DIR ="./Data/raw"
LOG_FILE ="./Data/logs/pipeline.log"
URL_BASE = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"
DATA_FILE = f"{RAW_DIR}/d_file.txt"

# Garantindo a existência do d_file.txt
os.makedirs(RAW_DIR, exist_ok=True)
open(DATA_FILE, "a").close

# Ano anterior e ano vigente para automatizar o dowload
ANO_ANTERIOR = datetime.now().year -1
ANO_ATUAL = datetime.now().year

# Remissão aos trimestres conforme nome dos arquivos
tri =("1T", "2T", "3T", "4T")

# função Download dos últimos arquivos por ano inseridos na API

def evento_log(tipo, evento, nome_arquivo, detalhe=""):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok= True)

    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    linha = f"{timestamp} | {tipo} | {evento} | {nome_arquivo}"

    if detalhe:
        linha += f" | {detalhe}"
    linha += "\n"

    with open(LOG_FILE, "a") as f:
        f.write(linha)

def Dowload_arquivos():
    for t in tri: 
        try: 

                      
            if datetime.now().month < 6:
                os.makedirs(f"{RAW_DIR}/{ANO_ANTERIOR}", exist_ok = True)
                
                url = f"{URL_BASE}/{ANO_ANTERIOR}/{t}{ANO_ANTERIOR}.zip"
                r = requests.get(url, timeout=60)
                r.raise_for_status()

                r_content = BytesIO(r.content)
                file = zipfile.ZipFile(r_content)
                arquivo = url.split("/")[-1]

                with open(DATA_FILE, "r") as c:
                    baixados = set(line.strip() for line in c if line.strip())
                if arquivo in baixados:
                    continue
                  
                ## Log de download ano_anterior
                evento_log("INFO","DOWNLOADED",arquivo, detalhe=f"SIZE={len(r.content)}")
                
                ## Extração do zip
                file.extractall(f"{RAW_DIR}/{ANO_ANTERIOR}")

                ## Log de extração do Zip ano_anterior
                evento_log("INFO","EXTRACTED",arquivo, detalhe=f"DEST={RAW_DIR}/{ANO_ANTERIOR}")
            
            else:
                os.makedirs(f"{RAW_DIR}/{ANO_ATUAL}", exist_ok = True)

                url = f"{URL_BASE}/{ANO_ATUAL}/{t}{ANO_ATUAL}.zip"
                r = requests.get(url)
                r.raise_for_status()

                r_content = BytesIO(r.content)
                file = zipfile.ZipFile(r_content)
                arquivo = url.split("/")[-1]

                ## Log de download Ano_atual
                evento_log("INFO","DOWNLOADED",arquivo, detalhe=f"SIZE={len(r.content)}") 

                file.extractall(f"{RAW_DIR}/{ANO_ATUAL}")

                ## Log de extração do zip ano_atual
                evento_log("INFO","EXTRACTED",arquivo, detalhe=f"DEST={RAW_DIR}/{ANO_ATUAL}")

            with open(DATA_FILE, "a") as f:
                f.write(f"{arquivo}\n")

        ## Logs em caso de erros de HTTP 
        except requests.exceptions.HTTPError as e:
            arquivo = url.split("/")[-1]
            evento_log("WARN","HTTP_ERROR",arquivo, detalhe= str(e))
            
                
        ## Logs em caso de zip com problemas
        except zipfile.BadZipFile as e:
            arquivo = url.split("/")[-1]
            evento_log("WARN","BAD_ZIP",arquivo, detalhe=f"SIZE={len(r.content)}")
           
if __name__ == "__main__": Dowload_arquivos()
