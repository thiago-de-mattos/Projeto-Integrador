from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as login_django
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseForbidden
from django.db.models import Sum, Avg, Count, Q

#
from django.http import JsonResponse
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
#

from rolepermissions.roles import assign_role
from rolepermissions.checkers import has_role, get_user_roles
from rolepermissions.decorators import has_role_decorator

from .models import (
    CustomUser, Empresa, Projeto, Accounts, Profile, 
    DadosAnuaisEmpresa, Estudios, Responsavel_Empresa, 
    Profissional, VinculoProfissionalEmpresa
    )
from .forms import (
    EmpresaForm, EstudioForm, ProjetosForm, 
    ProfileForm, ResponsavelForm
)

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields

def get_clean_role(user):
    try:
        roles = list(get_user_roles(user))
        return roles[0].get_name().replace('_', ' ').title() if roles else ""
    except:
        return ""

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
    context = {
        'username': request.user.username, 
        'permicoes': get_clean_role(request.user),
        'total_contas': Accounts.objects.count(),
        'total_empresas': Empresa.objects.count(),
        'total_projetos': Projeto.objects.count(),
        'total_estudios': Estudios.objects.count(),
    }
    return render(request, "home.html", context) 

@login_required(login_url="login")
@has_role_decorator('diretoria')
def visao_diretoria(request):

    contas = Accounts.objects.all()
    empresas = Empresa.objects.all()
    projetos = Projeto.objects.all()

    try:
        permicoes = list(get_user_roles(request.user))
        permicoes_limpa = permicoes[0].get_name().replace('_','').title()
    except:
        permicoes_limpa = ""
    
    context = {
        'contas': contas,
        'empresas': empresas,
        'projetos': projetos,
        'username': request.user.username,
        'permicoes': permicoes_limpa,
        }
    
    return render(request, 'visao_diretoria.html', context)

@login_required(login_url="login")
def cadastro_empresa(request):
    """Passo 1: Cadastra os dados da empresa"""
    if request.method == 'POST':
        form = EmpresaForm(request.POST, request.FILES)
        if form.is_valid():
            empresa = form.save()

            perfil, _ = Profile.objects.get_or_create(user=request.user)
            perfil.empresa = empresa
            perfil.save()

            request.session['empresa_id'] = empresa.id
            
            messages.success(request, f"Empresa {empresa.nome_fantasia} cadastrada com sucesso!")
 
            return redirect('cadastro_responsavel_empresa')
        else:
            print("FORM ERRORS:", form.errors)
            messages.error(request, "Erro no formulário. Verifique os campos.")
    else:
        form = EmpresaForm()
    
    return render(request, 'empresas.html', {'form': form})

@login_required(login_url="login")
def listagem_empresas(request):
    query = request.GET.get("q", "")
    cidade = request.GET.get("cidade", "")

    empresas = Empresa.objects.all()

    if query:
        empresas = empresas.filter(
            Q(nome_fantasia__icontains=query) |
            Q(razao_social__icontains=query)
        )

    if cidade:
        empresas = empresas.filter(cidade__iexact=cidade)

    cidades = (
        Empresa.objects
        .exclude(cidade__isnull=True)
        .exclude(cidade__exact="")
        .values_list("cidade", flat=True)
        .distinct()
        .order_by("cidade")
    )

    context = {
        "empresas": empresas,
        "query": query,
        "cidades": cidades,
        "cidade_selecionada": cidade,
    }

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

    perfil, _ = Profile.objects.get_or_create(user=request.user)

    if not perfil.empresa_id:
        messages.error(request, "Cadastre uma empresa antes de criar um projeto.")
        return redirect('cadastro_empresa')

    if request.method == 'POST':
        form = ProjetosForm(request.POST)
        if form.is_valid():

            projeto = form.save()

            messages.success(
                request, 
                f'Projeto "{projeto.titulo}" cadastrado e vinculado à sua empresa!'
            )
            return redirect('listagem_empresas')
        else:

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

    ano_atual = timezone.now().year
    
    total_empresas = Empresa.objects.count()
    empresas_ativas = Empresa.objects.filter(
        status_historico__status='ATIVA',
        status_historico__data_fim__isnull=True
    ).distinct().count()

    total_projetos = Projeto.objects.count()
    projetos_desenvolvimento = Projeto.objects.filter(status='DESENVOLVIMENTO').count()
    jogos_lancados = Projeto.objects.filter(status='LANCADO').count()
    
    total_profissionais = Profissional.objects.count()
    
    dados_ano_atual = DadosAnuaisEmpresa.objects.filter(ano_referencia=ano_atual)
    total_jogos_lancados_2024 = dados_ano_atual.aggregate(
        total=Sum('jogos_lancados')
    )['total'] or 0
    
    context = {
        'total_empresas': total_empresas,
        'empresas_ativas': empresas_ativas,
        'total_projetos': total_projetos,
        'projetos_lancados': jogos_lancados,
        'projetos_desenvolvimento': projetos_desenvolvimento,
        'total_profissionais': total_profissionais,
        'total_jogos_2024': total_jogos_lancados_2024,
        'ano_referencia': ano_atual,
    }
    
    return render(request, 'estatistica.html', context)

@login_required(login_url="login")
def estatisticas_detalhadas(request):
    user = request.user
    
    tem_permissao = (
        has_role(user, 'Diretoria') or
        has_role(user, 'GestorACJOGOS') or
        has_role(user, 'PoderPublico')
    )
    
    ano_atual = 2024
    
    total_empresas = Empresa.objects.count()
    empresas_ativas = Empresa.objects.filter(
        status_historico__status='ATIVA',
        status_historico__data_fim__isnull=True
    ).distinct().count()
    empresas_associadas = Empresa.objects.filter(associada_acjogos=True).count()
    
    total_projetos = Projeto.objects.count()
    projetos_por_status = Projeto.objects.values('status').annotate(
        total=Count('id')
    ).order_by('-total')
    
    total_profissionais = Profissional.objects.count()
    vinculos_ativos = VinculoProfissionalEmpresa.objects.filter(
        data_fim__isnull=True,
        status_aprovacao='APROVADO'
    ).count()
    
    dados_ano_atual = DadosAnuaisEmpresa.objects.filter(ano_referencia=ano_atual)
    
    if dados_ano_atual.exists():
        stats_ano_atual = dados_ano_atual.aggregate(
            faturamento_total=Sum('faturamento_anual'),
            faturamento_medio=Avg('faturamento_anual'),
            investimento_total=Sum('investimento_recebido'),
            total_funcionarios=Sum('numero_funcionarios'),
            total_jogos_lancados=Sum('jogos_lancados'),
            total_jogos_desenvolvimento=Sum('jogos_em_desenvolvimento'),
        )
    else:
        stats_ano_atual = {
            'faturamento_total': 0,
            'faturamento_medio': 0,
            'investimento_total': 0,
            'total_funcionarios': 0,
            'total_jogos_lancados': 0,
            'total_jogos_desenvolvimento': 0,
        }
    
    dados_por_empresa = DadosAnuaisEmpresa.objects.filter(
        ano_referencia=ano_atual
    ).select_related('empresa').order_by('-faturamento_anual')
    
    empresas_por_porte = Empresa.objects.values('porte_empresa').annotate(
        total=Count('id')
    ).order_by('-total')
    
    empresas_por_tipo = Empresa.objects.values('tipo_empresa').annotate(
        total=Count('id')
    ).order_by('-total')
    
    historico_anos = DadosAnuaisEmpresa.objects.values('ano_referencia').annotate(
        faturamento_total=Sum('faturamento_anual'),
        total_funcionarios=Sum('numero_funcionarios'),
        total_jogos_lancados=Sum('jogos_lancados')
    ).order_by('ano_referencia')
    
    context = {
        'ano_atual': ano_atual,
        'total_empresas': total_empresas,
        'empresas_ativas': empresas_ativas,
        'empresas_associadas': empresas_associadas,
        'total_projetos': total_projetos,
        'projetos_por_status': projetos_por_status,
        'total_profissionais': total_profissionais,
        'vinculos_ativos': vinculos_ativos,
        'stats_ano_atual': stats_ano_atual,
        'dados_por_empresa': dados_por_empresa,
        'empresas_por_porte': empresas_por_porte,
        'empresas_por_tipo': empresas_por_tipo,
        'historico_anos': historico_anos,
    }

    return render(request, 'estatistica_detalhada.html', context)

@login_required(login_url="login")
def vitrine_projetos(request):
    query = request.GET.get("q", "")
    genero = request.GET.get("genero", "")

    projetos = Projeto.objects.prefetch_related("empresas").all()

    if query:
        projetos = projetos.filter(
            Q(titulo__icontains=query) |
            Q(descricao__icontains=query)
        )

    if genero:
        projetos = projetos.filter(genero_principal__iexact=genero)

    generos = (
        Projeto.objects
        .exclude(genero_principal__isnull=True)
        .exclude(genero_principal__exact="")
        .values_list("genero_principal", flat=True)
        .distinct()
        .order_by("genero_principal")
    )

    context = {
        "projetos": projetos,
        "query": query,
        "generos": generos,
        "genero_selecionado": genero,
    }

    return render(request, "vitrine_projetos.html", context)

# @login_required(login_url="login")
def vitrine(request):
    return render(request, 'vitrine.html')

@login_required(login_url="login")
def cadastro_responsavel_empresa(request):

    empresa_id = request.session.get('empresa_id')
    
    if not empresa_id:
        messages.warning(request, "Cadastre primeiro uma empresa antes de adicionar o responsável.")
        return redirect('cadastro_empresa')
    
    if request.method == 'POST':
        form = ResponsavelForm(request.POST)
        if form.is_valid():
            responsavel = form.save(commit=False)

            
            responsavel.save()

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
    
    return render(request, 'editar_responsavel.html', {'form': form})

# @login_required(login_url="login")
def pagina_projeto(request):
    return render(request, 'pagina_projeto.html')

# html de teste
def home_teste(request):
    """Página inicial com empresas e projetos em destaque"""
    # Usando associada_acjogos ao invés de aprovada
    empresas_destaque = Empresa.objects.filter(
        associada_acjogos=True
    ).order_by('-data_cadastro')[:6]
    
    # Ajustar conforme seu modelo de Projeto
    projetos_destaque = Projeto.objects.all().select_related('empresa').order_by('-data_lancamento')[:4]
    
    # Estatísticas gerais
    stats = {
        'total_empresas': Empresa.objects.filter(associada_acjogos=True).count(),
        'total_projetos': Projeto.objects.count(),
        'total_cidades': Empresa.objects.filter(associada_acjogos=True).values('municipio').distinct().count(),
    }
    
    context = {
        'empresas_destaque': empresas_destaque,
        'projetos_destaque': projetos_destaque,
        'stats': stats,
    }
    return render(request, 'home_teste.html', context)


def empresas_list(request):
    """Lista todas as empresas com filtros"""
    # Removido filtro por 'aprovada' - ajuste conforme necessário
    # Se quiser filtrar apenas associadas, use: filter(associada_acjogos=True)
    empresas = Empresa.objects.all()
    
    # Filtros
    search = request.GET.get('search', '')
    cidade = request.GET.get('cidade', 'Todas')
    porte = request.GET.get('porte', 'Todos')
    tipo = request.GET.get('tipo', 'Todos')
    
    if search:
        empresas = empresas.filter(
            Q(nome__icontains=search) | 
            Q(nome_fantasia__icontains=search) |
            Q(tipo_empresa__icontains=search)
        )
    
    # Usar 'municipio' ao invés de 'cidade'
    if cidade != 'Todas':
        empresas = empresas.filter(municipio=cidade)
    
    # Usar 'porte_empresa' ao invés de 'porte'
    if porte != 'Todos':
        empresas = empresas.filter(porte_empresa=porte)
    
    # Filtro por tipo
    if tipo != 'Todos':
        empresas = empresas.filter(tipo=tipo)
    
    # Listas para filtros - usando 'municipio'
    cidades = Empresa.objects.values_list('municipio', flat=True).distinct().order_by('municipio')
    
    # Portes disponíveis - ajuste conforme suas escolhas no model
    portes = [
        ('MEI', 'MEI'),
        ('Microempresa', 'Microempresa'),
        ('Pequeno Porte', 'Pequeno Porte'),
        ('Médio Porte', 'Médio Porte'),
        ('Grande Porte', 'Grande Porte'),
    ]
    
    # Serializar para Alpine.js - usando campos corretos
    empresas_json = json.dumps(list(empresas.values(
        'id', 'nome', 'nome_fantasia', 'tipo_empresa', 'municipio', 'porte_empresa', 'associada_acjogos'
    )), default=str)
    
    context = {
        'empresas': empresas,
        'empresas_json': empresas_json,
        'cidades': cidades,
        'portes': portes,
        'selected_cidade': cidade,
        'selected_porte': porte,
        'search': search,
    }
    return render(request, 'empresa_test.html', context)


def empresa_detail(request, pk):
    """Detalhes de uma empresa específica"""
    empresa = get_object_or_404(Empresa, pk=pk)
    projetos = Projeto.objects.filter(empresa=empresa)
    
    context = {
        'empresa': empresa,
        'projetos': projetos,
    }
    return render(request, 'pages/empresa_detail.html', context)


def projetos_list(request):
    """Lista todos os projetos públicos"""
    projetos = Projeto.objects.all().select_related('empresa').order_by('-data_lancamento')
    
    # Filtros - ajuste conforme campos do seu modelo
    status = request.GET.get('status', 'Todos')
    genero = request.GET.get('genero', 'Todos')
    
    # Ajuste os filtros conforme os campos reais do seu modelo Projeto
    if status != 'Todos':
        projetos = projetos.filter(status=status)
    
    if genero != 'Todos':
        projetos = projetos.filter(genero__icontains=genero)
    
    context = {
        'projetos': projetos,
        'selected_status': status,
        'selected_genero': genero,
    }
    return render(request, 'projetos_teste.html', context)


def mapa(request):
    """Mapa interativo das empresas"""
    # Ajuste conforme os campos de latitude/longitude do seu modelo
    empresas = Empresa.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    )
    
    # Serializar coordenadas para o mapa
    empresas_coords = []
    for emp in empresas:
        empresas_coords.append({
            'nome': emp.nome,
            'cidade': emp.municipio,  # Usando municipio
            'lat': float(emp.latitude),
            'lng': float(emp.longitude),
            'porte': emp.porte_empresa,  # Usando porte_empresa
        })
    
    # Estatísticas para o mapa
    stats = {
        'regioes': 8,
        'cidades': empresas.values('municipio').distinct().count(),
        'empresas': empresas.count(),
        'profissionais': Profile.objects.filter(user__is_active=True).count(),
    }
    
    context = {
        'empresas_coords_json': json.dumps(empresas_coords),
        'stats': stats,
    }
    return render(request, 'mapa.html', context)


def estatisticas_teste(request):
    """Página de estatísticas do ecossistema"""
    empresas = Empresa.objects.all()
    
    # Estatísticas gerais
    stats = {
        'crescimento_anual': 23,
        'faturamento_estimado': '45M',
        'total_profissionais': Profile.objects.filter(user__is_active=True).count(),
        'total_empresas': empresas.count(),
    }
    
    # Distribuição por porte - usando porte_empresa
    por_porte = {}
    portes_choices = [
        'MEI', 'Microempresa', 'Pequeno Porte', 'Médio Porte', 'Grande Porte'
    ]
    for porte in portes_choices:
        por_porte[porte] = empresas.filter(porte_empresa=porte).count()
    
    # Distribuição por cidade (top 5) - usando municipio
    por_cidade = empresas.values('municipio').annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    # Distribuição por tipo de empresa
    por_tipo = {}
    tipos = empresas.values_list('tipo_empresa', flat=True).distinct()
    for tipo in tipos:
        if tipo:
            por_tipo[tipo] = empresas.filter(tipo_empresa=tipo).count()
    
    context = {
        'stats': stats,
        'por_porte': por_porte,
        'por_cidade': list(por_cidade),
        'por_tipo': por_tipo,
    }
    return render(request, 'estatisticas_teste.html', context)


def logout_view(request):
    """Logout do usuário"""
    logout(request)
    return redirect('home_teste')


# API endpoints (opcional, para AJAX)
def api_empresas(request):
    """API JSON para empresas"""
    empresas = Empresa.objects.all().values(
        'id', 'nome', 'nome_fantasia', 'tipo_empresa', 'municipio', 
        'porte_empresa', 'latitude', 'longitude'
    )
    return JsonResponse(list(empresas), safe=False)


def api_stats(request):
    """API JSON para estatísticas"""
    stats = {
        'total_empresas': Empresa.objects.count(),
        'total_projetos': Projeto.objects.count(),
        'total_profissionais': Profile.objects.filter(user__is_active=True).count(),
        'crescimento': 23,
    }
    return JsonResponse(stats)


def login_view_teste(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            user = None

        if user:
            login(request, user)
            return redirect("inicio")
        else:
            return render(request, "login_teste.html", {
                "error": "E-mail ou senha inválidos"
            })

    return render(request, "login_teste.html")


def register_view_teste(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            return render(request, "cadastro_teste.html", {
                "error": "As senhas não coincidem"
            })

        if User.objects.filter(email=email).exists():
            return render(request, "cadastro_teste.html", {
                "error": "Este e-mail já está cadastrado"
            })

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        login(request, user)
        return redirect("inicio")

    return render(request, "cadastro_teste.html")