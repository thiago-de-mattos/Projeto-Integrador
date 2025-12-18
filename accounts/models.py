from django.db import models
from django.contrib.auth.models import User

class Accounts(models.Model):
    nome = models.CharField(max_length=200, verbose_name='Nome')
    cargo = models.CharField(max_length=200, verbose_name='Cargo')
    empresa = models.CharField(max_length=200, verbose_name='Empresa')

class User(models.Model):
    is_diretoria = models.BooleanField(default=False, verbose_name='Diretoria')
    is_associado = models.BooleanField(default=False, verbose_name='Associado')
    is_afiliado = models.BooleanField(default=False, verbose_name='Afiliado')

    def __str__(self):
        return self.titulo