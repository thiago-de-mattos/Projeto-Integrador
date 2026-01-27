from cryptography.fernet import Fernet
from django.conf import settings

fernet = Fernet(settings.FERNET_KEY)



def encrypt_cpf(valor: str) -> str:
    return fernet.encrypt(valor.encode()).decode()

def decrypt_cpf(valor: str) -> str:
    return fernet.decrypt(valor.encode()).decode()



def encrypt_cnpj(valor: str) -> str:
    return fernet.encrypt(valor.encode()).decode()

def decrypt_cnpj(valor: str) -> str:
    return fernet.decrypt(valor.encode()).decode()
