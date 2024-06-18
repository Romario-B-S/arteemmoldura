from .models import Pedido, Cliente, Categoria, Tipo


def carrinho(request):
    quantidade_produtos_carrinho = 0
    if request.user.is_authenticated:
        cliente = request.user.cliente
    else:
        if request.COOKIES.get("id_sessao"):
            id_sessao = request.COOKIES.get("id_sessao")
            cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
        else:
            return {"quantidade_produtos_carrinho": quantidade_produtos_carrinho}
    pedido = Pedido.objects.filter(cliente=cliente, finalizado=False)
    for item in pedido:
        quantidade_produtos_carrinho += item.quantidade
    return {"quantidade_produtos_carrinho": quantidade_produtos_carrinho}


def categorias_tipos(request):
    categorias_navegacao = Categoria.objects.all()
    tipos_navegacao = Tipo.objects.all()

    return {"categorias_navegacao": categorias_navegacao, "tipos_navegacao": tipos_navegacao}

def faz_parte_equipe(request):
    equipe = False
    if request.user.is_authenticated:
        if request.user.groups.filter(name="equipe").exists():
            equipe = True
    return {"equipe": equipe}