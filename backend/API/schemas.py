from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional



class OperadoraCNPJSchema(BaseModel):
    # --- Identificação ---
    operadora_id: int
    registro_operadora: str
    cnpj: str = Field(..., min_length=14, max_length=14)
    razao_social: str
    nome_fantasia: Optional[str] = None
    modalidade: str
    data_registro_ans: date
    regiao_de_comercializacao: int
    
    # --- Localização ---
    logradouro: str
    numero: str
    complemento: Optional[str] = None
    bairro: str
    cidade: str
    uf: str = Field(..., min_length=2, max_length=2)
    cep: str
    
    # --- Contato ---
    ddd: Optional[str] = None
    telefone: Optional[str] = None
    fax: Optional[str] = None
    endereco_eletronico: Optional[str] = None
    
    # --- Gestão ---
    representante: str
    cargo_representante: str
    
    # --- Sistema ---
    created_at: datetime

    class Config:
        from_attributes = True # Permite mapeamento direto de objetos do banco (SQLAlchemy)

class DespesaIndividual(BaseModel):
    operadora_id: int
    ano: int
    trimestre: int
    valor_despesas: float |None
    loaded_at: datetime

class EstatisticaResponse(BaseModel):
    agg_id: int
    operadora_id: int | None
    razao_social: str
    uf: str | None
    total_despesas: float | None
    media_trimestral: float | None
    desvio_padrao_despesas: float | None
    loaded_at: datetime

    class Config:
        from_attributes = True
