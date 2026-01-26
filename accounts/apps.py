from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        """
        Registra o signal para criar dados após migrate
        """
        from django.db.models.signals import post_migrate
        post_migrate.connect(criar_dados_iniciais, sender=self)


def criar_dados_iniciais(sender, **kwargs):
    """
    Cria dados iniciais após as migrations serem executadas
    """
    from django.contrib.auth import get_user_model
    from rolepermissions.roles import assign_role
    from accounts.models import Empresa, Profile, Projeto, Profissional
    
    User = get_user_model()
    
    # Verifica se já existem
    if User.objects.filter(username="diretoria_geral").exists():
        return

    
    # --- 1. SETUP DIRETORIA & COLETIVO ---
    u_dir = User.objects.create(
        username="diretoria_geral",
        email="diretoria@teste.com"
    )
    u_dir.set_password("123")
    u_dir.save()
    assign_role(u_dir, 'diretoria')


    u_col = User.objects.create(
        username="coletivo_geral",
        email="coletivo@teste.com"
    )
    u_col.set_password("123")
    u_col.save()
    assign_role(u_col, 'coletivo')


    # --- 2. GERADOR DE EMPRESAS (ASSOCIADOS) ---
    lista_empresas = [
        {"nome": "Pixel Rio Studio", "user": "assoc_pixel", "cidade": "Rio de Janeiro", "porte": "Pequeno Porte", "tipo": "Desenvolvedora", "projeto": "Cangaço Cyberpunk", "genero": "RPG"},
        {"nome": "Niterói Games", "user": "assoc_niteroi", "cidade": "Niterói", "porte": "Microempresa", "tipo": "Editora", "projeto": "Ponte Rio-Niterói Racer", "genero": "Corrida"},
        {"nome": "Serrana Arts", "user": "assoc_serra", "cidade": "Petrópolis", "porte": "MEI", "tipo": "Asset Store", "projeto": "Imperial City Sim", "genero": "Simulação"},
        {"nome": "Caxias Code", "user": "assoc_caxias", "cidade": "Duque de Caxias", "porte": "Médio Porte", "tipo": "Outsourcing", "projeto": "Baixada Defense", "genero": "Estratégia"},
        {"nome": "Maricá VR", "user": "assoc_marica", "cidade": "Maricá", "porte": "Pequeno Porte", "tipo": "Desenvolvedora", "projeto": "Maricá Verse", "genero": "Aventura"},
        {"nome": "Petrópolis Devs", "user": "assoc_petropolis", "cidade": "Petrópolis", "porte": "Pequeno Porte", "tipo": "Desenvolvedora", "projeto": "Serra Run", "genero": "Arcade"},
        {"nome": "Cabo Frio Studio", "user": "assoc_cabofrio", "cidade": "Cabo Frio", "porte": "Micro Empresa", "tipo": "Desenvolvedora", "projeto": "Ocean Explorer", "genero": "Simulação"},
    ]

    for idx, data in enumerate(lista_empresas):
        # Cria o usuário
        email = f"{data['user']}@teste.com"
        user = User.objects.create(
            username=data['user'],
            email=email
        )
        user.set_password("123")
        user.save()
        assign_role(user, 'associado')
        
        # Cria a empresa
        cnpj_falso = f"00.000.000/000{500+idx}-00"
        empresa = Empresa.objects.create(
            nome_fantasia=data['nome'],
            razao_social=f"{data['nome']} Ltda",
            cnpj=cnpj_falso,
            cidade=data['cidade'],
            municipio=data['cidade'],
            tipo_empresa=data['tipo'],
            porte_empresa=data['porte'],
            associada_acjogos=True,
        )

        # Vincula o Profile à Empresa
        perfil, _ = Profile.objects.get_or_create(user=user)
        perfil.empresa = empresa
        perfil.save()

        # Cria o Projeto vinculado à Empresa
        projeto = Projeto.objects.create(
            titulo=data['projeto'],
            nome=data['projeto'],
            empresa=empresa,  # ← AQUI ESTÁ O VÍNCULO IMPORTANTE
            descricao=f"Um jogo incrível desenvolvido em {data['cidade']}.",
            tipo_jogo=data['genero'],
            genero_principal=data['genero'],
            equipe_projeto='Equipe Principal',
            status='LANCADO' if idx % 2 == 0 else 'DESENVOLVIMENTO',
            publico_alvo='GERAL'
        )

    # --- 3. GERADOR DE PROFISSIONAIS (AFILIADOS) ---
    lista_pros = [
        {"nome": "Ana Artist", "user": "afiliado_ana", "cargo": "2D Artist", "cidade": "Rio de Janeiro"},
        {"nome": "Carlos Coder", "user": "afiliado_carlos", "cargo": "Programador Unity", "cidade": "São Gonçalo"},
        {"nome": "Bruno Sound", "user": "afiliado_bruno", "cargo": "Sound Designer", "cidade": "Rio de Janeiro"},
        {"nome": "Diana Design", "user": "afiliado_diana", "cargo": "Game Designer", "cidade": "Niterói"},
    ]

    for idx, data in enumerate(lista_pros):
        email = f"{data['user']}@teste.com"
        user = User.objects.create(
            username=data['user'],
            email=email
        )
        user.set_password("123")
        user.save()
        assign_role(user, 'afiliado')

        Profissional.objects.create(
            user=user,
            nome_completo=data['nome'],
            cpf=f"111.222.333-{10+idx}",
            email=email,
            telefone='(21) 90000-0000',
            cidade_residencia=data['cidade'],
            tempo_experiencia=3 + idx,
            biografia=f"Sou especialista em {data['cargo']}.",
        )
