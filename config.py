from dotenv import load_dotenv
import os
from fastapi.security import OAuth2PasswordBearer

# carrega as variáveis definidas no arquivo .env para o ambiente
load_dotenv()

# chave secreta usada para assinar e verificar os tokens JWT
SECRET_KEY = os.getenv("SECRET_KEY")

# algoritmo de criptografia usado no JWT (ex: "HS256")
ALGORITHM = os.getenv("ALGORITHM")

# tempo de expiração padrão do access token em minutos (ex: 30)
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# esquema OAuth2 que diz ao FastAPI/Swagger onde está a rota de login
# tokenUrl é a URL que o Swagger usa no botão "Authorize" para buscar o token
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login-form")
