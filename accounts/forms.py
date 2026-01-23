from django import forms
from django.core.exceptions import ValidationError
from .models import Empresa, Projeto, Profile, Estudios, Responsavel_Empresa, Profissional
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()



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
        model = Empresa
        fields = "__all__"
        
        widgets = {
            'nome_fantasia': forms.TextInput(attrs={'placeholder': 'Digite o nome da empresa'}),
            'razao_social': forms.TextInput(attrs={'placeholder': 'Digite a razão social'}),
            'cnpj': forms.TextInput(attrs={'placeholder': 'Digite o CNPJ'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Digite o email da empresa'}),
            'telefone': forms.TextInput(attrs={'placeholder': 'Digite o telefone'}),
            'site': forms.TextInput(attrs={'placeholder': 'Digite o site'}),
            'endereco_completo': forms.TextInput(attrs={'placeholder': 'Digite o endereço'}),
            'cep': forms.TextInput(attrs={'placeholder': 'Digite o CEP'}),
            'cidade': forms.TextInput(attrs={'placeholder': 'Digite a cidade'}),
            'complemento': forms.TextInput(attrs={'placeholder': 'Digite o complemento'}),
            'data_fundacao':forms.TextInput(attrs={'placeholder': 'Ex:dd/mm/aaaa'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Este loop adiciona automaticamente a classe 'form-input' a todos os campos
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})

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




# Pedro veja se isto esta correto e se vc vai aproveitar isso.  
class CadastroEmpresaForm(forms.ModelForm):
    """Formulário de cadastro de empresa"""
    
    # Campos de acesso (User)
    email = forms.EmailField(
        label='Email de Acesso',
        widget=forms.EmailInput(attrs={
            'placeholder': 'contato@suaempresa.com',
            'class': 'form-control'
        })
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Mínimo 8 caracteres',
            'class': 'form-control'
        }),
        min_length=8,
        help_text='Use letras, números e caracteres especiais'
    )
    
    class Meta:
        model = Empresa
        fields = [
            'nome_fantasia', 'razao_social', 'cnpj', 'telefone', 'site',
            'cep', 'endereco_completo', 'cidade', 'latitude', 'longitude',
            'tipo_empresa', 'porte_empresa', 'data_fundacao', 'arranjo_produtivo'
        ]
        widgets = {
            'nome_fantasia': forms.TextInput(attrs={
                'placeholder': 'Ex: Pixel Studios',
                'class': 'form-control'
            }),
            'razao_social': forms.TextInput(attrs={
                'placeholder': 'Ex: Pixel Studios LTDA',
                'class': 'form-control'
            }),
            'cnpj': forms.TextInput(attrs={
                'placeholder': '00.000.000/0000-00',
                'class': 'form-control'
            }),
            'telefone': forms.TextInput(attrs={
                'placeholder': '(21) 98888-8888',
                'class': 'form-control'
            }),
            'site': forms.URLInput(attrs={
                'placeholder': 'https://suaempresa.com',
                'class': 'form-control'
            }),
            'cep': forms.TextInput(attrs={
                'placeholder': '00000-000',
                'class': 'form-control',
                'id': 'cep'
            }),
            'endereco_completo': forms.TextInput(attrs={
                'placeholder': 'Rua, número, complemento',
                'class': 'form-control'
            }),
            'cidade': forms.TextInput(attrs={
                'placeholder': 'Rio de Janeiro',
                'class': 'form-control'
            }),
            'latitude': forms.NumberInput(attrs={
                'placeholder': 'Será preenchido automaticamente',
                'class': 'form-control',
                'readonly': 'readonly'
            }),
            'longitude': forms.NumberInput(attrs={
                'placeholder': 'Será preenchido automaticamente',
                'class': 'form-control',
                'readonly': 'readonly'
            }),
            'tipo_empresa': forms.Select(attrs={'class': 'form-control'}),
            'porte_empresa': forms.Select(attrs={'class': 'form-control'}),
            'data_fundacao': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'arranjo_produtivo': forms.Select(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'latitude': 'Preenchido automaticamente pelo CEP',
            'longitude': 'Preenchido automaticamente pelo CEP',
        }
    
    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj')
        # Remove caracteres não numéricos
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        
        if len(cnpj_limpo) != 14:
            raise forms.ValidationError('CNPJ deve ter 14 dígitos')
        
        # Verifica se já existe
        if Empresa.objects.filter(cnpj=cnpj).exists():
            raise forms.ValidationError('Este CNPJ já está cadastrado')
        
        return cnpj
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email já está cadastrado')
        return email


class CadastroProfissionalForm(forms.ModelForm):
    """Formulário de cadastro de profissional"""
    
    # Campos de acesso (User)
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'seu@email.com',
            'class': 'form-control'
        })
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Mínimo 8 caracteres',
            'class': 'form-control'
        }),
        min_length=8,
        help_text='Use letras, números e caracteres especiais'
    )
    
    class Meta:
        model = Profissional
        fields = [
            'nome_completo', 'cpf', 'telefone', 'cidade_residencia',
            'data_nascimento', 'tempo_experiencia', 'portfolio_url',
            'linkedin', 'github', 'behance', 'biografia'
        ]
        widgets = {
            'nome_completo': forms.TextInput(attrs={
                'placeholder': 'Ex: João Silva',
                'class': 'form-control'
            }),
            'cpf': forms.TextInput(attrs={
                'placeholder': '000.000.000-00',
                'class': 'form-control'
            }),
            'telefone': forms.TextInput(attrs={
                'placeholder': '(21) 98888-8888',
                'class': 'form-control'
            }),
            'cidade_residencia': forms.TextInput(attrs={
                'placeholder': 'Rio de Janeiro',
                'class': 'form-control'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'tempo_experiencia': forms.NumberInput(attrs={
                'placeholder': 'Ex: 5',
                'min': '0',
                'class': 'form-control'
            }),
            'portfolio_url': forms.URLInput(attrs={
                'placeholder': 'https://seuportfolio.com',
                'class': 'form-control'
            }),
            'linkedin': forms.URLInput(attrs={
                'placeholder': 'https://linkedin.com/in/seuperfil',
                'class': 'form-control'
            }),
            'github': forms.URLInput(attrs={
                'placeholder': 'https://github.com/seuperfil',
                'class': 'form-control'
            }),
            'behance': forms.URLInput(attrs={
                'placeholder': 'https://behance.net/seuperfil',
                'class': 'form-control'
            }),
            'biografia': forms.Textarea(attrs={
                'placeholder': 'Conte um pouco sobre você',
                'rows': 3,
                'class': 'form-control'
            }),
        }
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        # Remove caracteres não numéricos
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        
        if len(cpf_limpo) != 11:
            raise forms.ValidationError('CPF deve ter 11 dígitos')
        
        # Verifica se já existe
        if Profissional.objects.filter(cpf=cpf).exists():
            raise forms.ValidationError('Este CPF já está cadastrado')
        
        return cpf
    
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")

        return email