from django.contrib import admin

from .models import Accounts

@admin.register(Accounts)
class AccountsAdmin(admin.ModelAdmin):
    list_display = ('nome', 'empresa', 'cargo') # colunas da lista
    search_fields = ('nome', 'empresa') # barra de busca