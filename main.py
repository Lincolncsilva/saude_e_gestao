#!/usr/bin/env python3

from datetime import datetime
import sys

# Importa suas funções diretamente
from coleta_dados import Dowload_arquivos
from processar_dados import processar_dados
from validar_dados import validar_cnpj, validar_positivo, validar_razao_social


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def main():
    try:
        log("PIPELINE INICIADO")

        log("Etapa 1/3 — Coleta de dados")
        Dowload_arquivos()

        log("Etapa 2/3 — Processamento de dados")
        processar_dados()

        log("Etapa 3/3 — Validações disponíveis (importadas)")
        log("Funções de validação carregadas:")
        log(f" - validar_cnpj: {callable(validar_cnpj)}")
        log(f" - validar_positivo: {callable(validar_positivo)}")
        log(f" - validar_razao_social: {callable(validar_razao_social)}")

        log("PIPELINE FINALIZADO COM SUCESSO")
        return 0

    except Exception as e:
        log(f"ERRO NO PIPELINE: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
