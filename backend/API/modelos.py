from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    SmallInteger,
    String,
    Text,
    CHAR,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    Index,
)
from sqlalchemy.sql import func
from backend.API.db import Base


class Operadoras(Base):
    __tablename__ = "operadoras"
    __table_args__ = {"schema": "app"}

    # PK no DDL: operadora_id bigint GENERATED ALWAYS AS IDENTITY
    operadora_id = Column(BigInteger, primary_key=True, autoincrement=True)

    # chaves de negócio
    registro_operadora = Column(String(20), unique=True, nullable=False)
    cnpj = Column(String(14), unique=True, nullable=False)

    # dados cadastrais
    razao_social = Column(Text, nullable=False)
    nome_fantasia = Column(Text)
    modalidade = Column(Text)

    # endereço
    logradouro = Column(Text)
    numero = Column(Text)
    complemento = Column(Text)
    bairro = Column(Text)
    cidade = Column(Text)
    uf = Column(CHAR(2))
    cep = Column(String(8))

    # contato
    ddd = Column(String(3))
    telefone = Column(String(30))
    fax = Column(String(30))
    endereco_eletronico = Column(Text)

    # representante
    representante = Column(Text)
    cargo_representante = Column(Text)

    # metadados ANS
    regiao_de_comercializacao = Column(SmallInteger)
    data_registro_ans = Column(Date)

    # controle
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# Índices (opcional no ORM; no seu SQL já existem.
# Só defina aqui se você pretende gerar schema via ORM, o que não parece ser o caso.)
Index("operadoras_uf_idx", Operadoras.uf)
Index("operadoras_razao_idx", Operadoras.razao_social)
Index("operadoras_modalidade_idx", Operadoras.modalidade)


class DespesasConsolidadas(Base):
    __tablename__ = "despesas_consolidadas"
    __table_args__ = {"schema": "app"}

    # PK composta no DDL
    operadora_id = Column(
        BigInteger,
        ForeignKey("app.operadoras_ans.operadora_id", onupdate="CASCADE", ondelete="RESTRICT"),
        primary_key=True,
        nullable=False,
    )
    ano = Column(SmallInteger, primary_key=True, nullable=False)
    trimestre = Column(SmallInteger, primary_key=True, nullable=False)

    valor_despesas = Column(Numeric(18, 2), nullable=False)
    loaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


Index("despesas_cons_periodo_idx", DespesasConsolidadas.ano, DespesasConsolidadas.trimestre)
Index("despesas_cons_operadora_idx", DespesasConsolidadas.operadora_id)


class DespesasAgregadas(Base):
    __tablename__ = "despesas_agregadas"
    __table_args__ = {"schema": "app"}

    # PK no DDL: agg_id bigserial
    agg_id = Column(BigInteger, primary_key=True, autoincrement=True)

    operadora_id = Column(
        BigInteger,
        ForeignKey("app.operadoras_ans.operadora_id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )

    razao_social = Column(Text, nullable=False)
    uf = Column(CHAR(2))

    total_despesas = Column(Numeric(18, 2))
    media_trimestral = Column(Numeric(18, 2))
    desvio_padrao_despesas = Column(Numeric(18, 2))

    loaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


Index("despesas_agg_uf_idx", DespesasAgregadas.uf)
Index("despesas_agg_operadora_idx", DespesasAgregadas.operadora_id)
Index("despesas_agg_razao_idx", DespesasAgregadas.razao_social)
