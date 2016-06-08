# -*- coding: utf-8 -*-
from pagador import configuracoes, entidades
from pagador_paypal_transparente import cadastro

CODIGO_GATEWAY = 3


class Malote(entidades.Malote):
    _chaves_alternativas_para_serializacao = {
        'user': 'USER',
        'pwd': 'PWD',
        'signature': 'SIGNATURE',
        'version': 'VERSION',
        'method': 'METHOD',
        'token': 'TOKEN',
        'payerid': 'PAYERID',
        'notifyurl': 'NOTIFYURL',
        'returnurl': 'RETURNURL',
        'cancelurl': 'CANCELURL',
        'buttonsource': 'BUTTONSOURCE',
        'localcode': 'LOCALECODE',
        'hdrimg': 'HDRIMG',
        'email': 'EMAIL',
        'paymentrequest_0_paymentaction': 'PAYMENTREQUEST_0_PAYMENTACTION',
        'paymentrequest_0_amt': 'PAYMENTREQUEST_0_AMT',
        'paymentrequest_0_shippingamt': 'PAYMENTREQUEST_0_SHIPPINGAMT',
        'paymentrequest_0_currencycode': 'PAYMENTREQUEST_0_CURRENCYCODE',
        'paymentrequest_0_itemamt': 'PAYMENTREQUEST_0_ITEMAMT',
        'paymentrequest_0_invnum': 'PAYMENTREQUEST_0_INVNUM',
        'paymentrequest_0_notifyurl': 'PAYMENTREQUEST_0_NOTIFYURL',
        'paymentrequest_0_shiptoname': 'PAYMENTREQUEST_0_SHIPTONAME',
        'paymentrequest_0_shiptostreet': 'PAYMENTREQUEST_0_SHIPTOSTREET',
        'paymentrequest_0_shiptostreet2': 'PAYMENTREQUEST_0_SHIPTOSTREET2',
        'paymentrequest_0_shiptocity': 'PAYMENTREQUEST_0_SHIPTOCITY',
        'paymentrequest_0_shiptostate': 'PAYMENTREQUEST_0_SHIPTOSTATE',
        'paymentrequest_0_shiptozip': 'PAYMENTREQUEST_0_SHIPTOZIP',
        'paymentrequest_0_shiptocountrycode': 'PAYMENTREQUEST_0_SHIPTOCOUNTRYCODE',
        'paymentrequest_0_shiptophonenum': 'PAYMENTREQUEST_0_SHIPTOPHONENUM',
    }

    def __init__(self, configuracao, metodo='SetExpressCheckout'):
        super(Malote, self).__init__(configuracao)
        self.version = configuracoes.PAYPAL_VERSION
        self.method = metodo
        self.localcode = 'pt_BR'
        self.user = None
        self.pwd = None
        self.signature = None
        self.buttonsource = None
        self.notifyurl = None
        self.returnurl = None
        self.cancelurl = None
        self.email = None
        self.paymentrequest_0_paymentaction = 'SALE'
        self.paymentrequest_0_amt = None
        self.paymentrequest_0_shippingamt = None
        self.paymentrequest_0_currencycode = 'BRL'
        self.paymentrequest_0_itemamt = None
        self.paymentrequest_0_invnum = None
        self.paymentrequest_0_notifyurl = None
        self.paymentrequest_0_shiptoname = None
        self.paymentrequest_0_shiptostreet = None
        self.paymentrequest_0_shiptostreet2 = None
        self.paymentrequest_0_shiptocity = None
        self.paymentrequest_0_shiptostate = None
        self.paymentrequest_0_shiptozip = None
        self.paymentrequest_0_shiptocountrycode = 'BR'
        self.paymentrequest_0_shiptophonenum = None

    def monta_conteudo(self, pedido, parametros_contrato=None, dados=None):
        if 'next_url' not in dados:
            raise self.DadosInvalidos(u'Os dados de envio não foram processados corretamente no carrinho.')
        notification_url = configuracoes.NOTIFICACAO_URL.format('pptransparente', self.configuracao.loja_id)
        self.user = parametros_contrato['username']
        self.pwd = parametros_contrato['password']
        self.signature = parametros_contrato['signature']
        self.buttonsource = parametros_contrato['button_source']
        self.notifyurl = '{}/{}?referencia={}'.format(notification_url, entidades.TipoRetorno.notificacao, pedido.numero)
        self.returnurl = '{}/{}?sucesso=true&next_url={}&referencia={}'.format(notification_url, entidades.TipoRetorno.resultado, dados['next_url'], pedido.numero)
        self.cancelurl = '{}/{}?sucesso=false&next_url={}&referencia={}'.format(notification_url, entidades.TipoRetorno.resultado, dados['next_url'], pedido.numero)
        self.email = pedido.cliente['email']
        if 'token' in dados:
            setattr(self, 'token', dados['token'])
        if 'PayerID' in dados:
            setattr(self, 'payerid', dados['PayerID'])
        self.paymentrequest_0_amt = self.formatador.formata_decimal(pedido.valor_total)
        self.paymentrequest_0_shippingamt = self.formatador.formata_decimal(pedido.valor_envio)
        self.paymentrequest_0_itemamt = self.formatador.formata_decimal(pedido.valor_subtotal)
        self.paymentrequest_0_invnum = pedido.numero
        self.paymentrequest_0_notifyurl = '{}/{}?referencia={}'.format(notification_url, entidades.TipoRetorno.notificacao, pedido.numero)
        self.paymentrequest_0_shiptoname = self.formatador.trata_unicode_com_limite(pedido.endereco_entrega['nome'])
        self.paymentrequest_0_shiptostreet = u"{}, {} {}".format(pedido.endereco_entrega['endereco'], pedido.endereco_entrega['numero'], pedido.endereco_entrega['complemento'])
        self.paymentrequest_0_shiptostreet2 = self.formatador.trata_unicode_com_limite(pedido.endereco_entrega['bairro'])
        self.paymentrequest_0_shiptocity = self.formatador.trata_unicode_com_limite(pedido.endereco_entrega['cidade'])
        self.paymentrequest_0_shiptostate = self.formatador.trata_unicode_com_limite(pedido.endereco_entrega['estado'])
        self.paymentrequest_0_shiptozip = self.formatador.trata_unicode_com_limite(pedido.endereco_entrega['cep'])
        self.paymentrequest_0_shiptophonenum = '{}{}'.format(*pedido.cliente_telefone)
        indice_final = 1
        for indice, item in enumerate(pedido.itens):
            self._cria_item(indice, item)
            indice_final = indice + 1
        if pedido.valor_desconto:
            nomes = {
                'NAME': 'Desconto',
                'AMT': self.formatador.formata_decimal(pedido.valor_desconto * -1),
                'QTY': 1,
            }
            self.define_atributos(nomes, indice_final + 1)

    def _cria_item(self, indice, item_pedido):
        indice += 1
        nomes = {
            'NAME': self.formatador.trata_unicode_com_limite(item_pedido.nome, 127),
            'DESC': '',
            'AMT': self.formatador.formata_decimal(item_pedido.preco_venda),
            'QTY': self.formatador.formata_decimal(item_pedido.quantidade),
            'NUMBER': self.formatador.trata_unicode_com_limite(item_pedido.sku, 127),
            'ITEMURL': item_pedido.url_produto
        }
        self.define_atributos(nomes, indice)

    def define_atributos(self, nomes, indice):
        for chave in nomes:
            atributo = 'L_PAYMENTREQUEST_0_{}{}'.format(chave, indice)
            setattr(self, atributo.lower(), nomes[chave])
            self._chaves_alternativas_para_serializacao[atributo.lower()] = atributo


class ConfiguracaoMeioPagamento(entidades.ConfiguracaoMeioPagamento):
    modos_pagamento_aceitos = {
        'cartoes': ['visa', 'mastercard', 'amex', 'elo', 'hiper', 'hipercard']
    }

    def __init__(self, loja_id, codigo_pagamento=None, eh_listagem=False):
        self.campos = ['ativo', 'usuario', 'valor_minimo_aceitado', 'valor_minimo_parcela', 'mostrar_parcelamento', 'parcelas_sem_juros']
        self.codigo_gateway = CODIGO_GATEWAY
        self.eh_gateway = True
        super(ConfiguracaoMeioPagamento, self).__init__(loja_id, codigo_pagamento, eh_listagem=eh_listagem)
        if not self.eh_listagem:
            self.formulario = cadastro.FormularioPayPalTransparente()
