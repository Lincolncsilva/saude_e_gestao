from fastapi import FastAPI, Depends, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from backend.API.db import get_db
from backend.API.modelos import Operadoras as Operadora
from backend.API.modelos import DespesasConsolidadas as DespesaConsolidada
from backend.API.modelos import DespesasAgregadas as DespesaAgregada
from backend.API.schemas import EstatisticaResponse, DespesaIndividual, OperadoraCNPJSchema
from typing import List, Optional
from sqlalchemy import or_, cast, String, exists
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
        query = query.filter(
            exists().where(DespesaConsolidada.operadora_id == Operadora.operadora_id)
        )

    # (seu filtro por q continua igual)
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
    # Agrupa por UF e soma as despesas
    # Nota: Assumindo que a tabela Operadora tem 'uf' e a Despesa tem 'valor'
    # Se os nomes forem diferentes no seu modelo, ajuste aqui
    resultados = (
        db.query(Operadora.uf, func.sum(DespesaConsolidada.valor).label("total"))
        .join(DespesaConsolidada, Operadora.operadora_id == DespesaConsolidada.operadora_id)
        .group_by(Operadora.uf)
        .all()
    )
    
    return [{"uf": r.uf, "total": float(r.total)} for r in resultados]