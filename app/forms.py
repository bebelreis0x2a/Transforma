from django import forms
from django.contrib.auth.models import User
from .models import *
# Em Django, posso criar os formulários com Python!

import re # para trabalhar com expressões, como tratar o formato das senhas!


class CadastroPessoaForm(forms.ModelForm):
    email = forms.EmailField(
        label="E-mail (Seu usuário de acesso)",
        widget=forms.EmailInput(attrs={'placeholder': 'seuemail@dominio.com'})
    )
    senha = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={'placeholder': 'Digite sua senha'})
    )

    class Meta:
        model = Pessoas
        fields = ['nome_social', 'genero', 'pronomes', 'data_nasc', 'foto_perfil']
        widgets = {
            'data_nasc': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado no sistema.")
        return email

    # VALIDAÇÃO DE SEGURANÇA DA SENHA
    def clean_senha(self):
        senha = self.cleaned_data.get('senha')

        if len(senha) < 8:
            raise forms.ValidationError("A senha deve conter no mínimo 8 caracteres.")
        if not re.search(r'\d', senha):
            raise forms.ValidationError("A senha deve conter pelo menos um número.")
        if not re.search(r'[a-zA-Z]', senha):
            raise forms.ValidationError("A senha deve conter pelo menos uma letra.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', senha):
            raise forms.ValidationError("A senha deve conter pelo menos um símbolo especial (!@#$%...).")

        return senha

    def save(self, commit=True):
        email = self.cleaned_data.get('email')
        senha = self.cleaned_data.get('senha')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=senha
        )

        pessoa = super().save(commit=False)
        pessoa.usuario = user

        if commit:
            pessoa.save()
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

# Sugestões
class SugestaoForm(forms.ModelForm):
    class Meta:
        model = Sugestoes
        fields = ['tipo', 'nome', 'descricao', 'link']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do curso ou vaga'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descrição detalhada'}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }

# Avaliações
class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacoes
        fields = ['nome', 'descricao', 'pontos_positivos', 'pontos_negativos']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título ou assunto da avaliação'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição geral da sua experiência'}),
            'pontos_positivos': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'O que você mais gostou no site?'}),
            'pontos_negativos': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'O que precisa ser melhorado?'}),
        }