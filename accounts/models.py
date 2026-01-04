from django.db import models
from django.contrib.auth.models import AbstractUser

class Accounts(models.Model):
    nome = models.CharField(max_length=200, verbose_name='Nome')
    cargo = models.CharField(max_length=200, verbose_name='Cargo')
    empresa = models.CharField(max_length=200, verbose_name='Empresa')

class CustomUser(AbstractUser):
    pass

    def __str__(self):
        return self.username
    

class Empresas(models.Model):
    nome=models.CharField(max_length=150)
    
    razao=models.CharField(max_length=150)
    
    cnpj=models.CharField(max_length=18,unique=True)
    
    email=models.EmailField(unique=True)
    
    telefone=models.CharField(max_length=15)
    
    site=models.CharField()
    
    endereco=models.CharField(max_length=150)
    
    cep=models.CharField(max_length=9)
    
    numero=models.CharField(max_length=9)
    
    complemento=models.CharField(max_length=150)
    
    
    nome_responsavel=models.CharField(max_length=150)
    
    razao_responsavel=models.CharField(max_length=150)
    
    cpf_responsavel=models.CharField(max_length=18,unique=True)
    
    email_responsavel=models.EmailField(unique=True)
    
    telefone_responsavel=models.CharField(max_length=15)
    
    nick_responsavel=models.CharField()
    
    endereco_responsavel=models.CharField(max_length=150)
    
    cep_responsavel=models.CharField(max_length=9)
    
    numero_responsavel=models.CharField(max_length=9)
    
    complemento_responsavel=models.CharField(max_length=150)
    
class Projetos(models.Model):
    
    nome=models.CharField(max_length=150)
    
    descricao=models.TextField(max_length=450)
    
    status=models.CharField(max_length=150)
    
    equipe=models.CharField(max_length=150)
    
    links=models.CharField(max_length=150)