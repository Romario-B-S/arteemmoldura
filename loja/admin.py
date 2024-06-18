from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Cliente)
admin.site.register(Categoria)
admin.site.register(Tipo)
admin.site.register(Produto)
#admin.site.register(ItemEstoque)
admin.site.register(Endereco)
admin.site.register(Pedido)
#admin.site.register(ItensPedido)
admin.site.register(Banner)
admin.site.register(Tamanho)
admin.site.register(Pagamento)
admin.site.register(Status_pedido)
admin.site.register(Transportadora)
admin.site.register(Tabela_frete)



