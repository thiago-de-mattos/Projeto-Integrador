from django import forms
from django.core.exceptions import ValidationError
from .models import Empresa, Projeto, Profile, Responsavel_Empresa, Profissional, EntidadeParceira
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

# 🔐 IMPORT DO CRIPTOGRAFADOR
from .criptografador import encrypt_cpf, decrypt_cpf, encrypt_cnpj, decrypt_cnpj

User = get_user_model()


class ResponsavelForm(forms.ModelForm):
    class Meta:
        model = Responsavel_Empresa
        fields = [
            'nome_completo','nome_social','cpf','email','telefone',
            'nick_discord','cep','endereco','numero','complemento',
        ]

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')

        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        if len(cpf_limpo) != 11:
            raise forms.ValidationError('CPF deve conter 11 dígitos.')

        return cpf 


def save(self, commit=True):
    obj = super().save(commit=False)
    obj.cpf = encrypt_cpf(obj.cpf)

    if commit:
        obj.save()
    return obj


class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = "__all__"


class ProjetosForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = ['titulo', 'descricao', 'status', 'equipe_projeto', 'url_site']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["telefone_contato", "foto_perfil"]


class CadastroForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class CadastroEmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = [
            'nome_fantasia','razao_social','cnpj','telefone','site',
            'cep','endereco_completo','cidade','tipo_empresa','porte_empresa',
            'data_fundacao'
        ]

def clean_cnpj(self):
    cnpj = self.cleaned_data.get('cnpj')

    # valida formato antes
    if not re.match(r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$', cnpj):
        raise forms.ValidationError('CNPJ inválido. Use 00.000.000/0000-00')

    cnpj_limpo = ''.join(filter(str.isdigit, cnpj))

    if len(cnpj_limpo) != 14:
        raise forms.ValidationError('CNPJ deve ter 14 dígitos')

    cnpj_criptografado = encrypt_cnpj(cnpj_limpo)

    if Empresa.objects.filter(cnpj=cnpj_criptografado).exists():
        raise forms.ValidationError('Este CNPJ já está cadastrado')

    return cnpj_criptografado
class CadastroProfissionalForm(forms.ModelForm):
    class Meta:
        model = Profissional
        fields = [
            'nome_completo','cpf','telefone','cidade_residencia',
            'data_nascimento','tempo_experiencia','portfolio_url',
            'linkedin','github','behance','biografia'
        ]
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')

        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        if len(cpf_limpo) != 11:
            raise forms.ValidationError('CPF deve ter 11 dígitos')

        return cpf  


    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.cpf = encrypt_cpf(obj.cpf)

        if commit:
            obj.save()
        return obj


class EntidadeParceiraForm(forms.ModelForm):
    class Meta:
        model = EntidadeParceira
        fields = ['nome','tipo','cnpj','telefone','endereco','descricao']

    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj')

        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        if len(cnpj_limpo) != 14:
            raise forms.ValidationError('CNPJ inválido')

        return cnpj 


    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.cnpj = encrypt_cnpj(obj.cnpj)

        if commit:
            obj.save()
        return obj


class UsuarioBaseForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está em uso.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('As senhas não coincidem.')

        if password:
            validate_password(password)

        return cleaned_data
