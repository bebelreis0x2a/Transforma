from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import *

# CADASTROS

def cadastro_pessoa_view(request):
    if request.method == 'POST': # Usa o método POST, mais seguro
        form = CadastroPessoaForm(request.POST, request.FILES) # Obtém os dados através do POST e os arquivos através de FILES
        if form.is_valid(): # Se o formulário for válido:
            pessoa = form.save() # Os dados do formulário são salvos
            login(request, pessoa.usuario)  # Realiza o login automático após o cadastro
            return redirect('home')  # Redireciona para a página inicial
    else:
        form = CadastroPessoaForm() # O Django entra aqui quando o usuário acessa a página pela primeira vez (requisição GET). Ele apenas cria um formulário em branco (form = CadastroPessoaForm()) para ser exibido na tela.
    
    return render(request, 'cadastro_pessoa.html', {'form': form}) # Renderiza a página de cadastro

def cadastro_empresa_view(request):
    if request.method == 'POST':
        form = CadastroEmpresaForm(request.POST, request.FILES)
        if form.is_valid():
            empresa = form.save()
            login(request, empresa.usuario)  # Realiza o login automático após o cadastro
            return redirect('home')
    else:
        form = CadastroEmpresaForm()

    return render(request, 'cadastro_empresa.html', {'form': form})

# LOGIN

def login_view(request):
    if request.method == 'POST': # Verifica se os dados foram digitados e enviados
        form = AuthenticationForm(request, data=request.POST) # Instancia o formuláio; request: Gerencia a sessão com segurança
        if form.is_valid(): # Verifica se os dados existem no banco de dados e se a senha bate com a senha criptografada
            user = form.get_user() # Obtém, então, o usuário que existe no banco de dados
            login(request, user) # Inicia a sessão
            return redirect('home') # Redireciona o user para a homepage
    else:
        form = AuthenticationForm() # Cria o formulário. Entra aqui quando o usuário apenas acessou a página de login (método GET).

    return render(request, 'login.html', {'form': form}) # Renderiza a página de login

# LOGOUT

def logout_view(request):
    logout(request)
    return redirect('login') # Redireciona o usuário para a página de login

# home.html

from django.shortcuts import render, redirect

def home_view(request):
    return render(request, 'home.html')