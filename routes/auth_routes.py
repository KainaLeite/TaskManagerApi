from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Usuario
from dependecies import pegar_sessão
from schemas import UsuarioSchema, LoginSchema
from security import bcrypt_context
from jose import jwt
from datetime import datetime, timedelta, timezone
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordRequestForm

auth_router = APIRouter(prefix="/auth", tags=["auth"])


def criar_token(id_usuario):
    expiracao = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(id_usuario), "exp": expiracao}, SECRET_KEY, algorithm=ALGORITHM)


@auth_router.post("/cadastro", status_code=201)
async def cadastro(dados: UsuarioSchema, session: Session = Depends(pegar_sessão)):
    if session.query(Usuario).filter(Usuario.email == dados.email).first():
        raise HTTPException(status_code=409, detail="Email já cadastrado")
    novo_usuario = Usuario(dados.nome, dados.email, bcrypt_context.hash(dados.senha))
    session.add(novo_usuario)
    session.commit()
    return {"mensagem": f"Usuário {dados.email} cadastrado com sucesso"}


@auth_router.post("/login")
async def login(dados: LoginSchema, session: Session = Depends(pegar_sessão)):
    usuario = session.query(Usuario).filter(Usuario.email == dados.email).first()
    if not usuario or not bcrypt_context.verify(dados.senha, usuario.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    return {"access_token": criar_token(usuario.id), "token_type": "bearer"}


@auth_router.post("/login-form")
async def login_form(dados: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessão)):
    usuario = session.query(Usuario).filter(Usuario.email == dados.username).first()
    if not usuario or not bcrypt_context.verify(dados.password, usuario.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    return {"access_token": criar_token(usuario.id), "token_type": "bearer"}
