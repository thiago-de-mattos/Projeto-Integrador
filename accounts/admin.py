from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib import messages
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from rolepermissions.roles import assign_role, remove_role, get_user_roles
from .models import *

User = get_user_model()

# ===== FORMULÁRIO CUSTOMIZADO COM VALIDAÇÃO =====
class CustomUserCreationForm(forms.ModelForm):
    """
    Formulário customizado para criação de usuários com validação de duplicatas
    """
    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmação de senha', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise ValidationError(f'O username "{username}" já está em uso.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError(f'O email "{email}" já está em uso.')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("As senhas não coincidem.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    """
    Formulário customizado para edição de usuários com validação de duplicatas
    """
    password = ReadOnlyPasswordHashField(
        label="Senha",
        help_text=(
            "Senhas são armazenadas de forma criptografada e não podem ser visualizadas. "
            "Você pode alterar a senha usando "
            "<a href=\"../password/\">este formulário</a>."
        ),
    )

    class Meta:
        model = User
        fields = '__all__'

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Se está editando, ignora o próprio usuário na verificação
        if username and User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError(f'O username "{username}" já está em uso.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Se está editando, ignora o próprio usuário na verificação
        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError(f'O email "{email}" já está em uso.')
        return email


# ===== ADMIN MODELS =====

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
    # Usa os formulários customizados
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'mostrar_cargo',
        'is_active'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    
    # Campos para o formulário de ADIÇÃO
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    
    # Campos para o formulário de EDIÇÃO
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissões', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    def mostrar_cargo(self, obj):
        roles = get_user_roles(obj)
        if roles:
            return ', '.join([r.get_name() for r in roles])
        return '(Sem cargo)'
    mostrar_cargo.short_description = 'Cargo'

    actions = (
        'tornar_diretoria',
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

    