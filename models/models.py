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
from dotenv import load_dotenv
load_dotenv()

_turso_url   = os.getenv("TURSO_DATABASE_URL")
_turso_token = os.getenv("TURSO_AUTH_TOKEN")

if _turso_url and _turso_token:
    import asyncio
    import libsql_client as _lc

    class _Cursor:
        description = None
        rowcount = -1
        lastrowid = None

        def __init__(self): self._rows = []

        def _run(self, sql, params=()):
            _url = _turso_url.replace("libsql://", "https://")
            async def _go():
                async with _lc.create_client(_url, auth_token=_turso_token) as c:
                    return await c.execute(sql, list(params))
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(asyncio.run, _go()).result()

        def execute(self, sql, parameters=()):
            rs = self._run(sql, parameters)
            self.description = [(col, None, None, None, None, None, None) for col in rs.columns] or None
            self._rows = [tuple(r) for r in rs.rows]
            self.rowcount = getattr(rs, "rows_affected", None) if not self._rows else len(self._rows)
            self.lastrowid = getattr(rs, "last_insert_rowid", None)

        def executemany(self, sql, seq):
            for p in seq: self.execute(sql, p)

        def fetchone(self): return self._rows.pop(0) if self._rows else None
        def fetchall(self): r, self._rows = self._rows, []; return r
        def fetchmany(self, n=None): r, self._rows = self._rows[:n], self._rows[n:]; return r
        def close(self): pass

    class _Connection:
        def cursor(self): return _Cursor()
        def commit(self): pass
        def rollback(self): pass
        def close(self): pass
        def create_function(self, *a, **kw): pass

    db = create_engine("sqlite://", creator=_Connection)
# else:
#     _db_path = "/tmp/task.db" if os.getenv("VERCEL") else "task.db"
#     db = create_engine(f"sqlite:///{_db_path}")
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
