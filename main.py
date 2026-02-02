#!/usr/bin/env python3
import os
import sys
import pandas as pd
from datetime import datetime
from pathlib import Path

from coleta_dados import Dowload_arquivos
from processar_dados import processar_dados
from validar_dados import validar_positivo, validar_razao_social

# Configuração de caminhos (deve ser o mesmo do seu processar_dados.py)
PROC_DIR = Path("./Data/processed")

def log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def validar_item(dado: dict) -> tuple[bool, str]:
    # Ajustado para bater com as chaves do seu DataFrame agregado
    # Mapeamento: Total_Despesas -> total, Media_Trimestral -> media, Desvio_Padrao_Despesas -> desvio
    mapeamento = {
        "razao_social": dado.get("RazaoSocial"),
        "total": dado.get("Total_Despesas"),
        "media": dado.get("Media_Trimestral"),
        "desvio": dado.get("Desvio_Padrao_Despesas")
    }

    for k, v in mapeamento.items():
        if v is None and k != "desvio":
            return False, f"chave ou valor ausente: {k}"

    razao = mapeamento["razao_social"]
    total = mapeamento["total"]
    media = mapeamento["media"]
    desvio = mapeamento["desvio"]

    if not isinstance(razao, str) or not razao.strip():
        return False, "razao_social inválida"
    
    if callable(validar_razao_social) and not validar_razao_social(razao):
        return False, "razao_social reprovada na validação"

    for campo, valor in (("total", total), ("media", media), ("desvio", desvio)):
        try:
            v = float(valor)
        except (ValueError, TypeError):
            return False, f"{campo} não é numérico: {valor!r}"

        if callable(validar_positivo) and not validar_positivo(v) and campo != "desvio":
            return False, f"{campo} não passou em validar_positivo: {v}"

        if campo == "desvio" and v < 0:
            return False, f"desvio negativo: {v}"

    return True, "ok"

def assert_file(path: Path, min_bytes: int = 100) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    size = path.stat().st_size
    if size < min_bytes:
        raise ValueError(f"Arquivo vazio/pequeno demais: {path} ({size} bytes)")

def main() -> int:
    try:
        log("PIPELINE INICIADO")

        log("Etapa 1/4 — Coleta de dados")
        Dowload_arquivos()

        log("Etapa 2/4 — Processamento de dados")
        dados_estatisticos = processar_dados()

        # Tratamento para Processamento Incremental (Checkpoint)
        if dados_estatisticos is None:
            caminho_agregado = PROC_DIR / "despesas_agregadas.csv"
            if not caminho_agregado.exists():
                log("ERRO: Nenhum dado processado e arquivos consolidados não encontrados.")
                return 1
            else:
                log("Aviso: Nenhum dado novo, usando arquivos processados anteriormente.")
                df_temp = pd.read_csv(caminho_agregado)
                dados_estatisticos = df_temp.to_dict('records')
        
        qtd_registros = len(dados_estatisticos)
        log(f"Processamento retornou {qtd_registros} registros")

        if qtd_registros == 0:
            log("ERRO: O processamento resultou em 0 registros. Abortando.")
            return 1

        log("Etapa 3/4 — Verificação de módulos de validação")
        log(f" - validar_positivo disponível: {callable(validar_positivo)}")
        log(f" - validar_razao_social disponível: {callable(validar_razao_social)}")

        rejeitados = 0
        for i, dado in enumerate(dados_estatisticos, start=1):
            ok, motivo = validar_item(dado)
            if not ok:
                rejeitados += 1
                # Logar apenas os primeiros erros para não poluir o console
                if rejeitados <= 5:
                    log(f"[SKIP] Registro #{i} rejeitado: {motivo}")

        log(f"Validação concluída. Rejeitados={rejeitados}")

        log("Etapa 4/4 — Verificação dos arquivos para importação (COPY → RAW)")
        # Caminhos baseados na estrutura de volumes do seu Docker
        base = Path("/app/Data/processed")
        assert_file(base / "despesas_agregadas.csv")

        # Verifica se existe alguma pasta de ano com o consolidado
        # (Busca dinâmica para evitar erro se o ano mudar)
        arquivos_consolidados = list(base.glob("**/consolidado_despesas.csv"))
        if not arquivos_consolidados:
            raise FileNotFoundError("consolidado_despesas.csv não encontrado em nenhuma subpasta de ano.")
        
        for f in arquivos_consolidados:
            assert_file(f)
            log(f"Arquivo verificado: {f}")

        log("ARQUIVOS OK — containers de importação podem prosseguir")
        log("PIPELINE FINALIZADO COM SUCESSO")
        return 0

    except Exception as e:
        log(f"ERRO CRÍTICO NO PIPELINE: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())