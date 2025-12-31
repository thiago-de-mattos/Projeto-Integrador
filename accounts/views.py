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
    
    
    return render(request, "home.html", {'username': request.user.username, 'permicoes':permicoes_limpa}) 
    

#Usuario de teste para permissoes

def Teste(request):
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
    todas_contas = Accounts.objects.all()
    
    context = {
        'contas': todas_contas,
        'username': request.user.username
    }
    
    return render(request, 'visao_diretoria.html', context)