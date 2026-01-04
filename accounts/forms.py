from django import forms
from django.core.exceptions import ValidationError
from .models import Empresas,Projetos

class EmpresaForm(forms.ModelForm):
    class Meta:
        model=Empresas
        fields="__all__"
        
        campos={
            'nome':forms.TextInput(attrs={'placeholder':'Digite o nome da empresa'}),
            'razao':forms.TextInput(attrs={'placeholder':'Digite a razão social'}),
            'cnpj':forms.TextInput(attrs={'placeholder':'Digite o CNPJ'}),
            'email':forms.EmailInput(attrs={'placeholder':'Digite o email da empresa'}),
            'telefone':forms.TextInput(attrs={'placeholder':'Digite o telefone da empresa'}),
            'site':forms.URLInput(attrs={'placeholder':'Digite o site da empresa'}),
            'endereco':forms.TextInput(attrs={'placeholder':'Digite o endereço da empresa'}),
            'cep':forms.TextInput(attrs={'placeholder':'Digite o CEP da empresa'}),
            'numero':forms.TextInput(attrs={'placeholder':'Digite o número da empresa'}),
            'complemento':forms.TextInput(attrs={'placeholder':'Digite o complemento da empresa'}),
            
            'nome_responsavel':forms.TextInput(attrs={'placeholder':'Digite o nome da empresa'}),
            'razao_responsavel':forms.TextInput(attrs={'placeholder':'Digite a razão social'}),
            'cpf_responsavel':forms.TextInput(attrs={'placeholder':'Digite o CNPJ'}),
            'email_responsavel':forms.EmailInput(attrs={'placeholder':'Digite o email da empresa'}),
            'telefone_responsavel':forms.TextInput(attrs={'placeholder':'Digite o telefone da empresa'}),
            'nick_responsavel':forms.URLInput(attrs={'placeholder':'Digite o site da empresa'}),
            'endereco_responsavel':forms.TextInput(attrs={'placeholder':'Digite o endereço da empresa'}),
            'cep_responsavel':forms.TextInput(attrs={'placeholder':'Digite o CEP da empresa'}),
            'numero_responsavel':forms.TextInput(attrs={'placeholder':'Digite o número da empresa'}),
            'complemento_responsavel':forms.TextInput(attrs={'placeholder':'Digite o complemento da empresa'}),
            }
        
        
class ProjetosForm(forms.ModelForm):
    class Meta:
        model=Projetos
        fields='__all__'
        campos={
            'nome':forms.TextInput(attrs={'placeholder':'Digite o nome da empresa'}),
            'descricao':forms.Textarea(attrs={'placeholder':'Digite o nome da empresa'}),
            'status':forms.TextInput(attrs={'placeholder':'Digite o nome da empresa'}),
            'equipe':forms.TextInput(attrs={'placeholder':'Digite o nome da empresa'}),
            'links':forms.TextInput(attrs={'placeholder':'Digite o nome da empresa'}),
            
        }

