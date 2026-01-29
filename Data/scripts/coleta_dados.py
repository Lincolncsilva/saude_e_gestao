import requests
import httpx
import zipfile
from datetime import datetime
import os
from io import BytesIO


os.makedirs("./Data/raw/logs", exist_ok = True)

path = "./Data/raw" 

# url que será utilizada para downloads dos arquivos 
url_base = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"

# Ano anterior e ano vigente para automatizar o dowload
ano_anterior = datetime.now().year -1
ano = datetime.now().year

# Remissão aos trimestres conforme nome dos arquivos
tri =("1T", "2T", "3T", "4T")

# função Download dos últimos arquivos por ano inseridos na API

def Dowload_arquivos():
    for t in tri: 
        try:            
            if datetime.now().month < 6:
                r = requests.get(f"{url_base}/{ano_anterior}/{t}{ano_anterior}.zip")
                r.raise_for_status()
                r_content = BytesIO(r.content)
                file = zipfile.ZipFile(r_content)

                ## Log de download Ano_anterior
                with open(f"{path}/logs/pipeline.log", "a") as f:
                    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"INFO | DOWLOADED | {r.url.rfind("/")} | size={len(r.content)}\n")
                
                file.extractall(f"{path}/{ano_anterior}")

                ## Log de extração do Zip Ano_anterior
                with open(f"{path}/logs/pipeline.log", "a") as f:
                    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"INFO | EXTRACTED | {r.url.rfind("/")} | DEST={path}/{ano_anterior}\n")
            
            else:
                r = requests.get(f"{url_base}/{ano}/{t}{ano}.zip")
                r.raise_for_status()
                r_content = BytesIO(r.content)
                file = zipfile.ZipFile(r_content)

                ## Log de download Ano_atual
                with open(f"{path}/logs/pipeline.log", "a") as f:
                    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"INFO | DOWLOADED | {r.url.rfind("/")} | size={len(r.content)}\n")
                    
                file.extractall(f"{path}/{ano}")

                ## Log de extração do zip ano_atual
                with open(f"{path}/logs/pipeline.log", "a") as f:
                    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"INFO | EXTRACTED | {r.url.rfind("/")} | DEST={path}/{ano}\n")

        ## Logs em caso de erros de HTTP 
        except requests.exceptions.HTTPError as e:
            with open(f"{path}/logs/pipeline.log", "a") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"WARN | HTTP_ERROR | {r.url} | {r.status_code} | {str(e)}\n")
                
        ## Logs em caso de zip com problemas
        except zipfile.BadZipFile as e:
            with open(f"{path}/logs/pipeline.log", "a") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"WARN | BAD_ZIP | {r.url} | {r.status_code} | size={len(r.content)}\n")


if __name__ == "__main__": Dowload_arquivos()
