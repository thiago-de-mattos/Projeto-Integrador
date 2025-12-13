from django.shortcuts import render,  redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login as login_django
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm

def cadastro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('login')
        
        else:
            messages.error(request, 'Houve um erro no cadastro. Verifique os campos.')

    else:
        form = UserCreationForm()
    context = {'form': form}
    
    return render(request, 'cadastro.html', context)
        

def login(request):
    if request.method=='GET':
        return render(request, 'login.html')
    else:
        username=request.POST.get('username')
        senha=request.POST.get('senha')
        
        if not username or not senha:
            messages.error(request,'Preencha os campos')
            return render(request,'login.html')
        
        user=authenticate(username=username,password=senha)
        
        if user:
            login_django(request,user)
            return redirect('home')
        
        else:
            messages.error(request, 'Usuário ou senha inválidos')
            return render(request, 'login.html')
        
@login_required(login_url="/auth/login/")
def home(request):
    username=request.POST.get('username')
    return render(request, "home.html", {'username': request.user.username})