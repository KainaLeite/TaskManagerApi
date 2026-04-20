from passlib.context import CryptContext

# cria o contexto de criptografia usando o algoritmo bcrypt
# bcrypt é um algoritmo seguro para armazenar senhas — ele gera um hash diferente a cada vez
# "deprecated='auto'" garante que hashes antigos sejam atualizados automaticamente
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
