from django.urls import path
from . import views 
from .views import Teste_Diretoria
from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('login')

urlpatterns = [

     path('', views.home, name='home',),
     path('login/', views.login_view, name='login'),
     path('logout/', logout_view, name='logout'),

     path('cadastro/', views.cadastro, name='cadastro'),
     path('perfil/editar/', views.editar_meu_perfil, name='editar_meu_perfil'),
     
     path('diretoria/', views.visao_diretoria, name='visao_diretoria'),
     #Usuario de teste DIRETORIA
     path("teste/", Teste_Diretoria, name="usuario_teste"),

     path('empresas/', views.cadastro_empresa, name='empresas'),
     path('empresas/listagem/', views.listagem_empresas, name="listagem_empresas"),
     path('empresas/editar/<int:pk>/',views.editar_empresas,name='editar_empresas'),
     path('empresa/editar/', views.editar_minha_empresa, name='editar_minha_empresa'),
     
     path('pagina/projeto',views.pagina_projeto , name= 'pagina_projeto'),

     path('projetos/', views.cadastro_projetos, name='projetos'),
     path('projetos/vitrine/', views.vitrine_projetos, name="vitrine_projetos"),

     path('vitrine/', views.vitrine, name='vitrine'),

     path('estatisticas/', views.estatistica, name='estatistica'),
     path('estatisticas/detalhadas/', views.estatisticas_detalhadas, name='estatistica_detalhada'),

     path('estudios/', views.cadastro_estudio, name='estudios'),
     path('estudio/editar_estudio/<int:pk>/', views.editar_estudios, name='editar_estudios'),

     path('responsavel/cadastrar/', views.cadastro_responsavel_empresa, name='cadastro_responsavel_empresa'),
     path('responsavel/editar/<int:id>/', views.editar_responsavel_empresa, name='editar_responsavel_empresa'),


     ]