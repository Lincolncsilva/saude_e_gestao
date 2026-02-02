from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from backend.API.db import get_db
from backend.API.modelos import Operadoras as Operadora
from backend.API.modelos import DespesasConsolidadas as DespesaConsolidada
from backend.API.modelos import DespesasAgregadas as DespesaAgregada
from backend.API.schemas import EstatisticaResponse, DespesaIndividual, OperadoraCNPJSchema
from typing import List
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
    db: Session = Depends(get_db),
):
    # 1. Calculamos o total antes de aplicar o limite (essencial para o meta)
    total_registros = db.query(Operadora).count()
    
    skip = (page - 1) * limit
    operadoras = (
        db.query(Operadora)
        .order_by(Operadora.operadora_id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # 2. Calculamos o total de páginas
    total_paginas = (total_registros + limit - 1) // limit

    # 3. Retornamos o dicionário (o "envelope")
    return {
        "data": operadoras,
        "meta": {
            "total": total_registros,
            "page": page,
            "limit": limit,
            "total_pages": total_paginas
        }
    }

    
    return operadoras

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
            DespesaConsolidada.ano.desc(),
            DespesaConsolidada.trimestre.desc(),
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
