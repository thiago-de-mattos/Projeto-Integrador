from django.urls import path
from . import views 
from .views import Teste

urlpatterns = [
    path(
        'home/',
        views.home,
        name='home',),
    
    path('cadastro/',
         views.cadastro,
         name='cadastro'),
    path('',
         views.login,
         name='login'),
#Usuario de teste    
    path("teste/", Teste, 
         name="usuario_teste"),
    
    path("perfil/editar/", views.editar_perfil, name="editar_perfil"),
]
