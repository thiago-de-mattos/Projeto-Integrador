from django.shortcuts import render,  redirect, get_object_or_404
from .models import CustomUser
from django.contrib.auth import authenticate,login as login_django
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from rolepermissions.roles import assign_role
from rolepermissions.checkers import get_user_roles
from rolepermissions.decorators import has_role_decorator
from .models import Accounts
from .forms import EmpresaForm,ProjetosForm
from .models import Empresas

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields

def cadastro(request):
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('login')
        
        else:
            messages.error(request, 'Houve um erro no cadastro. Verifique os campos.')

    else:
        form = CustomUserCreationForm()
    context = {'form': form}
    
    return render(request, 'cadastro.html', context)
        

def login_view(request):
    if request.method=='GET':
        return render(request, 'login.html')
    else:
        username=request.POST.get('username')
        senha=request.POST.get('senha')
        
        if not username or not senha:
            messages.error(request,'Preencha os campos')
            return render(request,'login.html')
        
        user=authenticate(username=username,password=senha)
        
        if user:
            login_django(request,user)
            print(f"DEBUG: Usuário {user.username} logado com sucesso!")
            return redirect('home')
        
        else:
            messages.error(request, 'Usuário ou senha inválidos')
            return render(request, 'login.html')

@login_required(login_url="login")
def home(request):
    username=request.POST.get('username')
    
    #para saber quais permiçoes tem
    try:
        permicoes = list(get_user_roles(request.user))
        permicoes_limpa = permicoes[0].get_name().replace('_','').title()
    except:
        permicoes_limpa = ""
    
    contagem = Accounts.objects.count() 
    
    context = {
        'username': request.user.username, 
        'permicoes': permicoes_limpa,
        'total_contas': contagem
    }
    
    return render(request, "home.html", context) 
    

#Usuario de teste para permissoes

def Teste_Diretoria(request):
    username = "Vitor"
    password = "123456789"
    user, created = CustomUser.objects.get_or_create(username=username)
    if created:
        user.set_password(password)
        user.is_staff = False
        user.is_superuser = False
        user.save()
        
        assign_role(user, 'diretoria')
        #assign_role(user, "gerente")
        
        return HttpResponse("Usuario de teste criado")
    else:
        return HttpResponse("Usuario de teste ja criado")
    
@login_required(login_url="login")
@has_role_decorator('diretoria')
def visao_diretoria(request):
    """ Busca todos os registros no banco de dados e permite ver e editar tudo. """
    contas = Accounts.objects.all()

    try:
        permicoes = list(get_user_roles(request.user))
        permicoes_limpa = permicoes[0].get_name().replace('_','').title()
    except:
        permicoes_limpa = ""
    
    context = {
        'contas': contas,
        'username': request.user.username,
        'permicoes': permicoes_limpa
        }
    
    return render(request, 'visao_diretoria.html', context)

def cadastro_empresas(request):
    if request.method=='POST':
        form=EmpresaForm(request.POST)
        if form.is_valid():
            empresa=form.save()
            
            messages.success(request,f"Empresa {empresa.nome} cadastrada")
            return redirect('empresas')
        else:
            messages.error(request,'Corrija os erros abaixo')
    else:
        form=EmpresaForm()
    
    return render(request,'empresas.html',{'form':form})

@login_required(login_url="login")
def listagem_empresas(request):
    empresas=Empresas.objects.all()
    
    context = {
        'empresas':empresas
    }
    return render(request,'listagem_empresas.html',context)


@login_required(login_url="login")
def editar_empresas(request,pk):
    empresas=get_object_or_404(Empresas,pk=pk)
    
    if request.method=='POST':
        form=EmpresaForm(request.POST,instance=empresas)
        
        if form.is_valid():
            form.save()
            messages.success(request,f'Empresa {empresas.nome} Atualizada com sucesso')
            return redirect('listagem_empresas')
        else:
            messages.error(request,"Corrija os Erros")
    else:
        form=EmpresaForm(instance=empresas)
        
    context={
        'form':form,
        'empresas':empresas
    }
    return render(request,'editar_empresas.html',context)




def cadastro_projetos(request):
        if request.method=='POST':
            form=ProjetosForm(request.POST)
            if form.is_valid():
                projetos=form.save()
            
                messages.success(request,f"Projetos {projetos.nome} cadastrada")
                return redirect('projetos')
            else:
                messages.error(request,'Corrija os erros abaixo')
        else:
            form=ProjetosForm()
    
        return render(request,'projetos.html',{'form':form})
    
