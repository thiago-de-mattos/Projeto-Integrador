from django.urls import path
from . import views 
from .views import Teste

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
    path("teste/", Teste, 
         name="usuario_teste"),
         
    path('diretoria/', 
         views.visao_diretoria, 
         name='visao_diretoria'),
]