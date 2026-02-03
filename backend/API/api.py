from fastapi import FastAPI, Depends, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from backend.API.db import get_db
from backend.API.modelos import Operadoras as Operadora
from backend.API.modelos import DespesasConsolidadas as DespesaConsolidada
from backend.API.modelos import DespesasAgregadas as DespesaAgregada
from backend.API.schemas import EstatisticaResponse, DespesaIndividual, OperadoraCNPJSchema
from typing import List, Optional, Dict
from sqlalchemy import or_, cast, String, exists, and_, func, desc
import re

app = FastAPI(title="ANS Data API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em produção, restrinja
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. LISTA OPERADORAS COM PAGINAÇÃO ---


@app.get("/api/operadoras")
def listar_operadoras(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    q: str = Query(None),
    has_despesas: bool = Query(False),
    db: Session = Depends(get_db),
):
    query = db.query(Operadora)

    # ✅ filtro: só operadoras que existem na tabela de despesas
    if has_despesas:
        despesas_exists = (
            db.query(DespesaConsolidada.operadora_id)
            .filter(
                and_(
                    DespesaConsolidada.operadora_id == Operadora.operadora_id,
                    DespesaConsolidada.valor_despesas > 0
                )
            )
            .correlate(Operadora)   # ✅ força correlação com Operadora
            .exists()
        )
        query = query.filter(despesas_exists)  # ← MOVER PARA DENTRO DO IF

    if q:
        query = query.filter(
            or_(
                Operadora.razao_social.ilike(f"%{q}%"),
                Operadora.cnpj.like(f"%{q}%")
            )
        )

    total_registros = query.count()

    skip = (page - 1) * limit
    operadoras = (
        query.order_by(Operadora.razao_social.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    total_paginas = (total_registros + limit - 1) // limit if total_registros > 0 else 1

    return {
        "data": operadoras,
        "meta": {
            "total": total_registros,
            "page": page,
            "limit": limit,
            "total_pages": total_paginas,
        },
    }

# --- 2. DETALHES DE UMA OPERADORA ESPECÍFICA ---
@app.get("/api/operadoras/{cnpj}", response_model=OperadoraCNPJSchema)
def buscar_operadora(cnpj: str, db: Session = Depends(get_db)):
    cnpj_limpo = "".join(ch for ch in cnpj if ch.isdigit())
    operadora = db.query(Operadora).filter(Operadora.cnpj == cnpj_limpo).first()
    if not operadora:
        raise HTTPException(status_code=404, detail="Operadora não encontrada")
    return operadora

# --- 3. HISTÓRICO DE DESPESAS DA OPERADORA ---
@app.get("/api/operadoras/{cnpj}/despesas", response_model=List[DespesaIndividual])
def historico_despesas(
    cnpj: str,
    db: Session = Depends(get_db),
):
    cnpj_limpo = "".join(ch for ch in cnpj if ch.isdigit())

    operadora = db.query(Operadora).filter(Operadora.cnpj == cnpj_limpo).first()
    if not operadora:
        raise HTTPException(status_code=404, detail="Operadora não encontrada")

    despesas = (
        db.query(DespesaConsolidada)
        .filter(DespesaConsolidada.operadora_id == operadora.operadora_id)
        .order_by(
            DespesaConsolidada.ano.asc(),
            DespesaConsolidada.trimestre.asc(),
        )
        .all()
    )
    return despesas


# --- 4. ESTATÍSTICAS GERAIS (DADOS AGREGADOS) ---
@app.get("/api/estatisticas", response_model= List[EstatisticaResponse])
def obter_estatisticas(db: Session = Depends(get_db)):
    stats = (
        db.query(DespesaAgregada)
        .order_by(DespesaAgregada.total_despesas.desc()).limit(5).all()
    )
    return stats


@app.get("/api/estatisticas/uf")
def despesas_por_uf(db: Session = Depends(get_db)):
    # Soma das despesas por UF (somando todas as operadoras)
    rows = (
        db.query(
            Operadora.uf.label("uf"),
            func.coalesce(func.sum(DespesaConsolidada.valor_despesas), 0).label("total")
        )
        .join(DespesaConsolidada, DespesaConsolidada.operadora_id == Operadora.operadora_id)
        .filter(Operadora.uf.isnot(None))
        .group_by(Operadora.uf)
        .all()
    )

    return [{"uf": r.uf, "total": float(r.total or 0)} for r in rows]

@app.get("/api/estatisticas/uf/{uf}")
def detalhes_por_uf(uf: str, db: Session = Depends(get_db)):
    uf = uf.strip().upper()
    if len(uf) != 2:
        raise HTTPException(status_code=400, detail="UF inválida")

    # Total do estado - ADICIONE FILTRO valor_despesas > 0
    total_uf = (
        db.query(func.sum(DespesaConsolidada.valor_despesas))
        .join(Operadora, Operadora.operadora_id == DespesaConsolidada.operadora_id)
        .filter(
            Operadora.uf == uf,
            DespesaConsolidada.valor_despesas > 0  # ← AQUI
        )
        .scalar()
    ) or 0

    # Top 5 operadoras por gasto no estado
    top5 = (
        db.query(
            Operadora.operadora_id,
            Operadora.razao_social,
            Operadora.cnpj,
            func.sum(DespesaConsolidada.valor_despesas).label("total")
        )
        .join(DespesaConsolidada, DespesaConsolidada.operadora_id == Operadora.operadora_id)
        .filter(
            Operadora.uf == uf,
            DespesaConsolidada.valor_despesas > 0  # ← AQUI
        )
        .group_by(Operadora.operadora_id, Operadora.razao_social, Operadora.cnpj)
        .order_by(desc(func.sum(DespesaConsolidada.valor_despesas)))  # ← CORRIGIDO
        .limit(5)
        .all()
    )

    return {
        "uf": uf,
        "total_uf": float(total_uf),
        "top5": [
            {
                "operadora_id": r.operadora_id,
                "razao_social": r.razao_social,
                "cnpj": r.cnpj,
                "total": float(r.total or 0),
            }
            for r in top5
        ],
    }