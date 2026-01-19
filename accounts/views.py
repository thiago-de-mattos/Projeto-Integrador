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
from .forms import EmpresaForm, EstudioForm, ProjetosForm, ProfileForm,ResponsavelForm
from .models import Empresa, Profile, DadosAnuaisEmpresa, Projeto, Estudios,Responsavel_Empresa
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
        permicoes_limpa = ""
    
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
    username = "Teste"
    password = "123456789"
    user, created = CustomUser.objects.get_or_create(username=username)
    if created:
        user.set_password(password)
        user.is_staff = False
        user.is_superuser = False
        user.save()
        
        assign_role(user, 'diretoria')
        #assign_role(user, "gerente")
        
        return HttpResponse("Usuario de teste criado Usuario:Teste Senha:123456789")
    else:
        return HttpResponse("Usuario de teste ja criado Usuario:Teste Senha:123456789")
    
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
@login_required(login_url="login")
def cadastro_empresa(request):
    """Passo 1: Cadastra os dados da empresa"""
    if request.method == 'POST':
        form = EmpresaForm(request.POST, request.FILES)
        if form.is_valid():
            empresa = form.save()
            
            # Vincula empresa ao perfil do usuário
            perfil, _ = Profile.objects.get_or_create(user=request.user)
            perfil.empresa = empresa
            perfil.save()
            
            # Armazena o ID da empresa na sessão para usar no próximo passo
            request.session['empresa_id'] = empresa.id
            
            messages.success(request, f"Empresa {empresa.nome_fantasia} cadastrada com sucesso!")
            
            # Redireciona para o cadastro do responsável
            return redirect('cadastro_responsavel_empresa')
        else:
            print("FORM ERRORS:", form.errors)
            messages.error(request, "Erro no formulário. Verifique os campos.")
    else:
        form = EmpresaForm()
    
    return render(request, 'empresas.html', {'form': form})


@login_required(login_url="login")
def listagem_empresas(request):
    perfil, _ = Profile.objects.get_or_create(user=request.user)

    if perfil.empresa_id:
        empresas = Empresa.objects.filter(id=perfil.empresa_id)
        estudios = Estudios.objects.filter(empresa_id=perfil.empresa_id)
        responsaveis = Responsavel_Empresa.objects.all()
        projetos = Projeto.objects.filter(empresas__empresa=perfil.empresa)
    else:
        empresas = Empresa.objects.none()
        estudios = Estudios.objects.none()
        responsaveis = Responsavel_Empresa.objects.none()
        projetos = Projeto.objects.none()

    return render(request, 'listagem_empresas.html', {
        'empresas': empresas,
        'estudios': estudios,
        'responsaveis': responsaveis,
        'projetos': projetos,
    })

@login_required(login_url="login")
def cadastro_estudio(request):
    perfil, _ = Profile.objects.get_or_create(user=request.user)

    if not perfil.empresa_id:
        messages.error(request, "Cadastre uma empresa antes de criar um estúdio.")
        return redirect('empresas')

    if request.method == 'POST':
        form = EstudioForm(request.POST)
        if form.is_valid():
            estudio = form.save(commit=False)
            estudio.empresa_id = perfil.empresa_id

            estudio.save()
            messages.success(
                request,
                f'Estúdio {estudio.nome_do_estudio} cadastrado com sucesso!'
            )
            return redirect('listagem_empresas')
    else:
        form = EstudioForm()

    return render(request, 'estudios.html', {'form': form})


@login_required(login_url="login")
def editar_estudios(request, pk):
    estudio = get_object_or_404(Estudios, pk=pk)

    if has_role(request.user, "diretoria"):
        permitido = True
    else:
        perfil, _ = Profile.objects.get_or_create(user=request.user)
        permitido = (perfil.empresa_id == estudio.empresa_id)

    if not permitido:
        return HttpResponseForbidden("Você não pode editar este estúdio.")

    if request.method == "POST":
        form = EstudioForm(request.POST, instance=estudio)
        if form.is_valid():
            estudio_editado = form.save(commit=False)
            estudio_editado.empresa = estudio.empresa

            estudio_editado.save()
            messages.success(request, "Estúdio atualizado com sucesso.")
            return redirect("listagem_empresas")
    else:
        form = EstudioForm(instance=estudio)

    return render(request, "editar_estudios.html", {
        "form": form,
        "estudio": estudio
    })


@login_required(login_url="login")
def editar_empresas(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)

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
    # Seguindo o padrão da sua view 'cadastro_estudio'
    perfil, _ = Profile.objects.get_or_create(user=request.user)

    # Verifica se o usuário tem uma empresa vinculada
    if not perfil.empresa_id:
        messages.error(request, "Cadastre uma empresa antes de criar um projeto.")
        return redirect('cadastro_empresa')

    if request.method == 'POST':
        form = ProjetosForm(request.POST)
        if form.is_valid():
            # 1. Salva o Projeto (Tabela Projeto)
            projeto = form.save()

            # 2. Cria o Vínculo (Tabela EmpresaProjeto)
            # Como Projeto e Empresa são Muitos-para-Muitos no seu model, 
            # precisamos criar essa linha na tabela intermediária.


            messages.success(
                request, 
                f'Projeto "{projeto.titulo}" cadastrado e vinculado à sua empresa!'
            )
            return redirect('listagem_empresas')
        else:
            # Debug para ajudar você a ver erros no terminal se o form falhar
            print("ERROS NO FORM:", form.errors)
            messages.error(request, "Erro ao salvar o projeto. Verifique os campos.")
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
    
    total_empresas = Empresa.objects.count()
    empresas_ativas = Empresa.objects.filter(status_historico__status='Ativa').count()
    projetos_empresa = Projeto.objects.count()
    jogos_lancados = Projeto.objects.filter(status='Lancado').count()
   
    context = {
        'total_empresas': total_empresas,
        'empresas_ativas': empresas_ativas,
        'projetos_empresa': projetos_empresa,
        'jogos_lancados': jogos_lancados, 
    }
    
    return render(request, 'estatistica.html', context)

def estatisticas_detalhadas(request):
    dados = DadosAnuaisEmpresa.objects.all()
    profissionais_empresa = Profissional.objects.count()
     
    context = {
        'dados': dados,
        'profissionais_empresa': profissionais_empresa,
    }
    return render(request, 'estatisticas_detalhadas.html', context)

def vitrine(request):
    return render(request,'vitrine.html')


@login_required(login_url="login")
def cadastro_responsavel_empresa(request):
    """Passo 2: Cadastra o responsável da empresa"""
    
    # Verifica se existe uma empresa cadastrada na sessão
    empresa_id = request.session.get('empresa_id')
    
    if not empresa_id:
        messages.warning(request, "Cadastre primeiro uma empresa antes de adicionar o responsável.")
        return redirect('cadastro_empresa')
    
    if request.method == 'POST':
        form = ResponsavelForm(request.POST)
        if form.is_valid():
            responsavel = form.save(commit=False)
            
            # Vincula o responsável à empresa (se seu model tiver esse campo)
            # responsavel.empresa_id = empresa_id
            
            responsavel.save()
            
            # Limpa a sessão
            if 'empresa_id' in request.session:
                del request.session['empresa_id']
            
            messages.success(request, f"Responsável {responsavel.nome_completo} cadastrado com sucesso!")
            return redirect('listagem_empresas')
        else:
            print("FORM ERRORS:", form.errors)
            messages.error(request, "Erro no formulário. Verifique os campos.")
    else:
        form = ResponsavelForm()
    
    return render(request, 'responsavel_empresa.html', {'form': form})



@login_required(login_url="login")
def editar_responsavel_empresa(request, id):
    """Edita um responsável existente"""
    from django.shortcuts import get_object_or_404
    responsavel = get_object_or_404(Responsavel_Empresa, id=id)
    
    if request.method == 'POST':
        form = ResponsavelForm(request.POST, instance=responsavel)
        if form.is_valid():
            form.save()
            messages.success(request, f"Responsável {responsavel.nome_completo} atualizado com sucesso!")
            return redirect('listagem_empresas')
        else:
            messages.error(request, "Erro ao atualizar. Verifique os campos.")
    else:
        form = ResponsavelForm(instance=responsavel)
    
    return render(request, 'responsavel_empresa.html', {'form': form})
