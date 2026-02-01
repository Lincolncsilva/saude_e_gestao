import os
import pandas as pd
import zipfile
from validar_dados import validar_cnpj,validar_positivo,validar_razao_social
# -------------#
# CONFIGURAÇÃO #
# -------------#
os.makedirs("./Data/processed/auditoria", exist_ok=True)

RAW_DIR = "./Data/raw"
PROC_DIR = "./Data/processed"
PROC_FILE = f"{PROC_DIR}/p_file.txt"

# garante que o marker exista
open(PROC_FILE, "a").close()

# Arquivo CADOP
CADOP_FILE = "./Data/references/Relatorio_cadop.csv"
CADOP_DF = pd.read_csv(
    CADOP_FILE,
    sep=";",
    encoding="utf-8",
    dtype={"CNPJ": "string", "REGISTRO_OPERADORA": "string"},
)


def processar_dados():
    dfs = []

    # -----------------------------#
    # PROCESSAMENTO INCREMENTAL    #
    # -----------------------------#
    
    for ano in os.listdir(RAW_DIR):
        ano_path = os.path.join(RAW_DIR, ano)
        if not os.path.isdir(ano_path):
            continue

        processed_ano_dir = os.path.join(PROC_DIR, ano)
        os.makedirs(processed_ano_dir, exist_ok=True)

        for nome_arquivo in os.listdir(ano_path):
            arquivo_path = os.path.join(ano_path, nome_arquivo)

            # marker: se já estiver no p_file.txt não processa de novo.
            with open(PROC_FILE, "r") as c:
                if nome_arquivo in c.read():
                    continue

            if not os.path.isfile(arquivo_path):
                continue

            # leitura do arquivo baixado conforme extensão
            if nome_arquivo.lower().endswith(".csv"):
                df = pd.read_csv(arquivo_path, sep=";", encoding="utf-8", header=0)
            elif nome_arquivo.lower().endswith(".txt"):
                df = pd.read_csv(arquivo_path, sep=";", encoding="latin-1", header=0)
            elif nome_arquivo.lower().endswith(".xlsx"):
                df = pd.read_excel(arquivo_path)
            else:
                continue


            # Normalização de colunas 
            df.columns = df.columns.str.upper()

            # colunas de contexto
            df["Trimestre"] = int(nome_arquivo.split("T")[0])
            df["Ano"] = ano
            df["Arquivo_Origem"] = nome_arquivo

            dfs.append(df)

            # registra no marker como processado
            with open(PROC_FILE, "a") as f:
                f.write(f"{nome_arquivo}\n")


    if not dfs:
        print("Nenhum dado novo para processar.")
        return

    # ----------------#
    # CONCAT + FILTRO #
    # ----------------#
    df_concat = pd.concat(dfs, ignore_index=True)

    df_filtrado = df_concat[df_concat["DESCRICAO"] == "Despesas com Eventos / Sinistros"].copy()

    # Conversão numérica de colunas calculadas
    df_filtrado["VL_SALDO_FINAL"] = df_filtrado["VL_SALDO_FINAL"].astype(str).str.replace(",", ".").apply(pd.to_numeric, errors='coerce').fillna(0)
    df_filtrado["VL_SALDO_INICIAL"] = df_filtrado["VL_SALDO_INICIAL"].astype(str).str.replace(",", ".").apply(pd.to_numeric, errors='coerce').fillna(0)

    df_filtrado["ValorDespesas"] = (df_filtrado["VL_SALDO_FINAL"] - df_filtrado["VL_SALDO_INICIAL"]).round(2)

    # -------------------------------------#
    # JOIN (REG_ANS - REGISTRO_OPERADORA)  #
    # -------------------------------------#
    df_filtrado["REG_ANS"] =( df_filtrado["REG_ANS"]
                             .astype(str).str.replace(r"\.0$", "", regex=True))
    
    df_join = df_filtrado.join(
        CADOP_DF.set_index("REGISTRO_OPERADORA"),
        on="REG_ANS",
    )

    # -------------------#
    # RENOMEANDO COLUNAS #
    # -------------------#
    df_cons = (
        df_join.rename(
            columns={
                "Razao_Social": "RazaoSocial",
            }
        )[
            [
                "CNPJ",
                "RazaoSocial",
                "Trimestre",
                "Ano",
                "ValorDespesas",
            ]
        ]
    )

    # --------------------------#
    # AJUSTE DE TIPAGEM DO CNPJ #
    # --------------------------#
    df_cons["CNPJ"] =( df_cons["CNPJ"].astype(str)
                      .str.replace(r"\.0+$", "", regex=True)
                      .str.replace(r"\D", "", regex=True)
                      )

    # ------------#
    # VALIDAÇÕES  #
    # ------------#

    df_cons['CNPJ_Valido'] = df_cons['CNPJ'].apply(validar_cnpj)
    df_cons['Valor_Valido'] = df_cons['ValorDespesas'].apply(validar_positivo)
    df_cons['RS_Valida'] = df_cons['RazaoSocial'].apply(validar_razao_social)

    # -----------#
    # AUDITORIAS #
    # -----------#
    os.makedirs("./Data/processed/auditoria", exist_ok=True)
    df_check = df_cons.dropna(subset=["CNPJ", "RazaoSocial"]).copy()

    # Auditoria: CNPJs com múltiplas Razão Sociais
    cnpj_multi = df_check.groupby("CNPJ")["RazaoSocial"].nunique()
    df_check[df_check["CNPJ"].isin(cnpj_multi[cnpj_multi > 1].index)].to_csv(
        "./Data/processed/auditoria/cnpj_multiplas_razoes_sociais.csv", index=False
    )

    # Auditoria: Razão Social com múltiplos CNPJs
    razao_multi = df_check.groupby("RazaoSocial")["CNPJ"].nunique()
    df_check[df_check["RazaoSocial"].isin(razao_multi[razao_multi > 1].index)].to_csv(
        "./Data/processed/auditoria/razao_social_multiplos_cnpjs.csv", index=False
    )

    # Auditoria: Valores Negativos
    df_cons[df_cons["ValorDespesas"] <= 0].to_csv(
        "./Data/processed/auditoria/vd_zerados_e_negativos.csv", index=False
    )

    # Auditoria de Validação cnpj, valor positivos, razao social
    # 
    df_invalidos = df_cons[
        (df_cons['CNPJ_Valido'] == False) | 
        (df_cons['Valor_Valido'] == False) | 
        (df_cons['RS_Valida'] == False)
    ]
    df_invalidos.to_csv("./Data/processed/auditoria/inconsistencias_cadastrais.csv", index=False)

    # ----------------------#
    # EXPORT DO CONSOLIDADO #
    # ----------------------#
    # Salvando em CSV
    path_csv_cons = f"{PROC_DIR}/{ano}/consolidado_despesas.csv"
    df_cons.to_csv(path_csv_cons, index=False)
    
    # Gerando consolidado_despesas.zip
    with zipfile.ZipFile(f'{PROC_DIR}/{ano}/consolidado_despesas.zip', 'w') as z:
        z.write(path_csv_cons, arcname="consolidado_despesas.csv")
    print('consolidado_despesas.zip realizado com sucesso!')

    # ----------------------------#
    # AGREGAÇÃO E Cálculo         #
    # ----------------------------#
    
    # Join com CADOP para pegar UF e Modalidade
    df_desp = df_cons.merge(CADOP_DF, on="CNPJ", how="left")
    
    # Remove colunas duplicadas
    df_desp = df_desp.loc[:, ~df_desp.columns.duplicated()]

    
    

    # Desafio Adicional
    
    df_trimestral = df_desp.groupby(['RazaoSocial', 'UF', 'Trimestre'], as_index=False)['ValorDespesas'].sum() 
    df_agregado = df_trimestral.groupby(['RazaoSocial', 'UF'], as_index=False).agg(
        Total_Despesas=('ValorDespesas', 'sum'),
        Media_Trimestral=('ValorDespesas', 'mean'),
        Desvio_Padrao_Despesas=('ValorDespesas', 'std')
    ).round(2)

    # Trata Desvio Padrão para casos únicos
    df_agregado['Desvio_Padrao_Despesas'] = df_agregado['Desvio_Padrao_Despesas'].fillna(0)

    # Ordenação 
    df_agregado = df_agregado.sort_values(by='Total_Despesas', ascending=False)

    # Exportação despesas_agregadas.csv
    path_csv_agregado = f"{PROC_DIR}/despesas_agregadas.csv"
    df_agregado.to_csv(path_csv_agregado, index=False, sep=",", encoding="utf-8")
    
    # Zip final Teste_Lincoln_Silva.zip (Item 2.3)
    with zipfile.ZipFile('Teste_Lincoln_Silva.zip', 'w') as z:
        z.write(path_csv_agregado, arcname="despesas_agregadas.csv")
    print('Teste_Lincoln_Silva.zip realizado com sucesso!')

if __name__ == "__main__":
    processar_dados()