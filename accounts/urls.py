from django.urls import path
from . import views 
from .views import Teste

urlpatterns = [
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
]