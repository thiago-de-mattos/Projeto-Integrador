from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from rolepermissions.roles import assign_role, remove_role, get_user_roles
from .models import *

User = get_user_model()

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome_fantasia', 'cidade', 'tipo_empresa', 'associada_acjogos')
    search_fields = ('nome_fantasia', 'cnpj', 'cidade')
    list_filter = ('tipo_empresa', 'associada_acjogos')

@admin.register(Accounts)
class AccountsAdmin(admin.ModelAdmin):
    list_display = ('nome', 'empresa', 'cargo')
    search_fields = ('nome', 'empresa')

@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'empresa', 'status', 'data_lancamento')
    list_filter = ('status',)
    search_fields = ('titulo',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo_usuario')
    list_filter = ('tipo_usuario',)


@admin.register(Profissional)
class ProfissionalAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'email', 'cidade_residencia')
    search_fields = ('nome_completo', 'email')


@admin.register(VinculoProfissionalEmpresa)
class VinculoAdmin(admin.ModelAdmin):
    list_display = ('profissional', 'empresa', 'cargo', 'status_aprovacao')
    list_filter = ('status_aprovacao',)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'mostrar_cargo',
        'is_active'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active')

    def mostrar_cargo(self, obj):
        roles = get_user_roles(obj)
        if roles:
            return ', '.join([r.get_name() for r in roles])
        return '(Sem cargo)'
    mostrar_cargo.short_description = 'Cargo'

    actions = (
        'tornar_diretoria',
        'tornar_associado',
        'tornar_afiliado',
        'tornar_coletivo',
        'remover_cargo',
    )

    def _limpar_roles(self, user):
        for role in get_user_roles(user):
            remove_role(user, role)

    def tornar_diretoria(self, request, queryset):
        for user in queryset:
            self._limpar_roles(user)
            assign_role(user, 'diretoria')
        self.message_user(request, f'{queryset.count()} usuário(s) atualizados.')
    tornar_diretoria.short_description = 'Tornar Diretoria'

    def tornar_associado(self, request, queryset):
        for user in queryset:
            self._limpar_roles(user)
            assign_role(user, 'associado')
        self.message_user(request, f'{queryset.count()} usuário(s) atualizados.')
    tornar_associado.short_description = 'Tornar Associado'

    def tornar_afiliado(self, request, queryset):
        for user in queryset:
            self._limpar_roles(user)
            assign_role(user, 'afiliado')
        self.message_user(request, f'{queryset.count()} usuário(s) atualizados.')
    tornar_afiliado.short_description = 'Tornar Afiliado'

    def tornar_coletivo(self, request, queryset):
        for user in queryset:
            self._limpar_roles(user)
            assign_role(user, 'coletivo')
        self.message_user(request, f'{queryset.count()} usuário(s) atualizados.')
    tornar_coletivo.short_description = 'Tornar Coletivo'

    def remover_cargo(self, request, queryset):
        for user in queryset:
            self._limpar_roles(user)
        self.message_user(request, f'Cargo removido de {queryset.count()} usuário(s).')
    remover_cargo.short_description = 'Remover Cargo'