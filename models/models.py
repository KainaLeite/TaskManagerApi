from sqlalchemy import Column, ForeignKey, Integer, String, Date, create_engine, Enum as SAEnum
from sqlalchemy.orm import declarative_base
from enum import Enum
import uuid


class Status(Enum):
    PENDENTE  = "Pendente"
    CONCLUIDA = "Concluída"
    CANCELADA = "Cancelada"


class Lembrete(Enum):
    NENHUM   = "Nenhum"
    DIARIO   = "Diário"
    SEMANAL  = "Semanal"
    MENSAL   = "Mensal"


import os
_db_path = "/tmp/usuarios.db" if os.getenv("VERCEL") else "usuarios.db"
db = create_engine(f"sqlite:///{_db_path}")
Base = declarative_base()


class Usuario(Base):
    __tablename__ = "usuarios"
    id    = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nome  = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    senha = Column(String, nullable=False)

    def __init__(self, nome, email, senha):
        self.id    = str(uuid.uuid4())
        self.nome  = nome
        self.email = email
        self.senha = senha


class Tarefa(Base):
    __tablename__ = "tarefas"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    titulo          = Column(String, nullable=False)
    descricao       = Column(String)
    status          = Column(SAEnum(Status),   nullable=False, default=Status.PENDENTE)
    lembrete        = Column(SAEnum(Lembrete), nullable=False, default=Lembrete.NENHUM)
    data_vencimento = Column(Date, nullable=True)
    usuario_id      = Column(String, ForeignKey("usuarios.id"), nullable=False)

    def __init__(self, titulo, descricao, usuario_id, lembrete=Lembrete.NENHUM, data_vencimento=None):
        self.titulo          = titulo
        self.descricao       = descricao
        self.usuario_id      = usuario_id
        self.status          = Status.PENDENTE
        self.lembrete        = lembrete
        self.data_vencimento = data_vencimento
