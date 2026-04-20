from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models import Tarefa, Usuario, Status, Lembrete
from schemas import TarefaSchema, TarefaResponse
from dependecies import pegar_sessão, verificar_token

order_router = APIRouter(prefix="/tarefas", tags=["tarefas"])

LEMBRETES = {l.value: l for l in Lembrete}


@order_router.post("/", response_model=TarefaResponse, status_code=201)
async def criar_tarefa(
    dados: TarefaSchema,
    session: Session = Depends(pegar_sessão),
    usuario: Usuario = Depends(verificar_token),
):
    lembrete_enum = LEMBRETES.get(dados.lembrete, Lembrete.NENHUM)
    tarefa = Tarefa(
        titulo=dados.titulo,
        descricao=dados.descricao,
        usuario_id=usuario.id,
        lembrete=lembrete_enum,
        data_vencimento=dados.data_vencimento,
    )
    session.add(tarefa)
    session.commit()
    session.refresh(tarefa)
    return tarefa


@order_router.get("/", response_model=List[TarefaResponse])
async def listar_tarefas(
    session: Session = Depends(pegar_sessão),
    usuario: Usuario = Depends(verificar_token),
):
    return session.query(Tarefa).filter(Tarefa.usuario_id == usuario.id).all()


@order_router.post("/{id_tarefa}/concluir", response_model=TarefaResponse)
async def concluir_tarefa(
    id_tarefa: int,
    session: Session = Depends(pegar_sessão),
    usuario: Usuario = Depends(verificar_token),
):
    tarefa = session.query(Tarefa).filter(Tarefa.id == id_tarefa, Tarefa.usuario_id == usuario.id).first()
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    if tarefa.status == Status.CONCLUIDA:
        raise HTTPException(status_code=400, detail="Tarefa já está concluída")
    tarefa.status = Status.CONCLUIDA
    session.commit()
    session.refresh(tarefa)
    return tarefa


@order_router.post("/{id_tarefa}/cancelar", response_model=TarefaResponse)
async def cancelar_tarefa(
    id_tarefa: int,
    session: Session = Depends(pegar_sessão),
    usuario: Usuario = Depends(verificar_token),
):
    tarefa = session.query(Tarefa).filter(Tarefa.id == id_tarefa, Tarefa.usuario_id == usuario.id).first()
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    if tarefa.status == Status.CANCELADA:
        raise HTTPException(status_code=400, detail="Tarefa já está cancelada")
    tarefa.status = Status.CANCELADA
    session.commit()
    session.refresh(tarefa)
    return tarefa
