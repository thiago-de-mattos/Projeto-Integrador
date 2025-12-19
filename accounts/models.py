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