# TaskFlow - Gerenciador de Tarefas

Aplicação full-stack de gerenciamento de tarefas com autenticação JWT, construída com FastAPI no backend e HTML/CSS/JavaScript puro no frontend.

## Funcionalidades

- Cadastro e login de usuários com autenticação JWT
- Criar, visualizar e organizar tarefas
- Definir status das tarefas: Pendente, Concluída ou Cancelada
- Configurar lembretes: Nenhum, Diário, Semanal ou Mensal
- Definir data de vencimento com detecção automática de atraso
- Filtrar tarefas por status na sidebar
- Visualizar resumo estatístico das tarefas

## Tecnologias

**Backend**
- Python 3.10+
- FastAPI
- SQLAlchemy (SQLite)
- JWT com `python-jose`
- Hash de senhas com `bcrypt` + `passlib`
- Pydantic para validação
- Uvicorn (servidor ASGI)

**Frontend**
- HTML5, CSS3 e JavaScript puro (sem frameworks)
- SPA com gerenciamento de estado via `localStorage`

## Estrutura do Projeto

```
PROJETOMEU/
├── main.py                # Ponto de entrada da aplicação FastAPI
├── config.py              # Carregamento de variáveis de ambiente
├── security.py            # Configuração do bcrypt
├── requirements.txt       # Dependências Python
├── Procfile               # Configuração para deploy no Heroku
├── models/
│   └── models.py          # Modelos ORM (Usuario, Tarefa)
├── routes/
│   ├── auth_routes.py     # Endpoints de autenticação (/auth/*)
│   └── order_routes.py    # Endpoints de tarefas (/tarefas/*)
├── schemas/
│   └── schemas.py         # Schemas Pydantic
├── dependecies/
│   └── dependecies.py     # Dependências FastAPI (sessão, token)
└── frontend/
    ├── index.html         # Interface principal
    ├── app.js             # Lógica do frontend
    └── style.css          # Estilos
```

## Como Rodar Localmente

**1. Clone o repositório**

```bash
git clone https://github.com/KainaLeite/PROJETOMEU.git
cd PROJETOMEU
```

**2. Crie e ative um ambiente virtual**

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

**3. Instale as dependências**

```bash
pip install -r requirements.txt
```

**4. Configure as variáveis de ambiente**

```bash
cp .env.example .env
```

Edite o `.env` com seus valores (veja a seção abaixo).

**5. Inicie o servidor**

```bash
uvicorn main:app --reload
```

A aplicação estará disponível em `http://localhost:8000`.

- Frontend: `http://localhost:8000/`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Variáveis de Ambiente

| Variável                    | Descrição                              | Padrão |
|-----------------------------|----------------------------------------|--------|
| `SECRET_KEY`                | Chave secreta para assinar os tokens JWT | —      |
| `ALGORITHM`                 | Algoritmo JWT                          | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tempo de expiração do token (minutos) | `30`   |

## Endpoints da API

### Autenticação (`/auth`)

| Método | Rota              | Descrição              | Auth |
|--------|-------------------|------------------------|------|
| POST   | `/auth/cadastro`  | Cadastrar novo usuário | Não  |
| POST   | `/auth/login`     | Login (JSON)           | Não  |
| POST   | `/auth/login-form`| Login (form, Swagger)  | Não  |

### Tarefas (`/tarefas`)

| Método | Rota                            | Descrição              | Auth |
|--------|---------------------------------|------------------------|------|
| POST   | `/tarefas/`                     | Criar tarefa           | Sim  |
| GET    | `/tarefas/`                     | Listar tarefas         | Sim  |
| POST   | `/tarefas/{id}/concluir`        | Marcar como concluída  | Sim  |
| POST   | `/tarefas/{id}/cancelar`        | Marcar como cancelada  | Sim  |

## Deploy

### Heroku

```bash
heroku create
git push heroku main
```

## Banco de Dados

SQLite local (`usuarios.db`), criado automaticamente na primeira execução.
