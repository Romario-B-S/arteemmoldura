from django.db import models
from django.contrib.auth.models import User

class Cliente(models.Model):
    nome = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    telefone = models.CharField(max_length=200, null=True, blank=True)
    id_sessao = models.CharField(max_length=200, null=True, blank=True)
    usuario = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return str(self.email)

class Categoria(models.Model):
    nome = models.CharField(max_length=200, null=True, blank=True)
    slug = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.nome)

class Tipo(models.Model):
    nome = models.CharField(max_length=200, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, null=True, blank=True, on_delete=models.SET_NULL)
    slug = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.nome)

class Tamanho(models.Model):
    nome = models.CharField(max_length=7, null=True, blank=True)
    adicional = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"ID: {self.id} - Nome: {self.nome} - Adicional: R$ {self.adicional}"

class Produto(models.Model):
    imagem = models.ImageField(null=True, blank=True)  # "camisa.png"
    nome = models.CharField(max_length=200, null=True, blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    ativo = models.BooleanField(default=True)
    categoria = models.ForeignKey(Categoria, null=True, blank=True, on_delete=models.SET_NULL)
    tipo = models.ForeignKey(Tipo, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Nome: {self.nome}, Categoria: {self.categoria}, Tipo: {self.tipo}, Preço: {self.preco}"

class Endereco(models.Model):
    rua = models.CharField(max_length=400, null=True, blank=True)
    numero = models.IntegerField(default=0)
    complemento = models.CharField(max_length=200, null=True, blank=True)
    cep = models.CharField(max_length=9, null=True, blank=True)
    cidade = models.CharField(max_length=200, null=True, blank=True)
    estado = models.CharField(max_length=200, null=True, blank=True)
    telefone = models.CharField(max_length=11, null=True, blank=True)
    nome_cliente = models.CharField(max_length=100, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self) -> str:
        return f"{self.cliente} - {self.rua} - {self.cidade}-{self.estado} - {self.cep}"

class Status_pedido(models.Model):
    nome = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.nome}"

class Transportadora(models.Model):
    nome = models.CharField(max_length=200, null=True, blank=True)
    cnpj = models.CharField(max_length=14, null=False, blank=False, default='00000000000000')
    endereco = models.CharField(max_length=400, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.nome}"

class Tabela_frete(models.Model):
    transportadora = models.ForeignKey(Transportadora, null=True, blank=True, on_delete=models.SET_NULL)

class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.SET_NULL)
    produto = models.ForeignKey(Produto, null=True, blank=True, on_delete=models.SET_NULL)
    quantidade = models.IntegerField(default=0)
    tamanho = models.ForeignKey(Tamanho, null=True, blank=True, on_delete=models.SET_NULL)
    finalizado = models.BooleanField(default=False)
    adicheckout = models.BooleanField(default=False)
    codigo_transacao = models.CharField(max_length=200, null=True, blank=True)
    endereco = models.ForeignKey(Endereco, null=True, blank=True, on_delete=models.SET_NULL)
    data_finalizacao = models.DateTimeField(null=True, blank=True)
    id_pagamento = models.CharField(max_length=400)
    pagamento_aprovado = models.BooleanField(default=False)
    tipo_frete = models.CharField(max_length=3, null=True, blank=True)
    valor_frete = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0)
    transportadora = models.ForeignKey(Transportadora, null=True, blank=True, on_delete=models.SET_NULL)
    codigo_rastreio = models.CharField(max_length=200, null=True, blank=True)
    status = models.ForeignKey(Status_pedido, null=True, blank=True, on_delete=models.SET_NULL)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0)

    def __str__(self) -> str:
        cliente_nome = self.cliente.nome if self.cliente else 'N/A'
        cliente_email = self.cliente.email if self.cliente else 'N/A'
        produto_nome = self.produto.nome if self.produto else 'N/A'
        return (f"ID: {self.id} - Cliente: {cliente_nome} - Email: {cliente_email} pedido: {produto_nome} - "
                f"Finalizado: {self.finalizado} - Adicheckout: {self.adicheckout}")

class Banner(models.Model):
    imagem = models.ImageField(null=True, blank=True)
    link_destino = models.CharField(max_length=400, null=True, blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.link_destino} - Ativo: {self.ativo}"

class Pagamento(models.Model):
    id_pagamento = models.CharField(max_length=400)
    pedido = models.ForeignKey(Pedido, null=True, blank=True, on_delete=models.SET_NULL)
    aprovado = models.BooleanField(default=False)
