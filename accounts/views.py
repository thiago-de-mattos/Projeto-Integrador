from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Avg, Count, Q

#
import json
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, login as login_django, logout, get_user_model
User = get_user_model()
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.forms import UserCreationForm
from datetime import date

#

from rolepermissions.roles import assign_role
from rolepermissions.checkers import has_role, get_user_roles
from rolepermissions.decorators import has_role_decorator

from .models import (
    CustomUser, Empresa, Projeto, Accounts, Profile, 
    DadosAnuaisEmpresa, Responsavel_Empresa, 
    Profissional, VinculoProfissionalEmpresa
    )
from .forms import (
    EmpresaForm, ProjetosForm, 
    ProfileForm, ResponsavelForm, CadastroEmpresaForm, CadastroProfissionalForm
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

# def cadastro(request):

#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)

#         if form.is_valid():
#             user = form.save()
#             messages.success(request, 'Usuário cadastrado com sucesso!')
#             return redirect('login')
        
#         else:
#             messages.error(request, 'Houve um erro no cadastro. Verifique os campos.')

#     else:
#         form = CustomUserCreationForm()
#     context = {'form': form}
    
#     return render(request, 'cadastro.html', context)

    # Pedro veja se esse vai te servir o de cima verifique tambem veja o template empresa.html onde vc fez a logica de adicionar empresa
def cadastro_empresa(request):
    """Cadastro de empresa - Cria User + Profile + Empresa"""
    
    if request.method == 'POST':
        form = CadastroEmpresaForm(request.POST)
        
        if form.is_valid():
            try:
                # Pega o email e senha dos campos extras
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                
                # Cria o User
                username = email.split('@')[0]
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                
                # Salva a Empresa
                empresa = form.save(commit=False)
                empresa.email = email
                empresa.save()
                
                # Cria o Profile e vincula
                profile = Profile.objects.create(
                    user=user,
                    tipo_usuario='EMPRESA',
                    empresa=empresa
                )
                
                # Signal vai dar cargo "Associado" e deixar pendente
                
                messages.success(request, 'Empresa cadastrada! Aguarde aprovação da Diretoria.')
                return redirect('login')
                
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar: {str(e)}')
        else:
            # Se form inválido, mostra os erros
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CadastroEmpresaForm()
    
    context = {'form': form}
    return render(request, 'cadastro_empresa.html', context)


def cadastro_profissional(request):
    """Cadastro de profissional - Cria User + Profile + Profissional"""
    
    if request.method == 'POST':
        form = CadastroProfissionalForm(request.POST)
       
        if not form.is_valid():
            print("FORMULÁRIO INVÁLIDO!")
            print("Erros:", form.errors)
            print("Dados recebidos:", request.POST)
            
            # Adiciona mensagem de erro geral
            messages.error(
                request, 
                'Existem erros no formulário. Por favor, corrija os campos destacados abaixo.'
            )

            # Mostra cada erro individualmente (opcional - já aparece no campo)
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"  - {field}: {error}")
    
        if form.is_valid():
            try:
                # 1. Pegar dados do formulário
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                
                print(f"Criando usuário: {email}")
                
                # 2. Criar o User
                username = email.split('@')[0]
                base_username = username
                counter = 1
                
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=form.cleaned_data.get('nome_completo', '').split()[0] if form.cleaned_data.get('nome_completo') else ''
                )
                print(f"User criado: {user.username}")
                
                # 3. Atribuir role DIRETAMENTE
                assign_role(user, 'afiliado')
                print(f" Role 'afiliado' atribuída")
                
                # 4. Salvar o Profissional
                profissional = form.save(commit=False)
                profissional.user = user
                profissional.email = email
                profissional.save()
                print(f"Profissional criado: {profissional.nome_completo}")
                
                # 5. Criar o Profile
                profile = Profile.objects.create(
                    user=user,
                    tipo_usuario='PROFISSIONAL',
                    profissional=profissional
                )
                print(f"Profile criado")
                
                # 6. Mensagem de sucesso
                messages.success(
                    request, 
                    f' Cadastro realizado com sucesso! Bem-vindo(a), {profissional.nome_completo}! Você já pode fazer login.'
                )
                
                return redirect('home/diretoria/')
                
            except Exception as e:
                print(f" ERRO AO CADASTRAR: {e}")
                import traceback
                traceback.print_exc()
                
                messages.error(
                    request, 
                    f' Erro ao cadastrar: {str(e)}. Tente novamente ou entre em contato com o suporte.'
                )
    else:
        form = CadastroProfissionalForm()
    
    context = {'form': form}
    return render(request, 'cadastro_profissional.html', context)

# def login_view(request):
#     if request.method=='GET':
#         return render(request, 'login.html')
#     else:
#         username=request.POST.get('username')
#         senha=request.POST.get('senha')
        
#         if not username or not senha:
#             messages.error(request,'Preencha os campos')
#             return render(request,'login.html')
        
#         user=authenticate(username=username,password=senha)
        
#         if user:
#             login_django(request,user)
#             print(f"DEBUG: Usuário {user.username} logado com sucesso!")
#             return redirect('home')
        
#         else:
#             messages.error(request, 'Usuário ou senha inválidos')
#             return render(request, 'login.html')

@never_cache
@login_required(login_url="login")
def home(request):     
    role = get_clean_role(request.user) # Corrigido: usa request.user

    if role == 'Diretoria':
        return redirect('home_diretoria')
    elif role == 'Associado':
        return redirect('home_associado')
    elif role == 'Afiliado':
        return redirect('home_afiliado')
    elif role == 'Coletivo':
        return redirect('home_coletivo')
    
    # Se não cair em nenhum cargo específico, renderiza a home padrão sem redirecionar
    context = {
        'username': request.user.username, 
        'permicoes': role,
        'total_contas': Accounts.objects.count(),
        'total_empresas': Empresa.objects.count(),
        'total_projetos': Projeto.objects.count(),
    }
    return render(request, "home.html", context)

def Teste_Diretoria(request):
    username = "teste_diretoria"
    email = "diretoria@teste.com"
    password = "123"
    
    # 1. Criar ou buscar o usuário
    user, created = CustomUser.objects.get_or_create(username=username, defaults={'email': email})
    if created:
        user.set_password(password)
        user.save()
        assign_role(user, 'diretoria')

    # 2. Popular dados globais para a Diretoria visualizar
    # Criar uma empresa caso não exista nenhuma
    empresa_demo, _ = Empresa.objects.get_or_create(
        nome_fantasia="Empresa Global de Teste",
        defaults={'cnpj': '11.111.111/0001-11', 'cidade': 'Rio de Janeiro'}
    )

    # Criar um projeto de teste
    Projeto.objects.get_or_create(
        titulo="Projeto Alpha - Diretoria",
        empresa=empresa_demo,
        defaults={'status': 'concluido'}
    )
    
    # Criar um registro em Accounts (usado na home)
    Accounts.objects.get_or_create(
        nome="Administrador Geral",
        defaults={'cargo': 'Diretor Histórico', 'empresa': 'ACJOGOS-RJ'}
    )

    return gerar_resposta_html("Diretoria", username, email, password)

def setup_completo(request):
    """
    Cria uma massa de dados completa para teste:
    1. Diretoria e Coletivo (fixos)
    2. 5 Empresas (Associados) com projetos variados
    3. 5 Profissionais (Afiliados) com perfis variados
    """
    
    # --- 1. SETUP DIRETORIA & COLETIVO ---
    # Reaproveita a lógica existente, mas sem retornar o HTML imediatamente
    
    # Diretoria
    u_dir, _ = CustomUser.objects.get_or_create(username="diretoria_geral", defaults={'email': "diretoria@acjogos.teste"})
    u_dir.set_password("123")
    u_dir.save()
    assign_role(u_dir, 'diretoria')
    
    # Coletivo
    u_col, _ = CustomUser.objects.get_or_create(username="coletivo_geral", defaults={'email': "coletivo@acjogos.teste"})
    u_col.set_password("123")
    u_col.save()
    assign_role(u_col, 'coletivo')

    created_log = []

    # --- 2. GERADOR DE EMPRESAS (ASSOCIADOS) ---
    lista_empresas = [
        {"nome": "Pixel Rio Studio", "user": "assoc_pixel", "cidade": "Rio de Janeiro", "porte": "Pequeno Porte", "tipo": "Desenvolvedora", "projeto": "Cangaço Cyberpunk", "genero": "RPG"},
        {"nome": "Niterói Games", "user": "assoc_niteroi", "cidade": "Niterói", "porte": "Microempresa", "tipo": "Editora", "projeto": "Ponte Rio-Niterói Racer", "genero": "Corrida"},
        {"nome": "Serrana Arts", "user": "assoc_serra", "cidade": "Petrópolis", "porte": "MEI", "tipo": "Asset Store", "projeto": "Imperial City Sim", "genero": "Simulação"},
        {"nome": "Caxias Code", "user": "assoc_caxias", "cidade": "Duque de Caxias", "porte": "Médio Porte", "tipo": "Outsourcing", "projeto": "Baixada Defense", "genero": "Estratégia"},
        {"nome": "Maricá VR", "user": "assoc_marica", "cidade": "Maricá", "porte": "Pequeno Porte", "tipo": "Desenvolvedora", "projeto": "Maricá Verse", "genero": "Aventura"},
    ]

    for idx, data in enumerate(lista_empresas):
        # Cria User
        email = f"{data['user']}@teste.com"
        user, created = CustomUser.objects.get_or_create(username=data['user'], defaults={'email': email})
        if created:
            user.set_password("123")
            user.save()
            assign_role(user, 'associado')
        
        # Cria Empresa
        cnpj_falso = f"00000000000{500+idx}"
        empresa, _ = Empresa.objects.get_or_create(
            nome_fantasia=data['nome'],
            defaults={
                'razao_social': f"{data['nome']} Ltda",
                'cnpj': cnpj_falso,
                'cidade': data['cidade'], # Usando cidade conforme seu model
                'municipio': data['cidade'], # Redundância caso use municipio na vitrine
                'tipo_empresa': data['tipo'],
                'porte_empresa': data['porte'],
                'associada_acjogos': True, # Para aparecer na vitrine
                'ativo': True
            }
        )

        # Vincula Profile
        perfil, _ = Profile.objects.get_or_create(user=user)
        perfil.empresa = empresa
        perfil.save()

        # Cria Projeto
        Projeto.objects.get_or_create(
            titulo=data['projeto'],
            empresa=empresa,
            defaults={
                'nome': data['projeto'],
                'descricao': f"Um jogo incrível desenvolvido em {data['cidade']}.",
                'tipo_jogo': data['genero'],
                'genero_principal': data['genero'], # Caso use esse campo na vitrine
                'equipe_projeto': 'Equipe Principal',
                'status': 'LANCADO' if idx % 2 == 0 else 'DESENVOLVIMENTO',
                'publico_alvo': 'GERAL'
            }
        )
        created_log.append(f"Empresa criada: {data['nome']} (User: {data['user']})")

    # --- 3. GERADOR DE PROFISSIONAIS (AFILIADOS) ---
    lista_pros = [
        {"nome": "Ana Artist", "user": "afiliado_ana", "cargo": "2D Artist", "cidade": "Rio de Janeiro"},
        {"nome": "Carlos Coder", "user": "afiliado_carlos", "cargo": "Programador Unity", "cidade": "São Gonçalo"},
        {"nome": "Bruno Sound", "user": "afiliado_bruno", "cargo": "Sound Designer", "cidade": "Rio de Janeiro"},
        {"nome": "Diana Design", "user": "afiliado_diana", "cargo": "Game Designer", "cidade": "Niterói"},
    ]

    for idx, data in enumerate(lista_pros):
        email = f"{data['user']}@teste.com"
        user, created = CustomUser.objects.get_or_create(username=data['user'], defaults={'email': email})
        if created:
            user.set_password("123")
            user.save()
            assign_role(user, 'afiliado')

        # Cria Profissional
        profissional, _ = Profissional.objects.get_or_create(
            user=user,
            defaults={
                'nome_completo': data['nome'],
                'cpf': f"111.222.333-{10+idx}",
                'email': email,
                'telefone': '(21) 90000-0000',
                'cidade_residencia': data['cidade'],
                'tempo_experiencia': 3 + idx,
                'biografia': f"Sou especialista em {data['cargo']}.",
            }
        )
        created_log.append(f"Profissional criado: {data['nome']} (User: {data['user']})")

    # --- RETORNO VISUAL ---
    html_log = "".join([f"<li style='margin-bottom: 5px;'>✅ {item}</li>" for item in created_log])
    
    return HttpResponse(f"""
        <div style="font-family: Arial, sans-serif; padding: 40px; background: #0a0e1a; min-height: 100vh; color: white;">
            <h1 style="color: #19e3ff;">🚀 Banco de Dados Alimentado!</h1>
            <p>Os seguintes registros foram criados ou atualizados:</p>
            <ul style="background: #141827; padding: 20px 40px; border-radius: 10px; border: 1px solid #19e3ff;">
                <li style="color: #ffd700; font-weight: bold;">👑 Diretoria: diretoria_geral / 123</li>
                <li style="color: #ffd700; font-weight: bold;">👁️ Coletivo: coletivo_geral / 123</li>
                <hr style="border-color: #333;">
                {html_log}
            </ul>
            <br>
            <a href="/login_teste/" style="padding: 15px 30px; background: #19e3ff; color: #000; text-decoration: none; border-radius: 5px; font-weight: bold;">Ir para Login</a>
            <a href="/vitrine/" style="padding: 15px 30px; background: #333; color: #fff; text-decoration: none; border-radius: 5px; margin-left: 10px;">Ver Vitrine</a>
        </div>
    """)

def gerar_resposta_html(role_name, username, email, password):
    return HttpResponse(f"""
        <div style="font-family: Arial, sans-serif; padding: 40px; text-align: center; background: #0a0e1a; min-height: 100vh; color: white;">
            <h1 style="color: #19e3ff;">✅ Usuário {role_name} pronto!</h1>
            <div style="background: #141827; padding: 20px; border-radius: 10px; max-width: 400px; margin: 20px auto; border: 1px solid #19e3ff;">
                <p><strong style="color: #19e3ff;">Username:</strong> {username}</p>
                <p><strong style="color: #19e3ff;">E-mail:</strong> {email}</p>
                <p><strong style="color: #19e3ff;">Senha:</strong> {password}</p>
            </div>
            <a href="/login_teste/" style="display: inline-block; padding: 12px 30px; background: #19e3ff; color: #0a0e1a; text-decoration: none; border-radius: 10px; font-weight: bold;">Ir para o Login</a>
        </div>
    """)

# Ação específica para Diretoria
@login_required(login_url="login")
@has_role_decorator('diretoria')
def visao_diretoria(request):

    if request.method == 'POST' and 'aprovar_id' in request.POST:
        empresa_id = request.POST.get('aprovar_id')
        empresa = get_object_or_404(Empresa, id=empresa_id)
        empresa.ativo = True
        empresa.save()
        messages.success(request, f'Empresa {empresa.nome_fantasia} aprovada!')
        return redirect('visao_diretoria')

    contas = Accounts.objects.all()
    empresas = Empresa.objects.order_by('ativo', '-nome_fantasia') # Pendentes aparecem primeiro
    projetos = Projeto.objects.order_by('-id')

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

# Home específica para Diretoria
@login_required
@has_role_decorator('diretoria')
def home_diretoria(request):

    status_ativos = ['PLANEJAMENTO', 'DESENVOLVIMENTO', 'LANCADO']
    context = {
        'username': request.user.username,
        # Card: Empresas
        'total_empresas' : Empresa.objects.count(),
        'cadastros_pendentes' : Empresa.objects.filter(validada=False).count(),
        # Card: Projetos
        'total_projetos': Projeto.objects.count(),
        'projetos_ativos': Projeto.objects.filter(status__in=status_ativos).count(),
        'em_desenvolvimento': Projeto.objects.filter(status='DESENVOLVIMENTO').count(),
        # Card: Profissionais
        'total_profissionais': Profissional.objects.count(),
    }
    return render(request, 'home_diretoria.html', context)


# Home específica para Associados
@has_role_decorator('associado')
def home_associado(request):
    perfil = Profile.objects.filter(user=request.user).first()
    minha_empresa = perfil.empresa if perfil else None
    meus_projetos = []
    if minha_empresa:
        meus_projetos = Projeto.objects.filter(empresa=minha_empresa)
    
    context = {
        'empresa': minha_empresa,
        'projetos': meus_projetos,
        'permicoes': 'Associado'
    }
    return render(request, 'home_associado.html', context)

# Home específica para Afiliados
@has_role_decorator('afiliado')
def home_afiliado(request):
    
    perfil_profissional = Profissional.objects.filter(user=request.user).first()
    meus_vinculos = VinculoProfissionalEmpresa.objects.filter(profissional=perfil_profissional)

    # Listar TODOS os vínculos do sistema (para comparação)
    todos_vinculos = VinculoProfissionalEmpresa.objects.all()
    
    context = {
        'profissional': perfil_profissional,
        'vinculos': meus_vinculos,
        'permicoes': 'Afiliado',
        'title': 'Meu Painel de Profissional'
    }
    return render(request, 'home_afiliado.html', context)

# Home específica para Coletivo
@has_role_decorator('coletivo')
def home_coletivo(request):
    total_empresas = Empresa.objects.count()
    total_projetos = Projeto.objects.count()
    
    empresas_por_cidade = Empresa.objects.values('cidade').annotate(total=Count('id')).order_by('-total')[:5]

    context = {
        'permicoes': 'Coletivo',
        'total_empresas': total_empresas,
        'total_projetos': total_projetos,
        'ranking_cidades': empresas_por_cidade,
        'username': request.user.username,
        'titulo_painel': 'Painel de Observação Institucional'
    }
    return render(request, 'home_coletivo.html', context)

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
    
    return render(request, 'cadastro_empresas.html', {'form': form})

@login_required(login_url="login_teste")
def listagem_empresas(request):
    query = request.GET.get("q", "")
    cidade = request.GET.get("cidade", "")

    perfil, _ = Profile.objects.get_or_create(user=request.user)

    if perfil.empresa_id:
        empresas = Empresa.objects.filter(id=perfil.empresa_id)
        responsaveis = Responsavel_Empresa.objects.filter(empresa_id=perfil.empresa_id)
        projetos = Projeto.objects.filter(empresa=perfil.empresa)  # ✅ CORRETO
    else:
        empresas = Empresa.objects.none()
        responsaveis = Responsavel_Empresa.objects.none()
        projetos = Projeto.objects.none()

    cidades = (
        Empresa.objects
        .exclude(cidade__isnull=True)
        .exclude(cidade__exact="")
        .values_list("cidade", flat=True)
        .distinct()
        .order_by("cidade")
    )

    return render(request, 'listagem_empresas.html', {
        'empresas': empresas,
        'responsaveis': responsaveis,
        'projetos': projetos,
        'query': query,
        'cidades': cidades,
        'cidade_selecionada': cidade,
    })

@login_required(login_url="login")
def editar_empresas(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)

    if has_role(request.user, "diretoria"):
        permitido = True
        if request.method == 'POST':
            form = EmpresaForm(request.POST, request.FILES, instance=empresa)
            if form.is_valid():
                form.save()
                messages.success(request, "Dados da empresa atualizados!")
                return redirect('visao_diretoria')
            else:
                form = EmpresaForm(instance=empresa)

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

            projeto = form.save(commit=False)  # 👈 NÃO salva ainda
            projeto.empresa = perfil.empresa   # 👈 VINCULA A EMPRESA
            projeto.save()                      # 👈 AGORA salva

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

    return render(request, 'cadastro_projetos.html', {'form': form})


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

@login_required(login_url="login_teste")

def cadastro_responsavel_empresa(request):

    empresa_id = request.session.get('empresa_id')
    
    if not empresa_id:
        messages.warning(
            request,
            "Cadastre primeiro uma empresa antes de adicionar o responsável."
        )
        return redirect('cadastro_empresa')
    
    if request.method == 'POST':
        form = ResponsavelForm(request.POST)

        if form.is_valid():
            responsavel = form.save(commit=False)

            # 🔥 LINHA QUE FALTAVA
            responsavel.empresa = Empresa.objects.get(id=empresa_id)

            responsavel.save()

            # limpa a sessão se quiser
            del request.session['empresa_id']
            
            messages.success(
                request,
                f"Responsável {responsavel.nome_completo} cadastrado com sucesso!"
            )
            return redirect('listagem_empresas')
        else:
            print("FORM ERRORS:", form.errors)
            messages.error(request, "Erro no formulário. Verifique os campos.")
    else:
        form = ResponsavelForm()
    
    return render(request, 'cadastro_responsavel_empresa.html', {'form': form})


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
def vitrine(request):
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
    
    projetos = Projeto.objects.all().select_related('empresa').order_by('-data_lancamento')
    empresa = Empresa.objects.all()
    context = {
        'empresas_destaque': empresas_destaque,
        'projetos_destaque': projetos_destaque,
        'stats': stats,
        'projetos': projetos,
        'empresas': empresa,
        
    }
    return render(request, 'vitrine.html', context)

def empresas_vitrine(request):
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
    return render(request, 'empresa_vitrine.html', context)


def empresa_detail(request, pk):
    """Detalhes de uma empresa específica"""
    empresa = get_object_or_404(Empresa, pk=pk)
    projetos = Projeto.objects.filter(empresa=empresa)
    
    context = {
        'empresa': empresa,
        'projetos': projetos,
    }
    return render(request, 'pages/empresa_detail.html', context)


def projetos_vitrine(request):
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
    return render(request, 'projetos_vitrine.html', context)

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
    return redirect('vitrine')


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

@never_cache
def login_view_teste(request):
    # Se o usuário já está logado, redireciona para home
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            return redirect("home")  # ← Vai para a home antiga
        else:
            return render(request, "loginhtml", {
                "error": "E-mail ou senha inválidos",
                "email": email
            })

    return render(request, "login.html")


@never_cache
def register_view_teste(request):

    
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        # Validação: senhas coincidem
        if password != password2:
            return render(request, "cadastro_teste.html", {
                "error": "As senhas não coincidem",
                "username": username,
                "email": email
            })

        # Validação: email já existe
        if User.objects.filter(email=email).exists():
            return render(request, "cadastro_teste.html", {
                "error": "Este e-mail já está cadastrado",
                "username": username,
                "email": email
            })
        
        # Validação: username já existe
        if User.objects.filter(username=username).exists():
            return render(request, "cadastro_teste.html", {
                "error": "Este nome de usuário já está em uso",
                "username": username,
                "email": email
            })

        # Criar usuário com username correto
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Mensagem de sucesso
        messages.success(request, "Conta criada com sucesso! Faça login para continuar.")
        
        # Redirecionar para login (SEM fazer login automático)
        return redirect("login")

    return render(request, "cadastro.html")


@login_required(login_url="login")
def editar_projeto(request, projeto_id):
    perfil, _ = Profile.objects.get_or_create(user=request.user)

    if not perfil.empresa:
        messages.error(request, "Você precisa ter uma empresa para editar projetos.")
        return redirect('cadastro_empresa')

    projeto = get_object_or_404(
        Projeto,
        id=projeto_id,
        empresa=perfil.empresa
    )

    if request.method == 'POST':
        form = ProjetosForm(request.POST, instance=projeto)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Projeto "{projeto.titulo}" atualizado com sucesso!'
            )
            return redirect('listagem_empresas')
        else:
            messages.error(request, "Erro ao atualizar o projeto. Verifique os campos.")
    else:
        form = ProjetosForm(instance=projeto)

    return render(request, 'editar_projeto.html', {
        'form': form,
        'projeto': projeto
    })
    
    
    
    
    
    
    
    
    
    
    
    
    
@login_required
def criar_vinculo_teste(request):
    """View temporária para criar vínculo de teste - REMOVER EM PRODUÇÃO"""
    
    perfil = Profissional.objects.filter(user=request.user).first()
    
    if not perfil:
        messages.error(request, 'Você precisa ter um perfil profissional primeiro.')
        return redirect('home')
    
    # Pegar primeira empresa disponível
    empresa = Empresa.objects.first()
    
    if not empresa:
        messages.error(request, 'Não há empresas cadastradas no sistema.')
        return redirect('home')
    
    # Verificar se já existe um vínculo para evitar duplicatas
    vinculo_existe = VinculoProfissionalEmpresa.objects.filter(
        profissional=perfil,
        empresa=empresa
    ).exists()
    
    if vinculo_existe:
        messages.warning(request, 'Você já tem um vínculo com esta empresa.')
        return redirect('home_afiliado')
    
    # Criar vínculo de teste
    vinculo = VinculoProfissionalEmpresa.objects.create(
        profissional=perfil,
        empresa=empresa,
        cargo="Desenvolvedor de Jogos",
        tipo_vinculo="CLT",  # Ajuste se necessário baseado nas suas choices
        data_inicio=date(2024, 1, 1)
    )
    
    messages.success(request, f'✅ Vínculo de teste criado com sucesso! Você agora trabalha na {empresa.nome_fantasia}')
    return redirect('home_afiliado')