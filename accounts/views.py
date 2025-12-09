from django.shortcuts import render,  redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login as login_django
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.
def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    else:
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        if not username or not email or not senha:
            messages.error(request,"preencha todos os campos")
            return render(request,'cadastro.html')
        
        user = User.objects.filter(username=username).first()
        # Verifica se já existe um usuário com esse username
        if user:
            messages.error(request,'Já existe um usuário com esse cadastro')
            return render(request,'cadastro.html')
        
        user=User.objects.create_user(username=username,email=email,password=senha)
        messages.success(request,'Usuario cadastrado com sucesso')
        return redirect('login')
        
        
        
       
        
        

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