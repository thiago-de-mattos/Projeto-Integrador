from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin.sites import NotRegistered
from rolepermissions.roles import assign_role, remove_role, get_user_roles
from .models import Accounts

@admin.register(Accounts)
class AccountsAdmin(admin.ModelAdmin):
    list_display = ('nome', 'empresa', 'cargo') # colunas da lista
    search_fields = ('nome', 'empresa') # barra de busca
    
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'mostrar_cargo', 'is_active']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    
    def mostrar_cargo(self, obj):
        roles = get_user_roles(obj)
        if roles:
            return ', '.join([r.get_name() for r in roles])
        return '(Sem cargo)'
    mostrar_cargo.short_descripition = 'cargo'
    
    actions = [
        'tornar_diretoria',
        'tornar_associado',
        'tornar_afiliado',
        'tornar_coletivo',
        'tornar_cargo'
    ]

    def tornar_diretoria(self, request, queryset):
        for user in queryset:
            for role in get_user_roles(user):
                remove_role(user, role)
            assign_role(user, 'Diretoria')
            
        self.message_user(request, f'{queryset.count()}')
    tornar_diretoria.short_descripition = 'Tonar Diretoria'
    
    def tornar_associado(self, request, queryset):
        for user in queryset:
            for role in get_user_roles(user):
                remove_role(user, role)
            assign_role(user, 'Associado')
            
        self.message_user(request, f'{queryset.count()}')
    tornar_associado.short_descripition = 'Tonar Associado'

    def tornar_afiliado(self, request, queryset):
        for user in queryset:
            for role in get_user_roles(user):
                remove_role(user, role)
            assign_role(user, 'Afiliado')
            
        self.message_user(request, f'{queryset.count()}')
    tornar_afiliado.short_descripition = 'Tonar Afiliado'
    
    def tornar_coletivo(self, request, queryset):
        for user in queryset:
            for role in get_user_roles(user):
                remove_role(user, role)
            assign_role(user, 'Coletivo')
            
        self.message_user(request, f'{queryset.count()}')
    tornar_coletivo.short_descripition = 'Tonar Coletivo'
    
    def remover_cargo(self, request, queryset):
        for user in queryset:
            for role in get_user_roles(user):
                remove_role(user, role)
            
        self.message_user(request, f'cargo Removido {queryset.count()} usuário(s)')
    remover_cargo.short_descripition = 'Reomover Cargo'

try:
    admin.site.unregister(User)
except NotRegistered:
    pass

admin.site.register(User, UserAdmin)