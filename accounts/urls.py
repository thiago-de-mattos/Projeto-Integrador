from django.urls import path
from . import views 
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

def logout_view(request):
    logout(request)
    return redirect('login')

urlpatterns = [

# --- Rota Principal (Redirecionador) ---
     path('', views.home_teste, name='home_teste'),
     path('home/', views.home, name='home',),

# --- Autenticação ---
     path('logout/', logout_view, name='logout'), 
    # Pedro veja essas urls
    #  path('cadastro/', views.cadastro, name='cadastro'),
     path('cadastro/empresa/', views.cadastro_empresa, name='cadastro_empresa'),
     path('cadastro/profissional/', views.cadastro_profissional, name='cadastro_profissional'),

# --- Painéis Específicos (Roles) ---
     path('home/associado/', views.home_associado, name='home_associado'),
     path('home/afiliado/', views.home_afiliado, name='home_afiliado'),
     path('home/coletivo/', views.home_coletivo, name='home_coletivo'),
     path('home/diretoria/', views.home_diretoria, name='home_diretoria'),
     path('diretoria/gestao/', views.visao_diretoria, name='visao_diretoria'),

     #Usuario de teste 
     path('setup/diretoria/', views.Teste_Diretoria, name='setup_diretoria'),
     path('setup/associado/', views.Teste_Associado, name='setup_associado'),
     path('setup/afiliado/', views.Teste_Afiliado, name='setup_afiliado'),
     path('setup/coletivo/', views.Teste_Coletivo, name='setup_coletivo'),

# --- Edições ---
     path('perfil/editar/', views.editar_meu_perfil, name='editar_meu_perfil'),
     path('empresa/editar/', views.editar_minha_empresa, name='editar_minha_empresa'),
     path('empresas/editar/<int:pk>/',views.editar_empresas,name='editar_empresas'),
     path('estudio/editar_estudio/<int:pk>/', views.editar_estudios, name='editar_estudios'),
     path('responsavel/editar/<int:id>/', views.editar_responsavel_empresa, name='editar_responsavel_empresa'),
     path('projetos/editar/<int:projeto_id>/', views.editar_projeto, name='editar_projeto'),
     
# --- Funcionalidades Gerais ---
     path('empresas/', views.cadastro_empresa, name='empresas'),
     path('empresas/listagem/', views.listagem_empresas, name="listagem_empresas"),
     
     path('pagina/projeto',views.pagina_projeto , name= 'pagina_projeto'),

     path('projetos/', views.cadastro_projetos, name='projetos'),
     path('projetos/vitrine/', views.vitrine_projetos, name="vitrine_projetos"),

     path('vitrine/', views.vitrine, name='vitrine'),

     path('estatisticas/', views.estatistica, name='estatistica'),
     path('estatisticas/detalhadas/', views.estatisticas_detalhadas, name='estatistica_detalhada'),

     path('estudios/', views.cadastro_estudio, name='estudios'),
     
     path('responsavel/cadastrar/', views.cadastro_responsavel_empresa, name='cadastro_responsavel_empresa'),
     
#--- htmls TESTE ---
     path('empresas_teste/', views.empresas_list, name='empresas_teste'),
     # path('empresas_teste/<int:pk>/', views.empresa_detail, name='empresa_detail'),
     path('projetos_teste/', views.projetos_list, name='projetos_teste'),
     path('mapa_teste/', views.mapa, name='mapa'),
     path('estatisticas_teste/', views.estatisticas_teste, name='estatisticas_teste'),
     path("login_teste/", views.login_view_teste, name="login_teste"),
     path("cadastro_teste/", views.register_view_teste, name="cadastro_teste"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)