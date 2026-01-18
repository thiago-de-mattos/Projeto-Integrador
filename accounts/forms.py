from django import forms
from django.core.exceptions import ValidationError
from .models import Empresa, Projeto, Profile, Estudios, Responsavel_Empresa
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class ResponsavelForm(forms.ModelForm):
    class Meta:
        model =  Responsavel_Empresa
        fields = [
            'nome_completo',
            'nome_social',
            'cpf',
            'email',
            'telefone',
            'nick_discord',
            'cep',
            'endereco',
            'numero',
            'complemento',
        ]
        
        widgets = {
            'nome_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome completo',
                'required': True
            }),
            'nome_social': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome social (opcional)'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00',
                'maxlength': '14',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com',
                'required': True
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000',
                'maxlength': '15',
                'required': True
            }),
            'nick_discord': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'usuario#1234'
            }),
            'cep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-000',
                'maxlength': '9',
                'required': True
            }),
            'endereco': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Rua, Avenida, etc.',
                'required': True
            }),
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nº',
                'maxlength': '10',
                'required': True
            }),
            'complemento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apto, Bloco, etc. (opcional)'
            }),
        }
        
        labels = {
            'nome_completo': 'Nome Completo',
            'nome_social': 'Nome Social (opcional)',
            'cpf': 'CPF',
            'email': 'E-mail de Contato',
            'telefone': 'Telefone',
            'nick_discord': 'Nick no Discord',
            'cep': 'CEP',
            'endereco': 'Endereço',
            'numero': 'Número',
            'complemento': 'Complemento',
        }
    
    # def clean_cpf(self):
    #     """Limpa e valida CPF"""
    #     cpf = self.cleaned_data.get('cpf')
    #     # Remove caracteres não numéricos
    #     cpf_limpo = ''.join(filter(str.isdigit, cpf))
        
    #     if len(cpf_limpo) != 11:
    #         raise forms.ValidationError('CPF deve conter 11 dígitos.')
        
    #     # Valida CPF básico (verifica se todos os dígitos são iguais)
    #     if cpf_limpo == cpf_limpo[0] * 11:
    #         raise forms.ValidationError('CPF inválido.')
        
    #     return cpf
    
    # def clean_cep(self):
    #     """Limpa e valida CEP"""
    #     cep = self.cleaned_data.get('cep')
    #     cep_limpo = ''.join(filter(str.isdigit, cep))
        
    #     if len(cep_limpo) != 8:
    #         raise forms.ValidationError('CEP deve conter 8 dígitos.')
        
    #     return cep
    
    # def clean_telefone(self):
    #     """Limpa e valida telefone"""
    #     telefone = self.cleaned_data.get('telefone')
    #     telefone_limpo = ''.join(filter(str.isdigit, telefone))
        
    #     if len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
    #         raise forms.ValidationError('Telefone deve ter 10 ou 11 dígitos (DDD + número).')
        
    #     return telefone
    
    # def clean_email(self):
    #     """Valida e-mail único (exceto para o próprio registro)"""
    #     email = self.cleaned_data.get('email')
        
    #     # Verifica se já existe outro responsável com este e-mail
    #     if self.instance.pk:
    #         # Editando - exclui o próprio registro da verificação
    #         if Responsavel_Empresa.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
    #             raise forms.ValidationError('Este e-mail já está cadastrado.')
    #     else:
    #         # Criando novo
    #         if Responsavel_Empresa.objects.filter(email=email).exists():
    #             raise forms.ValidationError('Este e-mail já está cadastrado.')
        
    #     return email


class EmpresaForm(forms.ModelForm):
    class Meta:
        model=Empresa
        fields="__all__"
        
        widgets={
            'nome_fantasia':forms.TextInput(attrs={'placeholder':'Digite o nome da empresa'}),
            'razao_social':forms.TextInput(attrs={'placeholder':'Digite a razão social'}),
            'cnpj':forms.TextInput(attrs={'placeholder':'Digite o CNPJ'}),
            'email':forms.EmailInput(attrs={'placeholder':'Digite o email da empresa'}),
            'telefone':forms.TextInput(attrs={'placeholder':'Digite o telefone da empresa'}),
            'site':forms.TextInput(attrs={'placeholder':'Digite o site da empresa'}),
            'endereco_completo':forms.TextInput(attrs={'placeholder':'Digite o endereço da empresa'}),
            'cep':forms.TextInput(attrs={'placeholder':'Digite o CEP da empresa'}),
            'cidade':forms.TextInput(attrs={'placeholder':'Digite a cidade da empresa'}),
            'complemento':forms.TextInput(attrs={'placeholder':'Digite o complemento da empresa'}),
            }

class EstudioForm(forms.ModelForm):
    class Meta:
        model = Estudios
        fields = [
            'nome_do_estudio',
            'email',
            'telefone',
            'endereco',
        ]

        widgets={
            'nome_do_estudio':forms.TextInput(attrs={'placeholder':'Digite o nome da empresa'}),
            'email':forms.EmailInput(attrs={'placeholder':'Digite o email da empresa'}),
            'telefone':forms.TextInput(attrs={'placeholder':'Digite o telefone da empresa'}),
            'endereco':forms.TextInput(attrs={'placeholder':'Digite o endereco da empresa'}),
            }
        
        
class ProjetosForm(forms.ModelForm):
    class Meta:
        model = Projeto
        # Liste apenas os campos que estão no seu formulário HTML
        fields = ['titulo', 'descricao', 'status', 'equipe_projeto', 'url_site']
        
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Projeto'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'equipe_projeto': forms.TextInput(attrs={'class': 'form-control'}), # Mudei para TextInput para bater com o Model
            'url_site': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["telefone_contato", "foto_perfil"]

class CadastroForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']