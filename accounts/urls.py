from django.urls import path
from . import views 
from .views import Teste_Diretoria
from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('login')

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/',
         views.login_view,
         name='login'),
    path(
        'home/',
        views.home,
        name='home',),
    
    path('cadastro/',
         views.cadastro,
         name='cadastro'),
#Usuario de teste    
    path("teste/", Teste_Diretoria, 
         name="usuario_teste"),

    path('diretoria/', 
         views.visao_diretoria, 
         name='visao_diretoria'),
    
    path('logout/', 
         logout_view, 
         name='logout'),
    
    path('empresas/',
         views.cadastro_empresas,
         name='empresas'),
    
    path('projetos/',
         views.cadastro_projetos,
         name='projetos'),
    
    path('empresas/listar',views.listagem_empresas,name='listagem_empresas'),
    path('empresas/editar/<int:pk>/',views.editar_empresas,name='editar_empresas'),
]