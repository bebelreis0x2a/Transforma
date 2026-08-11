from django import forms
from django.contrib.auth.models import User
from .models import *

# Em Django, posso criar os formulários com Python!

class CadastroPessoaForm(forms.ModelForm):
    email = forms.EmailField(
        label = "E-mail (Seu usuário de acesso)", # É o label do HTML
        widget=forms.EmailInput(attrs={'placeholder': 'seuemail@dominio.com'}) # Crio um dicionário que indica a criação de um placeholder com a mensagem: "seuemail@dominio.com"
    )
    senha = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={'placeholder': 'Digite sua senha'})
    )

    class Meta:
        model = Pessoas # Pega a classe Pessoa em Models.py
        fields = ['nome_social', 'genero', 'pronomes', 'data_nasc', 'foto_perfil'] # São os campos a serem utilizados no formulário
        widgets = { # Muda o visual para o calendário de seleção de data
            'data_nasc': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email') # Limpa o email de código malicioso!
        if User.objects.filter(username=email).exists(): # Verifica se já há um email igual cadastrado.
            raise forms.ValidationError("Este e-mail já está cadastrado no sistema.") # Se sim, o sistema nega.
        return email # A função retorna o email.

    def save(self, commit=True):
        email = self.cleaned_data.get('email') # Pega o email formatado, livre de qualquer código malicioso.
        senha = self.cleaned_data.get('senha') # Pega a senha formatada, livre de qualquer código malicioso.

        # 1. Cria e salva o User com o e-mail no username.
        user = User.objects.create_user( # O create_user criptografa a senha.
            username=email,
            email=email,
            password=senha
        )

        # 2. Instancia a Pessoa e vincula ao User.
        pessoa = super().save(commit=False) # O commit=False não permite salver ainda no banco de dados
        pessoa.usuario = user # Vincula o campo usuario do banco de dados com o user do bloco de cima

        if commit: # Se tudo estiver ok com o formulário:
            pessoa.save() # A pessoa é salva e retornada pela função (linha de baixo)
        return pessoa

class CadastroEmpresaForm(forms.ModelForm):
    email = forms.EmailField(
        label="E-mail da Empresa (Seu usuário de acesso)",
        widget=forms.EmailInput(attrs={'placeholder': 'contato@empresa.com'})
    )
    senha = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={'placeholder': 'Digite sua senha'})
    )

    class Meta:
        model = Empresas
        fields = ['nome', 'cnpj', 'telefone', 'endereco', 'descricao', 'site', 'foto_perfil']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado no sistema.")
        return email

    def save(self, commit=True):
        email = self.cleaned_data.get('email')
        senha = self.cleaned_data.get('senha')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=senha
        )

        empresa = super().save(commit=False)
        empresa.usuario = user

        if commit:
            empresa.save()
        return empresa