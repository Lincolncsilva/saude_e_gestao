import pandas as pd
from datetime import datetime
import os, re
from IPython.display import display

## CONFIGURAÇÃO

os.makedirs("./Data/processed", exist_ok= True)
RAW_DIR ="./Data/raw"
LOG_FILE ="./Data/logs/pipeline.log"
PROC_DIR = "./Data/processed"
PROC_FILE = f"{PROC_DIR}/p_file.txt"

open(PROC_FILE, "a").close()

##Leitura do arquivo CADOP.csv para enriquecimento

CADOP_FILE = "./Data/references/Relatorio_cadop.csv"

CADOP_DF = pd.read_csv(CADOP_FILE, sep= ";", encoding= "utf-8")

def ler_arquivos():
    dfs = []

    for ano in os.listdir(RAW_DIR):
        ano_path = os.path.join(RAW_DIR, ano)
        os.makedirs(f"{PROC_DIR}/{ano}")

        if not os.path.isdir(ano_path):
            continue

        for nome_arquivo in os.listdir(ano_path):
            arquivo_path = os.path.join(ano_path, nome_arquivo)

            with open(f"{PROC_FILE}") as c:
                if nome_arquivo in c.read():
                    continue

            if not os.path.isfile(arquivo_path):
                continue

            if nome_arquivo.lower().endswith(".csv"):
                df = pd.read_csv(arquivo_path, sep=";", encoding="utf-8", header=0)

            elif nome_arquivo.lower().endswith(".txt"):
                df = pd.read_csv(arquivo_path, sep=";", encoding="latin-1", header=0)

            elif nome_arquivo.lower().endswith(".xlsx"):
                df = pd.read_excel(arquivo_path)

            else:
                continue

            # adiciona colunas de contexto
            df["trimestre"] =  int(nome_arquivo.split("T")[0])
            df["ano"] = ano
            df["arquivo_origem"] = nome_arquivo
            
            dfs.append(df)
                        
            with open(f"{PROC_FILE}", "a") as f:
                f.write(f"{nome_arquivo}\n")
                

            

    if not dfs:
        return pd.DataFrame()

    df_concat = pd.concat(dfs, ignore_index=True)
    df_filtrado = df_concat[df_concat['DESCRICAO'] == "Despesas com Eventos / Sinistros" ]
    df_filtrado.to_csv(f"./Data/processed/{ano}/consolidado.csv")

    



ler_arquivos()

