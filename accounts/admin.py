from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from rolepermissions.roles import assign_role, remove_role, get_user_roles
from .models import Accounts

User = get_user_model()


@admin.register(Accounts)
class AccountsAdmin(admin.ModelAdmin):
    list_display = ('nome', 'empresa', 'cargo')
    search_fields = ('nome', 'empresa')


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
