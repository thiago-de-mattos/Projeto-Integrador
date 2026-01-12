from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.conf import settings

class Accounts(models.Model):
    nome = models.CharField(max_length=200, verbose_name='Nome')
    cargo = models.CharField(max_length=200, verbose_name='Cargo')
    empresa = models.CharField(max_length=200, verbose_name='Empresa')

class CustomUser(AbstractUser):
    pass

    def __str__(self):
        return self.username
    

class ArranjosProdutivo(models.Model):
    nome = models.CharField('Nome', max_length=100)
    descricao = models.TextField('Descrição', blank=True)
    municipios_abrangidos = models.CharField('Municípios abrangidos', max_length=255)
    coordenador = models.CharField('Coordenador', max_length=100, blank=True)
    data_criacao = models.DateField('Data de criação')
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = 'Arranjo Produtivo'
        verbose_name_plural = 'Arranjos Produtivos'
        ordering = ['nome']


class Empresa(models.Model):
    TIPO_CHOICES = [
        ('DESENVOLVEDORA', 'Desenvolvedora'),
        ('PUBLICADORA', 'Publicadora'),
        ('AMBAS', 'Ambas'),
    ]
    
    PORTE_CHOICES = [
        ('MEI', 'MEI'),
        ('MICRO', 'Microempresa'),
        ('PEQUENA', 'Pequena'),
        ('MEDIA', 'Média'),
        ('GRANDE', 'Grande'),
    ]
    
    cnpj_validator = RegexValidator(
        regex=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$',
        message='CNPJ inválido. Use o formato: 00.000.000/0000-00'
    )
    
    nome_fantasia = models.CharField('Nome fantasia', max_length=150, blank= True, null = True)
    razao_social = models.CharField('Razão social', max_length=200, blank= True, null = True)
    cnpj = models.CharField('CNPJ', max_length=18, unique=True, validators=[cnpj_validator])
    
    email = models.EmailField('E-mail')
    telefone = models.CharField('Telefone', max_length=20, blank = True)
    site = models.URLField('Site', blank=True)
    
    endereco_completo = models.CharField('Endereço', max_length=255, blank= True, null = True)
    cidade = models.CharField('Cidade', max_length=100, blank=True)
    estado = models.CharField('Estado', max_length=2, default='RJ', blank= True, null = True)
    cep = models.CharField('CEP', max_length=10, blank=True)
    
    tipo_empresa = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES, blank=True)
    porte_empresa = models.CharField('Porte', max_length=10, choices=PORTE_CHOICES, blank = True)
    
    arranjo_produtivo = models.ForeignKey(
        ArranjosProdutivo, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Arranjo produtivo'
    )
    
    logo = models.ImageField('Logo', upload_to='empresas/logos/', blank=True, null=True)
    
    data_fundacao = models.DateField('Data de fundação', blank=True, null=True)
    associada_acjogos = models.BooleanField('Associada à ACJOGOS-RJ', default=False)
    data_cadastro = models.DateTimeField('Cadastrado em', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Atualizado em', auto_now=True)
    
    def __str__(self):
        return self.nome_fantasia
    
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nome_fantasia']


class StatusEmpresa(models.Model):
    STATUS_CHOICES = [
        ('ATIVA', 'Ativa'),
        ('INATIVA', 'Inativa'),
    ]
    
    empresa = models.ForeignKey(
        Empresa, 
        on_delete=models.CASCADE, 
        related_name='status_historico',
        verbose_name='Empresa'
    )
    status = models.CharField('Status', max_length=10, choices=STATUS_CHOICES)
    data_inicio = models.DateField('Data de início')
    data_fim = models.DateField('Data de fim', null=True, blank=True)
    motivo = models.TextField('Motivo', blank=True)
    
    def __str__(self):
        return f'{self.empresa.nome_fantasia} - {self.status}'
    
    class Meta:
        verbose_name = 'Status da Empresa'
        verbose_name_plural = 'Histórico de Status'
        ordering = ['-data_inicio']


class DadosAnuaisEmpresa(models.Model):
    MERCADO_CHOICES = [
        ('NACIONAL', 'Nacional'),
        ('INTERNACIONAL', 'Internacional'),
        ('AMBOS', 'Ambos'),
    ]
    
    empresa = models.ForeignKey(
        Empresa, 
        on_delete=models.CASCADE, 
        related_name='dados_anuais',
        verbose_name='Empresa'
    )
    ano_referencia = models.IntegerField(
        'Ano de referência',
        validators=[MinValueValidator(2000), MaxValueValidator(2100)]
    )
    
    faturamento_anual = models.DecimalField(
        'Faturamento anual (R$)',
        max_digits=15, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    investimento_recebido = models.DecimalField(
        'Investimento recebido (R$)',
        max_digits=15, 
        decimal_places=2, 
        default=0, 
        validators=[MinValueValidator(0)]
    )
    
    numero_funcionarios = models.IntegerField(
        'Número de funcionários',
        validators=[MinValueValidator(0)]
    )
    jogos_lancados = models.IntegerField(
        'Jogos lançados',
        default=0, 
        validators=[MinValueValidator(0)]
    )
    jogos_em_desenvolvimento = models.IntegerField(
        'Jogos em desenvolvimento',
        default=0, 
        validators=[MinValueValidator(0)]
    )
    
    plataformas_principais = models.CharField('Plataformas principais', max_length=200)
    mercado_principal = models.CharField('Mercado principal', max_length=20, choices=MERCADO_CHOICES)
    data_preenchimento = models.DateTimeField('Preenchido em', auto_now_add=True)
    
    def __str__(self):
        return f'{self.empresa.nome_fantasia} - {self.ano_referencia}'
    
    class Meta:
        verbose_name = 'Dados Anuais'
        verbose_name_plural = 'Dados Anuais das Empresas'
        unique_together = ['empresa', 'ano_referencia']
        ordering = ['-ano_referencia']


class Profissional(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('NB', 'Não-binário'),
        ('O', 'Outro'),
        ('N', 'Prefiro não informar'),
    ]
    
    cpf_validator = RegexValidator(
        regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
        message='CPF inválido. Use o formato: 000.000.000-00'
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Usuário')
    nome_completo = models.CharField('Nome completo', max_length=150)
    cpf = models.CharField('CPF', max_length=14, unique=True, validators=[cpf_validator])
    email = models.EmailField('E-mail', unique=True)
    telefone = models.CharField('Telefone', max_length=20)
    data_nascimento = models.DateField('Data de nascimento', null=True, blank=True)
    genero = models.CharField('Gênero', max_length=2, choices=GENERO_CHOICES, blank=True)
    cidade_residencia = models.CharField('Cidade', max_length=100)
    
    portfolio_url = models.URLField('Portfólio', blank=True)
    linkedin = models.URLField('LinkedIn', blank=True)
    github = models.URLField('GitHub', blank=True)
    behance = models.URLField('Behance', blank=True)
    
    tempo_experiencia = models.IntegerField(
        'Tempo de experiência (anos)',
        validators=[MinValueValidator(0)]
    )
    biografia = models.TextField('Biografia', blank=True)
    foto_perfil = models.ImageField('Foto', upload_to='profissionais/fotos/', blank=True, null=True)
    data_cadastro = models.DateTimeField('Cadastrado em', auto_now_add=True)
    
    def __str__(self):
        return self.nome_completo
    
    class Meta:
        verbose_name = 'Profissional'
        verbose_name_plural = 'Profissionais'
        ordering = ['nome_completo']


class Especialidade(models.Model):
    CATEGORIA_CHOICES = [
        ('PROGRAMACAO', 'Programação'),
        ('ARTE', 'Arte'),
        ('DESIGN', 'Design'),
        ('AUDIO', 'Áudio'),
        ('GESTAO', 'Gestão'),
        ('NARRATIVA', 'Narrativa'),
        ('QA', 'Quality Assurance'),
    ]
    
    nome = models.CharField('Nome', max_length=100, unique=True)
    categoria = models.CharField('Categoria', max_length=20, choices=CATEGORIA_CHOICES)
    descricao = models.TextField('Descrição', blank=True)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = 'Especialidade'
        verbose_name_plural = 'Especialidades'
        ordering = ['categoria', 'nome']


class ProfissionalEspecialidade(models.Model):
    NIVEL_CHOICES = [
        ('JUNIOR', 'Júnior'),
        ('PLENO', 'Pleno'),
        ('SENIOR', 'Sênior'),
        ('ESPECIALISTA', 'Especialista'),
    ]
    
    profissional = models.ForeignKey(
        Profissional, 
        on_delete=models.CASCADE, 
        related_name='especialidades',
        verbose_name='Profissional'
    )
    especialidade = models.ForeignKey(
        Especialidade, 
        on_delete=models.CASCADE,
        verbose_name='Especialidade'
    )
    nivel_experiencia = models.CharField('Nível', max_length=15, choices=NIVEL_CHOICES)
    
    def __str__(self):
        return f'{self.profissional.nome_completo} - {self.especialidade.nome}'
    
    class Meta:
        verbose_name = 'Especialidade do Profissional'
        verbose_name_plural = 'Especialidades dos Profissionais'
        unique_together = ['profissional', 'especialidade']


class VinculoProfissionalEmpresa(models.Model):
    TIPO_VINCULO_CHOICES = [
        ('CLT', 'CLT'),
        ('PJ', 'PJ'),
        ('FREELANCER', 'Freelancer'),
        ('ESTAGIO', 'Estágio'),
        ('VOLUNTARIO', 'Voluntário'),
    ]
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('APROVADO', 'Aprovado'),
        ('RECUSADO', 'Recusado'),
    ]
    
    profissional = models.ForeignKey(
        Profissional, 
        on_delete=models.CASCADE, 
        related_name='vinculos',
        verbose_name='Profissional'
    )
    empresa = models.ForeignKey(
        Empresa, 
        on_delete=models.CASCADE, 
        related_name='profissionais',
        verbose_name='Empresa'
    )
    cargo = models.CharField('Cargo', max_length=100)
    tipo_vinculo = models.CharField('Tipo de vínculo', max_length=15, choices=TIPO_VINCULO_CHOICES)
    data_inicio = models.DateField('Data de início')
    data_fim = models.DateField('Data de término', null=True, blank=True)
    status_aprovacao = models.CharField('Status', max_length=10, choices=STATUS_CHOICES, default='PENDENTE')
    data_solicitacao = models.DateTimeField('Solicitado em', auto_now_add=True)
    data_aprovacao = models.DateTimeField('Aprovado em', null=True, blank=True)
    
    def __str__(self):
        return f'{self.profissional.nome_completo} - {self.empresa.nome_fantasia}'
    
    class Meta:
        verbose_name = 'Vínculo Profissional-Empresa'
        verbose_name_plural = 'Vínculos Profissional-Empresa'
        ordering = ['-data_inicio']


class Projeto(models.Model):
    STATUS_CHOICES = [
        ('PLANEJAMENTO', 'Em Planejamento'),
        ('DESENVOLVIMENTO', 'Em Desenvolvimento'),
        ('LANCADO', 'Lançado'),
        ('CANCELADO', 'Cancelado'),
        ('DESCONTINUADO', 'Descontinuado'),
    ]
    
    PUBLICO_CHOICES = [
        ('INFANTIL', 'Infantil'),
        ('ADOLESCENTE', 'Adolescente'),
        ('ADULTO', 'Adulto'),
        ('GERAL', 'Geral'),
    ]
    
    titulo = models.CharField('Título', max_length=200)
    descricao = models.TextField('Descrição')
    genero_principal = models.CharField('Gênero principal', max_length=100)
    generos_secundarios = models.CharField('Gêneros secundários', max_length=200, blank=True)
    plataformas = models.CharField('Plataformas', max_length=200)
    engine_utilizada = models.CharField('Engine', max_length=100, blank=True)
    
    data_inicio_desenvolvimento = models.DateField('Início do desenvolvimento')
    data_lancamento = models.DateField('Data de lançamento', null=True, blank=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES)
    publico_alvo = models.CharField('Público-alvo', max_length=15, choices=PUBLICO_CHOICES)
    tipo_monetizacao = models.CharField('Monetização', max_length=100, blank=True)
    
    url_site = models.URLField('Site', blank=True)
    url_steam = models.URLField('Steam', blank=True)
    url_playstore = models.URLField('Play Store', blank=True)
    imagem_capa = models.ImageField('Capa', upload_to='projetos/capas/', blank=True, null=True)
    trailer_url = models.URLField('Trailer', blank=True)
    premiacoes = models.TextField('Premiações', blank=True)
    data_cadastro = models.DateTimeField('Cadastrado em', auto_now_add=True)
    
    def __str__(self):
        return self.titulo
    
    class Meta:
        verbose_name = 'Projeto'
        verbose_name_plural = 'Projetos'
        ordering = ['-data_inicio_desenvolvimento']


class EmpresaProjeto(models.Model):
    PAPEL_CHOICES = [
        ('DESENVOLVEDORA_PRINCIPAL', 'Desenvolvedora Principal'),
        ('CO_DESENVOLVEDORA', 'Co-desenvolvedora'),
        ('PUBLICADORA', 'Publicadora'),
        ('DISTRIBUIDORA', 'Distribuidora'),
        ('INVESTIDORA', 'Investidora'),
    ]
    
    empresa = models.ForeignKey(
        Empresa, 
        on_delete=models.CASCADE, 
        related_name='projetos',
        verbose_name='Empresa'
    )
    projeto = models.ForeignKey(
        Projeto, 
        on_delete=models.CASCADE, 
        related_name='empresas',
        verbose_name='Projeto'
    )
    papel = models.CharField('Papel', max_length=30, choices=PAPEL_CHOICES)
    porcentagem_participacao = models.DecimalField(
        'Participação (%)',
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    data_inicio_participacao = models.DateField('Início da participação')
    data_fim_participacao = models.DateField('Fim da participação', null=True, blank=True)
    
    def __str__(self):
        return f'{self.empresa.nome_fantasia} - {self.projeto.titulo}'
    
    class Meta:
        verbose_name = 'Empresa no Projeto'
        verbose_name_plural = 'Empresas nos Projetos'
        unique_together = ['empresa', 'projeto', 'papel']


class ProfissionalProjeto(models.Model):
    profissional = models.ForeignKey(
        Profissional, 
        on_delete=models.CASCADE, 
        related_name='projetos',
        verbose_name='Profissional'
    )
    projeto = models.ForeignKey(
        Projeto, 
        on_delete=models.CASCADE, 
        related_name='equipe',
        verbose_name='Projeto'
    )
    funcao = models.CharField('Função', max_length=100)
    especialidade = models.ForeignKey(
        Especialidade, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='Especialidade'
    )
    data_inicio = models.DateField('Data de início')
    data_fim = models.DateField('Data de término', null=True, blank=True)
    credito_publico = models.BooleanField('Exibir nos créditos públicos', default=True)
    
    def __str__(self):
        return f'{self.profissional.nome_completo} - {self.projeto.titulo}'
    
    class Meta:
        verbose_name = 'Profissional no Projeto'
        verbose_name_plural = 'Profissionais nos Projetos'
        unique_together = ['profissional', 'projeto', 'funcao']


class Profile(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('GESTOR', 'Gestor ACJOGOS'),
        ('EMPRESA', 'Empresa'),
        ('PROFISSIONAL', 'Profissional'),
        ('PODER_PUBLICO', 'Poder Público'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Usuário')
    tipo_usuario = models.CharField('Tipo de usuário', max_length=15, choices=TIPO_USUARIO_CHOICES)
    empresa = models.ForeignKey(
        Empresa, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Empresa'
    )
    profissional = models.ForeignKey(
        Profissional, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Profissional'
    )
    telefone_contato = models.CharField('Telefone', max_length=20, blank=True)
    foto_perfil = models.ImageField('Foto', upload_to='profiles/', blank=True, null=True)
    aceite_termos = models.BooleanField('Aceitou os termos', default=False)
    data_aceite_termos = models.DateTimeField('Data de aceite', null=True, blank=True)
    
    def __str__(self):
        return f'{self.user.username} ({self.get_tipo_usuario_display()})'
    
    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'
