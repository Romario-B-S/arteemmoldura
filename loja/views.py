from django.shortcuts import render, redirect
from django.urls import reverse
from .models import *
import uuid
from .utils import filtrar_produtos, preco_minimo_maximo, ordenar_produtos, enviar_email_compra, exportar_csv
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from datetime import datetime
from .api_mercadopago import criar_pagamento


# Create your views here.
def homepage(request):
    banners = Banner.objects.filter(ativo=True)
    context = {"banners": banners}
    return render(request, 'homepage.html', context)

def loja(request, filtro=None):
    produtos = Produto.objects.filter(ativo=True)
    produtos = filtrar_produtos(produtos, filtro)
    if request.method == "POST":
        dados = request.POST.dict()
        produtos = produtos.filter(preco__gte=dados.get("preco_minimo"), preco__lte=dados.get("preco_maximo"))
        if "tipo" in dados:
            produtos = produtos.filter(tipo__slug=dados.get("tipo"))
        if "categoria" in dados:
            produtos = produtos.filter(categoria__slug=dados.get("categoria"))
    ids_categorias = produtos.values_list("categoria", flat=True).distinct()
    categorias = Categoria.objects.filter(id__in=ids_categorias)
    minimo, maximo = preco_minimo_maximo(produtos)
    ordem = request.GET.get("ordem", "menor-preco")
    produtos = ordenar_produtos(produtos, ordem)
    context = {"produtos": produtos, "minimo": minimo, "maximo": maximo,
               "categorias": categorias}
    return render(request, 'loja.html', context)

def ver_produto(request, id_produto, id_tamanho=None):
    tem_estoque = True
    tamanhos = {item for item in Tamanho.objects.filter()}
    tamanho_selecionado = None
    produto = Produto.objects.get(id=id_produto)
    if id_tamanho:
        tamanho_selecionado = Tamanho.objects.get(id=id_tamanho)
        valor = produto.preco + tamanho_selecionado.adicional
    else:
        valor = produto.preco
    similares = Produto.objects.filter(categoria__id=produto.categoria.id, tipo__id=produto.tipo.id).exclude(
        id=produto.id)[:4]
    context = {"produto": produto, "tamanhos": tamanhos, "tamanho_selecionado": tamanho_selecionado, "similares": similares,
               "tem_estoque": tem_estoque, "valor": valor}
    return render(request, "ver_produto.html", context)

def adicionar_carrinho(request, id_produto):
    if request.method == "POST" and id_produto:
        dados = request.POST.dict()
        tamanho = dados.get("tamanho")
        if not tamanho:
            return redirect('loja')
        resposta = redirect('carrinho')
        if request.user.is_authenticated:
            cliente = request.user.cliente
        else:
            if request.COOKIES.get("id_sessao"):
                id_sessao = request.COOKIES.get("id_sessao")
            else:
                id_sessao = str(uuid.uuid4())
                resposta.set_cookie(key="id_sessao", value=id_sessao, max_age=60 * 60 * 24 * 30)
            cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
        produto = Produto.objects.get(id=id_produto)
        tamanho = Tamanho.objects.get(id=tamanho)
        pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False, produto=produto, tamanho=tamanho)
        pedido.quantidade += 1
        pedido.total = pedido.quantidade * (pedido.produto.preco + tamanho.adicional)
        pedido.save()
        return resposta
    else:
        return redirect('loja')

def remover_carrinho(request, id_produto):
    if request.method == "POST" and id_produto:
        dados = request.POST.dict()
        tamanho = dados.get("tamanho")
        if not tamanho:
            return redirect('loja')
        if request.user.is_authenticated:
            cliente = request.user.cliente
        else:
            if request.COOKIES.get("id_sessao"):
                id_sessao = request.COOKIES.get("id_sessao")
                cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
            else:
                return redirect('loja')
        tamanho = Tamanho.objects.get(id=tamanho)
        pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False, produto=id_produto, tamanho=tamanho)
        pedido.quantidade -= 1
        pedido.total = pedido.quantidade * (pedido.produto.preco + tamanho.adicional)
        pedido.save()
        if pedido.quantidade < 0:
            pedido.delete()
        return redirect('carrinho')
    else:
        return redirect('loja')

def pedido_selecionado(request, id_produto):
    if request.method == "POST" and id_produto:
        dados = request.POST.dict()
        tamanho = dados.get("tamanho")
        if not tamanho:
            return redirect('loja')
        if request.user.is_authenticated:
            cliente = request.user.cliente
        else:
            if request.COOKIES.get("id_sessao"):
                id_sessao = request.COOKIES.get("id_sessao")
                cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
            else:
                return redirect('loja')
        pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False, produto=id_produto,
                                                  tamanho=tamanho)
        if pedido.adicheckout == False:
            pedido.adicheckout = True
        elif pedido.adicheckout == True:
            pedido.adicheckout = False
        pedido.save()
        return redirect('carrinho')
    else:
        return redirect('loja')

def carrinho(request):
    if request.user.is_authenticated:
        cliente = request.user.cliente
    else:
        if request.COOKIES.get("id_sessao"):
            id_sessao = request.COOKIES.get("id_sessao")
            cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
        else:
            context = {"cliente_existente": False, "pedidos": None}
            return render(request, 'carrinho.html', context)
    pedidos = Pedido.objects.filter(cliente=cliente, finalizado=False)
    total_selecionado = 0
    quantidade_selecionada = 0
    for item in pedidos:
        if item.adicheckout == True:
            total_selecionado += item.total
            quantidade_selecionada += item.quantidade
    context = {"pedidos": pedidos, "cliente_existente": True, "total_selecionado": total_selecionado, "quantidade_selecionada": quantidade_selecionada}
    return render(request, 'carrinho.html', context)

def checkout(request):
    if request.user.is_authenticated:
        cliente = request.user.cliente
    else:
        if request.COOKIES.get("id_sessao"):
            id_sessao = request.COOKIES.get("id_sessao")
            cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
        else:
            return redirect('loja')
    pedido = Pedido.objects.filter(cliente=cliente, finalizado=False, adicheckout=True)
    enderecos = Endereco.objects.filter(cliente=cliente)
    total_selecionado = 0
    quantidade_selecionada = 0
    for item in pedido:
        total_selecionado += item.total
        quantidade_selecionada += item.quantidade
    context = {"pedido": pedido, "enderecos": enderecos, "erro": None, "total_selecionado": total_selecionado, "quantidade_selecionada": quantidade_selecionada}
    return render(request, 'checkout.html', context)

def finalizar_pedido(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            cliente = request.user.cliente
        else:
            if request.COOKIES.get("id_sessao"):
                id_sessao = request.COOKIES.get("id_sessao")
                cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
            else:
                return redirect('loja')
        pedido = Pedido.objects.filter(cliente=cliente, finalizado=False, adicheckout=True)
        erro = None
        dados = request.POST.dict()
        total = dados.get("total")
        total = float(total.replace(",", "."))
        preco_total = 0
        for item in pedido:
            preco_total += item.total

        if total != float(preco_total):
            erro = "preco"

        if not "endereco" in dados:
            erro = "endereco"
        else:
            id_endereco = dados.get("endereco")
            endereco = Endereco.objects.get(id=id_endereco)
            pedido.endereco = endereco
            pedido.save()

        if not request.user.is_authenticated:
            email = dados.get("email")
            try:
                validate_email(email)
            except ValidationError:
                erro = "email"
            if not erro:
                clientes = Cliente.objects.filter(email=email)
                if clientes:
                    pedido.cliente = clientes[0]
                else:
                    pedido.cliente.email = email
                    pedido.cliente.save()

        quantidade_de_pedidos = 0
        for item in pedido:
            quantidade_de_pedidos = quantidade_de_pedidos + 1
        if erro:
            enderecos = Endereco.objects.filter(cliente=pedido.cliente)
            context = {"erro": erro, "pedido": pedido, "enderecos": enderecos}
            return render(request, "checkout.html", context)
        else:
            link = request.build_absolute_uri(reverse('finalizar_pagamento'))
            link_pagamento, id_pagamento = criar_pagamento(pedido, link)
            status = Status_pedido.object.get(id=2)
            if quantidade_de_pedidos > 1:
                for item in pedido:
                    codigo_transacao = f"C{item.cliente.id}-{datetime.now().timestamp()}"
                    item.codigo_transacao = codigo_transacao
                    item.id_pagamento = id_pagamento
                    item.status = status
                    item.save()
            elif quantidade_de_pedidos == 1:
                for item in pedido:
                    codigo_transacao = f"{item.id}-{datetime.now().timestamp()}"
                    item.codigo_transacao = codigo_transacao
                    item.id_pagamento = id_pagamento
                    item.status = status
                    item.save()
            return redirect(link_pagamento)
    else:
        return redirect("loja")


def finalizar_pagamento(request):
    dados = request.GET.dict()
    status = dados.get("status")
    id_pagamento = dados.get("preference_id")
    if status == "approved":
        pedidos = Pedido.objects.filter(id_pagamento=id_pagamento)
        for item in pedidos:
            item.pagamento_aprovado = True
            item.finalizado = True
            item.data_finalizacao = datetime.now()
            item.adicheckout = False
            item.save()
        enviar_email_compra(pedidos)
        if request.user.is_authenticated:
            return redirect("meus_pedidos")
        else:
            return redirect("pedido_aprovado", pedidos.id)
    else:
        return redirect("checkout")


def pedido_aprovado(request, id_pedido):
    pedido = Pedido.objects.filter(id=id_pedido)
    context = {"pedido": pedido}
    return render(request, "pedido_aprovado.html", context)


def adicionar_endereco(request):
    if request.method == "POST":
        # tratar o envio do formulario
        if request.user.is_authenticated:
            cliente = request.user.cliente
        else:
            if request.COOKIES.get("id_sessao"):
                id_sessao = request.COOKIES.get("id_sessao")
                cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
            else:
                return redirect('loja')
        dados = request.POST.dict()
        endereco = Endereco.objects.create(cliente=cliente, rua=dados.get("rua"), numero=int(dados.get("numero")),
                                           estado=dados.get("estado"), cidade=dados.get("cidade"),
                                           cep=dados.get("cep"), complemento=dados.get("complemento"),
                                           telefone=int(dados.get("telefone")), nome_cliente=dados.get("nome_cliente"))
        endereco.save()
        return redirect("checkout")
    else:
        context = {}
        return render(request, "adicionar_endereco.html", context)


@login_required
def minha_conta(request):
    erro = None
    alterado = False
    if request.method == "POST":
        dados = request.POST.dict()
        if "senha_atual" in dados:
            # esta modificando senha
            senha_atual = dados.get("senha_atual")
            nova_senha = dados.get("nova_senha")
            nova_senha_confirmacao = dados.get("nova_senha_confirmacao")
            if nova_senha == nova_senha_confirmacao:
                # verificar se a senha atual ta certa
                usuario = authenticate(request, username=request.user.email, password=senha_atual)
                if usuario:
                    usuario.set_password(nova_senha)
                    usuario.save()
                    alterado = True
                else:
                    erro = "senha_incorreta"
            else:
                erro = "senhas_diferentes"
        elif "email" in dados:
            email = dados.get("email")
            telefone = dados.get("telefone")
            nome = dados.get("nome")
            if email != request.user.email:
                usuarios = User.objects.filter(email=email)
                if len(usuarios) > 0:
                    erro = "email_existente"
            if not erro:
                cliente = request.user.cliente
                cliente.email = email
                request.user.email = email
                request.user.username = email
                cliente.nome = nome
                cliente.telefone = telefone
                cliente.save()
                request.user.save()
                alterado = True
        else:
            erro = "formulario_invalido"
    context = {"erro": erro, "alterado": alterado}
    return render(request, 'usuario/minha_conta.html', context)


@login_required
def meus_pedidos(request):
    cliente = request.user.cliente
    pedidos = Pedido.objects.filter(finalizado=True, cliente=cliente).order_by("-data_finalizacao")
    context = {"pedidos": pedidos}
    return render(request, "usuario/meus_pedidos.html", context)


def fazer_login(request):
    erro = False
    if request.user.is_authenticated:
        return redirect('loja')
    if request.method == "POST":
        dados = request.POST.dict()
        if "email" in dados and "senha" in dados:
            email = dados.get("email")
            senha = dados.get("senha")
            usuario = authenticate(request, username=email, password=senha)
            if usuario:
                login(request, usuario)
                return redirect('loja')
            else:
                erro = True
        else:
            erro = True
    context = {"erro": erro}
    return render(request, 'usuario/login.html', context)


def criar_conta(request):
    erro = None
    if request.user.is_authenticated:
        return redirect("loja")
    if request.method == "POST":
        dados = request.POST.dict()
        if "email" in dados and "senha" in dados and "confirmacao_senha" in dados:
            # criar conta
            email = dados.get("email")
            senha = dados.get("senha")
            confirmacao_senha = dados.get("confirmacao_senha")
            try:
                validate_email(email)
            except ValidationError:
                erro = "email_invalido"
            if senha == confirmacao_senha:
                # criar conta
                usuario, criado = User.objects.get_or_create(username=email, email=email)
                if not criado:
                    erro = "usuario_existente"
                else:
                    usuario.set_password(senha)
                    usuario.save()
                    # fazer o login
                    usuario = authenticate(request, username=email, password=senha)
                    login(request, usuario)
                    # criar o cliente
                    # verificar se existe o id_sessao nos cookies
                    if request.COOKIES.get("id_sessao"):
                        id_sessao = request.COOKIES.get("id_sessao")
                        cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
                    else:
                        cliente, criado = Cliente.objects.get_or_create(email=email)
                    cliente.usuario = usuario
                    cliente.email = email
                    cliente.save()
                    return redirect("loja")
            else:
                erro = "senhas_diferentes"
        else:
            erro = "preenchimento"
    context = {"erro": erro}
    return render(request, "usuario/criar_conta.html", context)


@login_required
def fazer_logout(request):
    logout(request)
    return redirect("fazer_login")


@login_required
def gerenciar_loja(request):
    if request.user.groups.filter(name="equipe").exists():
        finalizado = "todos"
        pedidos = Pedido.objects.filter()
        soma_total = 0
        quantidade_pedidos = 0
        quantidade_produtos = 0
        if request.method == "POST":
            dados = request.POST.dict()
            finalizado = dados.get("finalizado")
            if finalizado == "sim":
                pedidos = Pedido.objects.filter(finalizado=True)
                for item in pedidos:
                    soma_total += item.total
                    quantidade_pedidos += 1
                    quantidade_produtos += item.quantidade
            elif finalizado == "nao":
                pedidos = Pedido.objects.filter(finalizado=False)
                for item in pedidos:
                    soma_total += item.total
                    quantidade_pedidos += 1
                    quantidade_produtos += item.quantidade
        else:
            pedidos = Pedido.objects.filter()
            for item in pedidos:
                soma_total += item.total
                quantidade_pedidos += 1
                quantidade_produtos += item.quantidade

        context = {"pedidos": pedidos, "finalizado": finalizado, "soma_total": soma_total, "quantidade_pedidos": quantidade_pedidos,
                   "quantidade_produtos": quantidade_produtos}
        return render(request, "interno/gerenciar_loja.html", context=context)
    else:
        redirect('loja')

def atualizar_status(request):
    pedidos = Pedido.objects.filter(finalizado=True)
    status = Status_pedido.objects.all()
    pedidos = pedidos.order_by('status__nome')
    if request.method == "POST":
        if request.POST.getlist('pedido') and request.POST.get('status'):
            dados = request.POST.getlist('pedido')
            status_selecionado = request.POST.get('status')
            novo_status = Status_pedido.objects.get(id=status_selecionado)
            for item in dados:
                pedido_selecionado = pedidos.get(id=item)
                pedido_selecionado.status = novo_status
                pedido_selecionado.save()
            context = {"pedidos": pedidos, "status": status}
            return render(request, "interno/atualizar_status.html", context)
    context = {"pedidos": pedidos, "status": status}
    return render(request, "interno/atualizar_status.html", context)

@login_required
def exportar_relatorio(request, relatorio):
    if request.user.groups.filter(name="equipe").exists():
        if relatorio == "pedido":
            informacoes = Pedido.objects.filter(finalizado=True)
        elif relatorio == "cliente":
            informacoes = Cliente.objects.all()
        elif relatorio == "endereco":
            informacoes = Endereco.objects.all()
        return exportar_csv(informacoes)
    else:
        return redirect('gerenciar_loja')