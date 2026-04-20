from typing import Optional
from datetime import date
from pydantic import BaseModel, EmailStr, field_validator


class UsuarioSchema(BaseModel):
    nome:  str
    email: EmailStr
    senha: str

    class Config:
        from_attributes = True


class LoginSchema(BaseModel):
    email: EmailStr
    senha: str

    class Config:
        from_attributes = True


class TarefaSchema(BaseModel):
    titulo:          str
    descricao:       Optional[str]  = None
    lembrete:        Optional[str]  = "Nenhum"
    data_vencimento: Optional[date] = None

    class Config:
        from_attributes = True


class TarefaResponse(BaseModel):
    id:              int
    titulo:          str
    descricao:       Optional[str]  = None
    status:          str
    lembrete:        str
    data_vencimento: Optional[date] = None

    @field_validator("status", "lembrete", mode="before")
    @classmethod
    def converter_enum(cls, v):
        return getattr(v, "value", str(v))

    class Config:
        from_attributes = True
