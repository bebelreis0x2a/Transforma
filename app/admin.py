from django.contrib import admin
from .models import *

# --- INLINES ---

class DiplomasInline(admin.TabularInline):
    model = Diplomas # Qual a Model que me refiro/que será editada.
    extra = 1 # Quant. de linhas que irão aparecer no Inline

class FAQVagaInline(admin.TabularInline):
    model = FAQ
    extra = 1
    fk_name = 'vaga' # Especifica para qual chave estrangeira o Inline está se referindo (visto que FAQ é usada tanto por Vagas, quanto por Cursos).
    exclude = ['curso'] # Como esse FAQ é de vagas, ele não mostrará, no Inline de Vagas, o campo para Cursos.

class FAQCursoInline(admin.TabularInline):
    model = FAQ
    extra = 1
    fk_name = 'curso'
    exclude = ['vaga']

class CandidaturasInline(admin.TabularInline):
    model = Candidaturas
    extra = 0
    readonly_fields = ['vaga', 'data_inscricao', 'status_vaga']
    can_delete = False # O administrador não tem o poder de excluir candidaturas existentes!

class InscricoesCursosInline(admin.TabularInline):
    model = InscricoesCursos
    extra = 0
    readonly_fields = ['curso', 'data_inscricao', 'status_curso']
    can_delete = False


# --- MODEL ADMINS ---

@admin.register(Pessoas)
class PessoasAdmin(admin.ModelAdmin):
    list_display = ('nome_social', 'usuario', 'genero', 'data_nasc') # Colunas a serem exibidas na tabela de LISTAGEM
    search_fields = ('nome_social', 'usuario__username', 'usuario__email') # Quais campos o sistema buscará na barra de pesquisa dentro do Django Admin
    inlines = [CandidaturasInline, InscricoesCursosInline]

@admin.register(Curriculos)
class CurriculosAdmin(admin.ModelAdmin):
    list_display = ('pessoa', 'formacao')
    search_fields = ('pessoa__nome_social', 'pessoa__usuario__username')
    list_filter = ('formacao',) # Cria uma barra lateral de filtros rápidos com base em campos específicos.
    inlines = [DiplomasInline]

@admin.register(Empresas)
class EmpresasAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'telefone', 'verificada')
    list_filter = ('verificada',)
    search_fields = ('nome', 'cnpj')
    list_editable = ('verificada',) # Permite editar campos diretamente na tabela de listagem, sem precisar abrir o registro individual.

@admin.register(Vagas)
class VagasAdmin(admin.ModelAdmin):
    list_display = ('nome', 'empresa', 'salario', 'status', 'data_criacao')
    list_filter = ('status', 'data_criacao')
    search_fields = ('nome', 'empresa__nome')
    list_editable = ('status',)
    inlines = [FAQVagaInline]

@admin.register(Cursos)
class CursosAdmin(admin.ModelAdmin):
    list_display = ('nome', 'carga_horaria', 'data_cadastro')
    search_fields = ('nome',)
    inlines = [FAQCursoInline]

@admin.register(Candidaturas)
class CandidaturasAdmin(admin.ModelAdmin):
    list_display = ('pessoa', 'vaga', 'status_vaga', 'data_inscricao')
    list_filter = ('status_vaga', 'data_inscricao')
    search_fields = ('pessoa__nome_social', 'vaga__nome')
    list_editable = ('status_vaga',)

@admin.register(InscricoesCursos)
class InscricoesCursosAdmin(admin.ModelAdmin):
    list_display = ('pessoa', 'curso', 'status_curso', 'data_inscricao')
    list_filter = ('status_curso', 'data_inscricao')
    search_fields = ('pessoa__nome_social', 'curso__nome')
    list_editable = ('status_curso',)

@admin.register(Sugestoes)
class SugestoesAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'pessoa', 'data_envio')
    list_filter = ('tipo', 'data_envio')
    search_fields = ('nome', 'pessoa__nome_social')

@admin.register(Avaliacoes)
class AvaliacoesAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'nome', 'data_envio')
    search_fields = ('usuario__username', 'nome')

@admin.register(Postagens)
class PostagensAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'status', 'data_post')
    list_filter = ('status', 'data_post')
    search_fields = ('titulo',)
    list_editable = ('status',)

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('pergunta', 'vaga', 'curso')
    search_fields = ('pergunta', 'resposta')