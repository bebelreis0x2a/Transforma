from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import *
from .models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

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

# curriculo.html

@login_required
def curriculo_view(request):
    if not hasattr(request.user, 'perfil'): # se o atributo do usuário não for perfil, que são as Pessoas (classe Pessoas na model, relative_name):
        messages.error(request, "Acesso restrito apenas para candidatos.") # retorne essa mensagem de erro
        return redirect('home') # volta para a home

    curriculo, _ = Curriculos.objects.get_or_create(pessoa=request.user.perfil) # Essa função procura se o usuário tem currículo, retornando ou criando um caso não tenha
    # Essa função retorna uma tupla, contendo o objeto criado e um valor booleano (true or false). O _ pega esse valor booleano e desarta, pois não utilizaremos.


    if request.method == 'POST':
        acao = request.POST.get('acao') # tem um input escondido em 'curriculo.html' que retorna a ação do usuário, ou seja, qual botão ele clicou

        # 1. Ação de Salvar Diploma
        if acao == 'salvar_diploma':
            titulo = request.POST.get('titulo') # pega o título do diploma
            arquivo = request.FILES.get('arquivo') # pega o arquivo do diploma
            if titulo and arquivo:
                Diplomas.objects.create(curriculo=curriculo, titulo=titulo, arquivo=arquivo) # salva no banco de dados
                messages.success(request, "Diploma adicionado com sucesso!") # mensagem para o Django Admin
            return redirect('curriculo') # atualiza a página

        # 2. Ação de Deletar Diploma
        elif acao == 'deletar_diploma':
            diploma_id = request.POST.get('diploma_id')
            # Garante que o diploma pertence ao currículo do usuário logado antes de deletar
            diploma = get_object_or_404(Diplomas, id=diploma_id, curriculo=curriculo)
            diploma.delete()
            messages.success(request, "Diploma removido com sucesso!")
            return redirect('curriculo')

        # 3. Ação de Atualizar Dados Gerais do Currículo
        elif acao == 'salvar_curriculo':
            curriculo.resumo = request.POST.get('resumo')
            curriculo.formacao = request.POST.get('formacao')
            curriculo.competencias = request.POST.get('competencias')
            curriculo.habilidades = request.POST.get('habilidades')
            curriculo.save()
            messages.success(request, "Currículo atualizado com sucesso!")
            return redirect('curriculo')

    diplomas = curriculo.diplomas.all()

    context = {
        'curriculo': curriculo,
        'diplomas': diplomas,
        'formacao_choices': Curriculos.FORMACAO_CHOICES, # Permite selecionar, em um input de seleções (select), as opções pré-inseridas no banco de dados!
    }
    return render(request, 'curriculo.html', context)

# *** VAGAS ***

# VISÃO DA PESSOA CANDIDATA
@login_required
def vagas_pessoa_view(request):
    if not hasattr(request.user, 'perfil'):
        return redirect('home')

    pessoa = request.user.perfil

    # Minhas candidaturas efetuadas
    minhas_candidaturas = Candidaturas.objects.filter(pessoa=pessoa)
    vagas_candidatadas_ids = minhas_candidaturas.values_list('vaga_id', flat=True)

    # Base de vagas disponíveis (Apenas 'Deferida' e que a pessoa ainda não se candidatou)
    vagas_disponiveis = Vagas.objects.filter(status='Deferida').exclude(id__in=vagas_candidatadas_ids).prefetch_related('faqs')

    # --- FILTROS DE BUSCA ---
    busca = request.GET.get('busca', '')
    salario_min = request.GET.get('salario_min', '')

    if busca:
        # Filtra se o termo está no nome da vaga, na descrição ou no nome da empresa
        vagas_disponiveis = vagas_disponiveis.filter(
            Q(nome__icontains=busca) | 
            Q(descricao__icontains=busca) | 
            Q(empresa__nome__icontains=busca)
        )

    if salario_min:
        try:
            vagas_disponiveis = vagas_disponiveis.filter(salario__gte=float(salario_min))
        except ValueError:
            pass  # Ignora se o valor digitado não for um número válido

    context = {
        'vagas_disponiveis': vagas_disponiveis,
        'minhas_candidaturas': minhas_candidaturas,
        'busca': busca,
        'salario_min': salario_min,
    }
    return render(request, 'vagas_pessoa.html', context)


@login_required
def candidatar_vaga_view(request, vaga_id):
    if not hasattr(request.user, 'perfil'):
        return redirect('home')

    vaga = get_object_or_404(Vagas, id=vaga_id, status='Deferida')
    pessoa = request.user.perfil

    Candidaturas.objects.get_or_create(
        vaga=vaga, 
        pessoa=pessoa, 
        defaults={'status_vaga': 'Pendente'}
    )
    messages.success(request, f"Inscrição realizada com sucesso na vaga '{vaga.nome}'!")

    return redirect('vagas_pessoa')


# VISÃO DA EMPRESA 

@login_required
def vagas_empresa_view(request):
    if not hasattr(request.user, 'empresa'):
        return redirect('home')

    empresa = request.user.empresa

    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        salario = request.POST.get('salario') or 0.00

        # Cria a vaga
        vaga = Vagas.objects.create(
            empresa=empresa,
            nome=nome,
            descricao=descricao,
            salario=salario,
            status='Pendente'
        )

        # Captura as perguntas e respostas dinâmicas do FAQ
        perguntas = request.POST.getlist('faq_pergunta[]') # Isso funciona porque, em candidaturas_empresa.html, no JS, criamos uma lista com os FAQs
        respostas = request.POST.getlist('faq_resposta[]')

        for pergunta, resposta in zip(perguntas, respostas):
            if pergunta.strip() and resposta.strip():
                FAQ.objects.create(
                    vaga=vaga,
                    pergunta=pergunta.strip(),
                    resposta=resposta.strip()
                )

        messages.success(request, "Vaga e FAQs cadastrados com sucesso! Aguardando aprovação do administrador.")
        return redirect('vagas_empresa')

    minhas_vagas = Vagas.objects.filter(empresa=empresa).order_by('-id')
    return render(request, 'vagas_empresa.html', {'minhas_vagas': minhas_vagas})


@login_required
def candidaturas_empresa_view(request):
    if not hasattr(request.user, 'empresa'):
        return redirect('home')

    empresa = request.user.empresa
    candidaturas = Candidaturas.objects.filter(vaga__empresa=empresa).order_by('-id')

    return render(request, 'candidaturas_empresa.html', {'candidaturas': candidaturas})


@login_required
def alterar_status_candidatura_view(request, candidatura_id, novo_status):
    if not hasattr(request.user, 'empresa'):
        return redirect('home')

    candidatura = get_object_or_404(Candidaturas, id=candidatura_id, vaga__empresa=request.user.empresa)

    if novo_status.capitalize() in ['Deferida', 'Indeferida']:
        candidatura.status_vaga = novo_status.capitalize()
        candidatura.save()
        messages.info(request, f"Status da candidatura alterado para '{candidatura.status_vaga}'.")

    return redirect('candidaturas_empresa')

# *** CURSOS (VISÃO DA PESSOA CANDIDATA) ***

@login_required
def cursos_pessoa_view(request):
    if not hasattr(request.user, 'perfil'):
        messages.error(request, "Acesso restrito apenas para candidatos.")
        return redirect('home')

    pessoa = request.user.perfil

    # Minhas inscrições em cursos
    minhas_inscricoes = InscricoesCursos.objects.filter(pessoa=pessoa)
    cursos_inscritos_ids = minhas_inscricoes.values_list('curso_id', flat=True)

    # Cursos disponíveis (exclui os que a pessoa já se inscreveu)
    cursos_disponiveis = Cursos.objects.exclude(id__in=cursos_inscritos_ids).prefetch_related('faqs')

    # Filtro de Busca
    busca = request.GET.get('busca', '')
    if busca:
        cursos_disponiveis = cursos_disponiveis.filter(
            Q(nome__icontains=busca) | Q(descricao__icontains=busca)
        )

    context = {
        'minhas_inscricoes': minhas_inscricoes,
        'cursos_disponiveis': cursos_disponiveis,
        'busca': busca,
    }
    return render(request, 'cursos_pessoa.html', context)


@login_required
def inscrever_curso_view(request, curso_id):
    if not hasattr(request.user, 'perfil'):
        return redirect('home')

    curso = get_object_or_404(Cursos, id=curso_id)
    pessoa = request.user.perfil

    InscricoesCursos.objects.get_or_create(
        curso=curso,
        pessoa=pessoa,
        defaults={'status_curso': 'Cursando'}
    )
    messages.success(request, f"Inscrição realizada com sucesso no curso '{curso.nome}'!")

    return redirect('cursos_pessoa')

#===========#
# SUGESTÕES #
#===========#

@login_required
def sugestoes_pessoa_view(request):
    # Restringe o acesso apenas para usuários do tipo Pessoa
    if not hasattr(request.user, 'perfil'):
        messages.error(request, "Acesso restrito apenas para candidatos/pessoas.")
        return redirect('home')

    pessoa = request.user.perfil

    if request.method == 'POST':
        form = SugestaoForm(request.POST)
        if form.is_valid():
            sugestao = form.save(commit=False)
            sugestao.pessoa = pessoa  # Vincula a sugestão ao perfil logado
            sugestao.save()
            messages.success(request, "Sua sugestão foi enviada com sucesso e será analisada pelo Admin!")
            return redirect('sugestoes_pessoa')
    else:
        form = SugestaoForm()

    # Busca apenas as sugestões criadas pela própria pessoa
    minhas_sugestoes = Sugestoes.objects.filter(pessoa=pessoa).order_by('-data_envio')

    context = {
        'form': form,
        'minhas_sugestoes': minhas_sugestoes,
    }
    return render(request, 'sugestoes_pessoa.html', context)

#============#
# Avaliações #
#============#

@login_required
def avaliacoes_view(request):
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.usuario = request.user  # Associa a avaliação ao User logado
            avaliacao.save()
            messages.success(request, "Sua avaliação foi enviada com sucesso! Agradecemos o feedback.")
            return redirect('avaliacoes')
    else:
        form = AvaliacaoForm()

    # Busca apenas as avaliações feitas pelo próprio usuário conectado
    minhas_avaliacoes = Avaliacoes.objects.filter(usuario=request.user).order_by('-data_envio')

    context = {
        'form': form,
        'minhas_avaliacoes': minhas_avaliacoes,
    }
    return render(request, 'avaliacoes.html', context)
    
#--------------#
# INFORMAÇÕES! #
#--------------#

def informacoes_view(request):
    # Filtra apenas as postagens marcadas como "Publicado" pelo Admin
    postagens = Postagens.objects.filter(status='Publicado').order_by('-data_post')
    
    # Opcional: filtro de busca na tela de informações
    busca = request.GET.get('busca', '')
    if busca:
        postagens = postagens.filter(
            Q(titulo__icontains=busca) | Q(conteudo__icontains=busca)
        )

    context = {
        'postagens': postagens,
        'busca': busca,
    }
    return render(request, 'informacoes.html', context)