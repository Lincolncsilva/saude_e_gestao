#!/usr/bin/env python3
from datetime import datetime
from pathlib import Path
import sys

from coleta_dados import Dowload_arquivos
from processar_dados import processar_dados
from validar_dados import validar_positivo, validar_razao_social


def log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def validar_item(dado: dict) -> tuple[bool, str]:
    for k in ("razao_social", "total", "media", "desvio"):
        if k not in dado:
            return False, f"chave ausente: {k}"

    razao = dado.get("razao_social")
    total = dado.get("total")
    media = dado.get("media")
    desvio = dado.get("desvio")

    if not isinstance(razao, str) or not razao.strip():
        return False, "razao_social inválida"
    if callable(validar_razao_social) and not validar_razao_social(razao):
        return False, "razao_social reprovada na validação"

    for campo, valor in (("total", total), ("media", media), ("desvio", desvio)):
        try:
            v = float(valor)
        except Exception:
            return False, f"{campo} não é numérico: {valor!r}"

        if callable(validar_positivo) and not validar_positivo(v) and campo != "desvio":
            return False, f"{campo} não passou em validar_positivo: {v}"

        if campo == "desvio" and v < 0:
            return False, f"desvio negativo: {v}"

    return True, "ok"


def assert_file(path: Path, min_bytes: int = 10) -> None:
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
        dados_estatisticos = processar_dados() or []
        log(f"Processamento retornou {len(dados_estatisticos)} registros")

        log("Etapa 3/4 — Verificação de módulos de validação")
        log(f" - validar_positivo disponível: {callable(validar_positivo)}")
        log(f" - validar_razao_social disponível: {callable(validar_razao_social)}")

        # Se quiser: validar e logar rejeições (sem travar o pipeline)
        rejeitados = 0
        for i, dado in enumerate(dados_estatisticos, start=1):
            ok, motivo = validar_item(dado)
            if not ok:
                rejeitados += 1
                log(f"[SKIP] Registro #{i} rejeitado: {motivo}")

        log(f"Validação concluída. Rejeitados={rejeitados}")

        log("Etapa 4/4 — Verificação dos arquivos para importação (COPY → RAW)")
        # Esses caminhos precisam bater com o seu 01_importacao.sql:
        # /data/processed/2025/consolidado_despesas.csv
        # /data/processed/despesas_agregadas.csv
        base = Path("/app/Data/processed")
        assert_file(base / "despesas_agregadas.csv")

        base_2025 = base / "2025"
        assert_file(base_2025 / "consolidado_despesas.csv")

        log("ARQUIVOS OK — importer pode executar COPY para RAW")
        log("PIPELINE FINALIZADO COM SUCESSO")
        return 0

    except Exception as e:
        log(f"ERRO CRÍTICO NO PIPELINE: {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
