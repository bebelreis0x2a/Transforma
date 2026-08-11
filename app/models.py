'''
Dica super legal!

Podemos criar um arquivo JSON para salvar os registros do Django Admin!

Para salvar:
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 4 > dados.json

Para carregar os dados salvos:
python manage.py loaddata dados.json
'''

from django.db import models
from django.contrib.auth.models import User

# SEÇÃO DOS ADMINS

class Postagens(models.Model):
    STATUS_CHOICES = [ # É o enum
        ('Rascunho', 'Rascunho'),
        ('Publicado', 'Publicado'),
    ]

    titulo = models.CharField(max_length=200, verbose_name="Título")
    conteudo = models.TextField(verbose_name="Conteúdo")
    data_post = models.DateTimeField(auto_now_add=True, verbose_name="Data de publicação")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, # Aqui, ele utiliza o enum
        default='Rascunho', 
        verbose_name="Status de Exibição"
    )

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Postagem"
        verbose_name_plural = "Postagens"

# ADICIONAR A CHAVE ESTRANGEIRA DE FAQ!

class Cursos(models.Model):
    nome = models.CharField(max_length=150, verbose_name="Nome do curso")
    descricao = models.TextField(verbose_name="Descrição do curso")
    carga_horaria = models.CharField(max_length=50, blank=True, null=True, verbose_name="Carga horária")
    link_inscricao = models.URLField(max_length=300, blank=True, null=True, verbose_name="Link de acesso/inscrição")
    data_cadastro = models.DateField(auto_now_add=True, verbose_name="Data de cadastro")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"

# PESSOAS

class Pessoas(models.Model):
    # Conecta este perfil diretamente a um usuário do Django.
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    
    nome_social = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nome social e/ou de registro da pessoa")
    genero = models.CharField(max_length=25, blank=True, null=True, verbose_name="Identidade de gênero")
    pronomes = models.CharField(max_length=15, blank=True, null=True, verbose_name="Pronomes")
    data_nasc = models.DateField(blank=True, null=True, verbose_name="Data de nascimento")
    foto_perfil = models.ImageField(upload_to='perfis/', blank=True, null=True, verbose_name="Foto de perfil")

    def __str__(self):
        return self.nome_social or self.usuario.username # Retorno apenas o nome da pessoa, é uma boa prática.

    class Meta:
        verbose_name = "Pessoa"
        verbose_name_plural = "Pessoas"

# SUGESTÕES

class Sugestoes(models.Model):
    TIPO_CHOICES = [
        ('Curso', 'Curso'),
        ('Vaga', 'Vaga'),
    ]

    # O related_name permite a pesquisa inversa (vide linha 75).
    pessoa = models.ForeignKey('Pessoas', on_delete=models.CASCADE, related_name="sugestoes", verbose_name="Pessoa") # Chave estrangeira de Pessoas.
    
    nome = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nome")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    link = models.URLField(max_length=200, blank=True, null=True, verbose_name="URL do site da vaga/curso proposto")
    data_envio = models.DateTimeField(auto_now_add=True, verbose_name="Data de Envio")

    tipo = models.CharField(
        max_length=20, 
        choices=TIPO_CHOICES, 
        verbose_name="Tipo de Sugestão"
    )

    def __str__(self):
        return f"[{self.tipo}] {self.nome or f'Sugestão #{self.pk}'}" # Caso, por algum motivo, for enviada uma sugstão sem nome, é mostrado o id da sugestão

    class Meta:
        verbose_name = "Sugestão"
        verbose_name_plural = "Sugestões"

# DIPLOMAS E CURRICULOS

class Curriculos(models.Model):
    FORMACAO_CHOICES = [
        ('fundamental_completo', 'Fundamental Completo'),
        ('fundamental_incompleto', 'Fundamental Incompleto'),
        ('medio_completo', 'Médio Completo'),
        ('medio_incompleto', 'Médio Incompleto'),
        ('superior_completo', 'Superior Completo'),
        ('superior_incompleto', 'Superior Incompleto'),
    ]

    # Cada pessoa tem no máximo 1 currículo
    pessoa = models.OneToOneField('Pessoas', on_delete=models.CASCADE, related_name='curriculo',verbose_name="Pessoa")
    resumo = models.TextField(blank=True, null=True, verbose_name="Resumo Profissional")
    competencias = models.TextField(blank=True, null=True, verbose_name="Competências")
    habilidades = models.TextField(blank=True, null=True, verbose_name="Habilidades")
    formacao = models.CharField(
        max_length=30, 
        choices=FORMACAO_CHOICES, 
        verbose_name="Tipo de Formação"
    )

    def __str__(self):
        return f"Currículo de {self.pessoa.nome_social or self.pessoa.usuario.username}"

    class Meta:
        verbose_name = "Currículo"
        verbose_name_plural = "Currículos"

class Diplomas(models.Model):
    curriculo = models.ForeignKey(Curriculos, on_delete=models.CASCADE, related_name='diplomas', verbose_name="Currículo")
    titulo = models.CharField(max_length=100, verbose_name="Título / Nome do Certificado")
    arquivo = models.FileField(upload_to='diplomas/', verbose_name="Arquivo (PDF/Imagem)")
    data_upload = models.DateField(auto_now_add=True, verbose_name="Data de envio")

    def __str__(self):
        return f"{self.titulo} - {self.curriculo.pessoa}"

    class Meta:
        verbose_name = "Diploma/Certificado"
        verbose_name_plural = "Diplomas/Certificados"

# SEÇÃO DE EMPRESAS

class Empresas(models.Model):
    # Conecta este perfil diretamente a um usuário do Django.
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='empresa')
    
    nome = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nome da empresa")
    cnpj = models.CharField(max_length=25, blank=True, unique=True, null=True, verbose_name="CNPJ") # O "unique = True" garante que não seja armazenada duas empresas com o mesmo CNPJ no banco de dados.
    telefone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Telefone para contato")
    endereco = models.CharField(max_length=100, blank=True, null=True, verbose_name="Endereço")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    site = models.URLField(max_length=200, blank=True, null=True, verbose_name="URL do site")
    verificada = models.BooleanField(default=False)
    foto_perfil = models.ImageField(upload_to='empresas/', blank=True, null=True, verbose_name="Imagem da empresa") # Criei um diretório diferente para as fotos das empresas

    def __str__(self):
        return self.nome or self.usuario.username # Retorno apenas o nome da pessoa, é uma boa prática.

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

# SEÇÃO DE VAGAS

class Vagas(models.Model):
    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Deferida', 'Deferida / Publicada'),
        ('Indeferida', 'Indeferida'),
    ]

    # Relaciona a vaga à Empresa criadora.
    empresa = models.ForeignKey('Empresas', on_delete=models.CASCADE, related_name='vagas', verbose_name="Empresa") # Related_name é utilizado para a consulta inversa de um registro, permitindo usar a função empresa.vagas.all()!
    nome = models.CharField(max_length=100, verbose_name="Nome da vaga")
    descricao = models.TextField(verbose_name="Descrição")
    salario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True, verbose_name="Salário")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Pendente', 
        verbose_name="Status de Aprovação (Admin)" # Pois é o admin que autoriza se a vaga será publicada ou não
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")

    def __str__(self):
        return f"{self.nome} - {self.empresa.nome or self.empresa.usuario.username}"

    class Meta:
        verbose_name = "Vaga"
        verbose_name_plural = "Vagas"


class FAQ(models.Model):
    # Usando 'Vagas' como string evita o erro de ordem das classes
    vaga = models.ForeignKey('Vagas', on_delete=models.CASCADE, related_name="faqs", blank=True, null=True, verbose_name="Vaga")
    curso = models.ForeignKey('Cursos', on_delete=models.CASCADE, related_name="faqs", blank=True, null=True, verbose_name="Curso")
    pergunta = models.TextField(verbose_name="Pergunta")
    resposta = models.TextField(verbose_name="Resposta")

    def __str__(self):
        origem = self.vaga.nome if self.vaga else (self.curso.nome if self.curso else "Geral")
        return f"FAQ ({origem}): {self.pergunta[:30]}..."

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

# CANDIDATURAS

class Candidaturas(models.Model): # Tabela de relação N:N entre Pessoas e Vagas.

    STATUS_CHOICES = [
        ('Pendente', 'Pendente / Em análise'),
        ('Deferida', 'Deferida'),
        ('Indeferida', 'Indeferida'),
    ]

    pessoa = models.ForeignKey('Pessoas', on_delete=models.CASCADE, related_name="candidaturas", verbose_name="Candidato(a)") # Chave estrangeira de Pessoas.
    vaga = models.ForeignKey(Vagas, on_delete=models.CASCADE, related_name="candidaturas", verbose_name="Vaga") # Chave estrangeira de Vagas.
    data_inscricao = models.DateField(auto_now_add=True, verbose_name="Data de Inscrição")
    status_vaga = models.CharField(
        max_length=30, 
        choices=STATUS_CHOICES,
        default='Pendente', 
        verbose_name="Status da Candidatura"
    )

    class Meta:
        verbose_name = "Candidatura"
        verbose_name_plural = "Candidaturas"
        # Garante que a mesma pessoa não se candidate duas vezes na mesma vaga
        unique_together = ('pessoa', 'vaga')

    def __str__(self):
        return f"{self.pessoa.nome_social or self.pessoa.usuario.username} -> {self.vaga.nome}"

# AVALIAÇÕES 

class Avaliacoes(models.Model):
    # Relaciona a avaliação diretamente à conta do User (Pessoa, Empresa ou Admin, independente se criado através do createsuperuser ou via relação OneToOneField).
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avaliacoes', verbose_name="Usuário")
    
    nome = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nome/Título do Feedback")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição geral")
    pontos_positivos = models.TextField(blank=True, null=True, verbose_name="Pontos Positivos")
    pontos_negativos = models.TextField(blank=True, null=True, verbose_name="Pontos Negativos")
    data_envio = models.DateTimeField(auto_now_add=True, verbose_name="Data de envio") # O "auto_now_add = True" configura a data da postagem com a data e hora exatas no momento que o objeto é criado/a postagem é enviada.

    def __str__(self):
        return f"Avaliação de {self.usuario.username} - {self.nome or 'Sem título'}" # A postagem pode não ter título.

    class Meta:
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"

# Inscrição em CURSOS

class InscricoesCursos(models.Model): # Tabela de relação N:N entre Pessoas e Vagas.

    STATUS_CHOICES = [
        ('Cursando', 'Cursando / Em andamento'),
        ('Concluido', 'Concluído'),
    ]

    pessoa = models.ForeignKey('Pessoas', on_delete=models.CASCADE, related_name="inscricoes_cursos", verbose_name="Estudante") # Related_name sempre em snake_name!
    curso = models.ForeignKey('Cursos', on_delete=models.CASCADE, related_name="inscricoes_cursos", verbose_name="Curso") 
    data_inscricao = models.DateField(auto_now_add=True, verbose_name="Data de Inscrição")
    status_curso = models.CharField(
        max_length=30, 
        choices=STATUS_CHOICES,
        default='Cursando', 
        verbose_name="Status do Curso"
    )

    class Meta:
        verbose_name = "Inscrição em Curso"
        verbose_name_plural = "Inscrições em Cursos"
        unique_together = ('pessoa', 'curso')

    def __str__(self):
        return f"{self.pessoa.nome_social or self.pessoa.usuario.username} -> {self.curso.nome}"