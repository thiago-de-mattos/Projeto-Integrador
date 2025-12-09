from django.urls import path
from . import views 

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
]