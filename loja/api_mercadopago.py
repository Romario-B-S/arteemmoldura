import mercadopago

#public_key = "APP_USR-1c522bb0-55b4-4f08-ab95-561eeb2232a2"
#token = "APP_USR-2875130686594154-042311-d0333f0492779eb253c92c693273bd37-619713008"

public_key = "TEST-9f099a33-8d25-4562-84b0-0c4c25628cad"
token = "TEST-2875130686594154-042311-ee8713fdecb0d5f2b6f9f128e6616703-619713008"

def criar_pagamento(pedido, link):
    # Configure as credenciais
    sdk = mercadopago.SDK(token)
    # Crie um item na preferência

    # itens que ele está comprando no formato de dicionário
    itens = []
    n_pedido = []
    for item in pedido:
        quantidade = int(item.quantidade)
        nome_produto = item.produto.nome
        preco_unitario = float(item.produto.preco)
        n_pedido.append(item.id)
        itens.append({
            "title": nome_produto + str(item.id),
            "quantity": quantidade,
            "unit_price": preco_unitario,
        })

    preference_data = {
        "items": itens,
        "auto_return": "all",
        "back_urls": {
            "success": link,
            "pending": link,
            "failure": link,
        }
    }
    resposta = sdk.preference().create(preference_data)
    link_pagamento = resposta["response"]["init_point"]
    id_pagamento = resposta["response"]["id"]
    return link_pagamento, id_pagamento
