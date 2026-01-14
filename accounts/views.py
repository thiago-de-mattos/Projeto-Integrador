from django.shortcuts import render,  redirect, get_object_or_404
from .models import CustomUser
from django.contrib.auth import authenticate,login as login_django
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from rolepermissions.roles import assign_role
from rolepermissions.checkers import has_role, get_user_roles
from rolepermissions.decorators import has_role_decorator
from .models import Accounts
from .forms import EmpresaForm,ProjetosForm, ProfileForm
from .models import Empresa, Profile, DadosAnuaisEmpresa, Projeto
from django.http import HttpResponseForbidden


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
        permicoes_limpa = "Visitante"
    
    contagem = Accounts.objects.count() 
    total_empresas = Empresa.objects.count()
    total_projetos = Projeto.objects.count()

    context = {
        'username': request.user.username, 
        'permicoes': permicoes_limpa,
        'total_contas': contagem,
        'total_empresas': total_empresas,
        'total_projetos': total_projetos,
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

@login_required(login_url= "login")
def cadastro_empresa(request):
    if request.method == 'POST':
        form = EmpresaForm(request.POST, request.FILES)
        if form.is_valid():
            empresa = form.save()
            
            perfil, _ = Profile.objects.get_or_create(user=request.user)
            perfil.empresa = empresa
            perfil.save()
            
            messages.success(request, f"Empresa {empresa.nome_fantasia} cadastra e vinculada no usuario")
            return redirect('listagem_empresas')
        else:
            print("FORM ERRORS:", form.errors)
            messages.error(request, f"Erro no formulário: {form.errors}")
    else:
        form = EmpresaForm()
    return render(request, 'empresas.html', {'form': form})
    
@login_required(login_url="login")
def listagem_empresas(request):
    perfil, _ = Profile.objects.get_or_create(user=request.user)

    if perfil.empresa_id:
        empresas = Empresa.objects.filter(id=perfil.empresa_id)
    else:
        empresas = Empresa.objects.none()

    
    context = {
        'empresas':empresas
    }
    return render(request,'listagem_empresas.html',context)


@login_required(login_url="login")
def editar_empresas(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)

    # diretoria pode editar qualquer uma
    if has_role(request.user, "diretoria"):
        permitido = True
    else:
        perfil, _ = Profile.objects.get_or_create(user=request.user)
        permitido = (perfil.empresa_id == empresa.id)

    if not permitido:
        return HttpResponseForbidden("Você não pode editar essa empresa.")

    if request.method == "POST":
        form = EmpresaForm(request.POST, request.FILES, instance=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, "Empresa atualizada com sucesso.")
            return redirect("listagem_empresas")
        else:
            messages.error(request, f"Erro no formulário: {form.errors}")
    else:
        form = EmpresaForm(instance=empresa)

    return render(request, "editar_empresas.html", {"form": form, "empresa": empresa})

@login_required(login_url="login")
def cadastro_projetos(request):
    if request.method == 'POST':
        form = ProjetosForm(request.POST)
        if form.is_valid():
            projetos = form.save()
            messages.success(request, f"Projeto {projetos} cadastrado")
            return redirect('projetos')
        else:
            messages.error(request, 'Corrija os erros abaixo')
    else:
        form = ProjetosForm()

    return render(request, 'projetos.html', {'form': form})

@login_required(login_url="login")
def editar_meu_perfil(request):
    perfil, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado com sucesso.")
            return redirect("home")
        else:
            messages.error(request, f"Erro no formulário: {form.errors}")
    else:
        form = ProfileForm(instance=perfil)

    return render(request, "editar_perfil.html", {"form": form, "perfil": perfil})

@login_required(login_url="login")
def editar_minha_empresa(request):
    perfil, _ = Profile.objects.get_or_create(user=request.user)

    if not perfil.empresa_id:
        return HttpResponseForbidden("Você não tem empresa vinculada ao seu usuário.")

    empresa = get_object_or_404(Empresa, pk=perfil.empresa_id)

    if request.method == "POST":
        form = EmpresaForm(request.POST, request.FILES, instance=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, "Empresa atualizada com sucesso.")
            return redirect("home")
        else:
            messages.error(request, f"Erro no formulário: {form.errors}")
    else:
        form = EmpresaForm(instance=empresa)

    return render(request, "editar_empresas.html", {"form": form, "empresa": empresa})

@login_required(login_url="login")

def estatistica(request):
    dados = DadosAnuaisEmpresa.objects.all()
    
    if dados.empresa_id:
        empresas = Empresa.objects.filter(id=DadosAnuaisEmpresa.empresa_id)
    else:
        empresas = Empresa.objects.none()

    context = {
        'empresas': empresas,
        'dados': dados,
    }
    
    return render(request, 'estatistica.html', context)


def vitrine(request):
    return render(request,'vitrine.html')

