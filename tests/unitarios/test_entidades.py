# -*- coding: utf-8 -*-
import unittest
from decimal import Decimal

import mock

from pagador_paypal_transparente import entidades


class PayPalConfiguracaoMeioPagamento(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(PayPalConfiguracaoMeioPagamento, self).__init__(*args, **kwargs)
        self.campos = ['ativo', 'usuario', 'valor_minimo_aceitado', 'valor_minimo_parcela', 'mostrar_parcelamento', 'parcelas_sem_juros']
        self.codigo_gateway = 3

    @mock.patch('pagador_paypal.entidades.ConfiguracaoMeioPagamento.preencher_gateway', mock.MagicMock())
    def test_deve_ter_os_campos_especificos_na_classe(self):
        entidades.ConfiguracaoMeioPagamento(234).campos.should.be.equal(self.campos)

    @mock.patch('pagador_paypal.entidades.ConfiguracaoMeioPagamento.preencher_gateway', mock.MagicMock())
    def test_deve_ter_codigo_gateway(self):
        entidades.ConfiguracaoMeioPagamento(234).codigo_gateway.should.be.equal(self.codigo_gateway)

    @mock.patch('pagador_paypal.entidades.ConfiguracaoMeioPagamento.preencher_gateway', autospec=True)
    def test_deve_preencher_gateway_na_inicializacao(self, preencher_mock):
        configuracao = entidades.ConfiguracaoMeioPagamento(234)
        preencher_mock.assert_called_with(configuracao, self.codigo_gateway, self.campos)

    @mock.patch('pagador_paypal.entidades.ConfiguracaoMeioPagamento.preencher_gateway', mock.MagicMock())
    def test_deve_definir_formulario_na_inicializacao(self):
        configuracao = entidades.ConfiguracaoMeioPagamento(234)
        configuracao.formulario.should.be.a('pagador_paypal.cadastro.FormularioPayPal')

    @mock.patch('pagador_paypal.entidades.ConfiguracaoMeioPagamento.preencher_gateway', mock.MagicMock())
    def test_deve_ser_aplicacao(self):
        configuracao = entidades.ConfiguracaoMeioPagamento(234)
        configuracao.eh_aplicacao.should.be.falsy


class PayPalMalote(unittest.TestCase):
    def test_deve_ter_propriedades_iniciais(self):
        configuracao = mock.MagicMock()
        malote = entidades.Malote(configuracao)
        malote.to_dict().should.be.equal({'BUTTONSOURCE': None, 'CANCELURL': None, 'EMAIL': None, 'LOCALECODE': 'pt_BR', 'METHOD': 'SetExpressCheckout', 'NOTIFYURL': None, 'PAYMENTREQUEST_0_AMT': None, 'PAYMENTREQUEST_0_CURRENCYCODE': 'BRL', 'PAYMENTREQUEST_0_INVNUM': None, 'PAYMENTREQUEST_0_ITEMAMT': None, 'PAYMENTREQUEST_0_NOTIFYURL': None, 'PAYMENTREQUEST_0_PAYMENTACTION': 'SALE', 'PAYMENTREQUEST_0_SHIPPINGAMT': None, 'PAYMENTREQUEST_0_SHIPTOCITY': None, 'PAYMENTREQUEST_0_SHIPTOCOUNTRYCODE': 'BR', 'PAYMENTREQUEST_0_SHIPTONAME': None, 'PAYMENTREQUEST_0_SHIPTOPHONENUM': None, 'PAYMENTREQUEST_0_SHIPTOSTATE': None, 'PAYMENTREQUEST_0_SHIPTOSTREET': None, 'PAYMENTREQUEST_0_SHIPTOSTREET2': None, 'PAYMENTREQUEST_0_SHIPTOZIP': None, 'PWD': None, 'RETURNURL': None, 'SIGNATURE': None, 'USER': None, 'VERSION': '108.0'})

    def test_deve_montar_malote_para_set_express(self):
        configuracao = mock.MagicMock(loja_id=2345)
        malote = entidades.Malote(configuracao)
        pedido = mock.MagicMock(
            numero=123,
            cliente={'email': 'cliente@email.com'},
            valor_total=Decimal('100.00'),
            valor_envio=Decimal('10.00'),
            valor_subtotal=Decimal('90.00'),
            valor_desconto=Decimal('5.00'),
            endereco_entrega={
                'nome': u'Nome endereço entrega', 'endereco': 'Rua entrega', 'numero': '51', 'complemento': 'lt 51',
                'bairro': 'Bairro', 'cidade': 'Cidade', 'cep': '12908-212', 'estado': 'RJ'
            },
            cliente_telefone=('21', '999999999'),
            itens=[
                mock.MagicMock(nome='Produto 1', sku='PROD01', quantidade=1, preco_venda=Decimal('40.00'), url_produto='url-prd-1'),
                mock.MagicMock(nome='Produto 2', sku='PROD02', quantidade=1, preco_venda=Decimal('50.00'), url_produto='url-prd-2'),
            ]
        )
        parametros = {'username': 'NOMEUSUARIO', 'password': 'SENHA', 'signature': 'ASSINATURA', 'button_source': 'BUTTON-SOURCE'}
        dados = {'next_url': 'url-next'}
        malote.monta_conteudo(pedido, parametros, dados)
        malote.to_dict().should.be.equal({'BUTTONSOURCE': 'BUTTON-SOURCE', 'CANCELURL': 'http://localhost:5000/pagador/meio-pagamento/paypal/retorno/2345/resultado?sucesso=false&next_url=url-next&referencia=123', 'EMAIL': 'cliente@email.com', 'LOCALECODE': 'pt_BR', 'L_PAYMENTREQUEST_0_AMT1': '40.00', 'L_PAYMENTREQUEST_0_AMT2': '50.00', 'L_PAYMENTREQUEST_0_AMT3': '-5.00', 'L_PAYMENTREQUEST_0_DESC1': '', 'L_PAYMENTREQUEST_0_DESC2': '', 'L_PAYMENTREQUEST_0_ITEMURL1': 'url-prd-1', 'L_PAYMENTREQUEST_0_ITEMURL2': 'url-prd-2', 'L_PAYMENTREQUEST_0_NAME1': 'Produto 1', 'L_PAYMENTREQUEST_0_NAME2': 'Produto 2', 'L_PAYMENTREQUEST_0_NAME3': 'Desconto', 'L_PAYMENTREQUEST_0_NUMBER1': 'PROD01', 'L_PAYMENTREQUEST_0_NUMBER2': 'PROD02', 'L_PAYMENTREQUEST_0_QTY1': '1.00', 'L_PAYMENTREQUEST_0_QTY2': '1.00', 'L_PAYMENTREQUEST_0_QTY3': 1, 'METHOD': 'SetExpressCheckout', 'NOTIFYURL': 'http://localhost:5000/pagador/meio-pagamento/paypal/retorno/2345/notificacao?referencia=123', 'PAYMENTREQUEST_0_AMT': '100.00', 'PAYMENTREQUEST_0_CURRENCYCODE': 'BRL', 'PAYMENTREQUEST_0_INVNUM': 123, 'PAYMENTREQUEST_0_ITEMAMT': '90.00', 'PAYMENTREQUEST_0_NOTIFYURL': 'http://localhost:5000/pagador/meio-pagamento/paypal/retorno/2345/notificacao?referencia=123', 'PAYMENTREQUEST_0_PAYMENTACTION': 'SALE', 'PAYMENTREQUEST_0_SHIPPINGAMT': '10.00', 'PAYMENTREQUEST_0_SHIPTOCITY': 'Cidade', 'PAYMENTREQUEST_0_SHIPTOCOUNTRYCODE': 'BR', 'PAYMENTREQUEST_0_SHIPTONAME': 'Nome endere\xc3\xa7o entrega', 'PAYMENTREQUEST_0_SHIPTOPHONENUM': '21999999999', 'PAYMENTREQUEST_0_SHIPTOSTATE': 'RJ', 'PAYMENTREQUEST_0_SHIPTOSTREET': 'Rua entrega, 51 lt 51', 'PAYMENTREQUEST_0_SHIPTOSTREET2': 'Bairro', 'PAYMENTREQUEST_0_SHIPTOZIP': '12908-212', 'PWD': 'SENHA', 'RETURNURL': 'http://localhost:5000/pagador/meio-pagamento/paypal/retorno/2345/resultado?sucesso=true&next_url=url-next&referencia=123', 'SIGNATURE': 'ASSINATURA', 'USER': 'NOMEUSUARIO', 'VERSION': '108.0'})

    def test_deve_montar_malote_para_do_express(self):
        configuracao = mock.MagicMock(loja_id=2345)
        malote = entidades.Malote(configuracao, metodo='DoExpressCheckout')
        pedido = mock.MagicMock(
            numero=123,
            cliente={'email': 'cliente@email.com'},
            valor_total=Decimal('100.00'),
            valor_envio=Decimal('10.00'),
            valor_subtotal=Decimal('90.00'),
            valor_desconto=Decimal('5.00'),
            endereco_entrega={
                'nome': u'Nome endereço entrega', 'endereco': 'Rua entrega', 'numero': '51', 'complemento': 'lt 51',
                'bairro': 'Bairro', 'cidade': 'Cidade', 'cep': '12908-212', 'estado': 'RJ'
            },
            cliente_telefone=('21', '999999999'),
            itens=[
                mock.MagicMock(nome='Produto 1', sku='PROD01', quantidade=1, preco_venda=Decimal('40.00'), url_produto='url-prd-1'),
                mock.MagicMock(nome='Produto 2', sku='PROD02', quantidade=1, preco_venda=Decimal('50.00'), url_produto='url-prd-2'),
            ]
        )
        parametros = {'username': 'NOMEUSUARIO', 'password': 'SENHA', 'signature': 'ASSINATURA', 'button_source': 'BUTTON-SOURCE'}
        dados = {'next_url': 'url-next', 'token': 'TOKEN', 'PayerID': 'PAYER-ID'}
        malote.monta_conteudo(pedido, parametros, dados)
        malote.to_dict().should.be.equal({'BUTTONSOURCE': 'BUTTON-SOURCE', 'CANCELURL': 'http://localhost:5000/pagador/meio-pagamento/paypal/retorno/2345/resultado?sucesso=false&next_url=url-next&referencia=123', 'EMAIL': 'cliente@email.com', 'LOCALECODE': 'pt_BR', 'L_PAYMENTREQUEST_0_AMT1': '40.00', 'L_PAYMENTREQUEST_0_AMT2': '50.00', 'L_PAYMENTREQUEST_0_AMT3': '-5.00', 'L_PAYMENTREQUEST_0_DESC1': '', 'L_PAYMENTREQUEST_0_DESC2': '', 'L_PAYMENTREQUEST_0_ITEMURL1': 'url-prd-1', 'L_PAYMENTREQUEST_0_ITEMURL2': 'url-prd-2', 'L_PAYMENTREQUEST_0_NAME1': 'Produto 1', 'L_PAYMENTREQUEST_0_NAME2': 'Produto 2', 'L_PAYMENTREQUEST_0_NAME3': 'Desconto', 'L_PAYMENTREQUEST_0_NUMBER1': 'PROD01', 'L_PAYMENTREQUEST_0_NUMBER2': 'PROD02', 'L_PAYMENTREQUEST_0_QTY1': '1.00', 'L_PAYMENTREQUEST_0_QTY2': '1.00', 'L_PAYMENTREQUEST_0_QTY3': 1, 'METHOD': 'DoExpressCheckout', 'NOTIFYURL': 'http://localhost:5000/pagador/meio-pagamento/paypal/retorno/2345/notificacao?referencia=123', 'PAYERID': 'PAYER-ID', 'PAYMENTREQUEST_0_AMT': '100.00', 'PAYMENTREQUEST_0_CURRENCYCODE': 'BRL', 'PAYMENTREQUEST_0_INVNUM': 123, 'PAYMENTREQUEST_0_ITEMAMT': '90.00', 'PAYMENTREQUEST_0_NOTIFYURL': 'http://localhost:5000/pagador/meio-pagamento/paypal/retorno/2345/notificacao?referencia=123', 'PAYMENTREQUEST_0_PAYMENTACTION': 'SALE', 'PAYMENTREQUEST_0_SHIPPINGAMT': '10.00', 'PAYMENTREQUEST_0_SHIPTOCITY': 'Cidade', 'PAYMENTREQUEST_0_SHIPTOCOUNTRYCODE': 'BR', 'PAYMENTREQUEST_0_SHIPTONAME': 'Nome endere\xc3\xa7o entrega', 'PAYMENTREQUEST_0_SHIPTOPHONENUM': '21999999999', 'PAYMENTREQUEST_0_SHIPTOSTATE': 'RJ', 'PAYMENTREQUEST_0_SHIPTOSTREET': 'Rua entrega, 51 lt 51', 'PAYMENTREQUEST_0_SHIPTOSTREET2': 'Bairro', 'PAYMENTREQUEST_0_SHIPTOZIP': '12908-212', 'PWD': 'SENHA', 'RETURNURL': 'http://localhost:5000/pagador/meio-pagamento/paypal/retorno/2345/resultado?sucesso=true&next_url=url-next&referencia=123', 'SIGNATURE': 'ASSINATURA', 'TOKEN': 'TOKEN', 'USER': 'NOMEUSUARIO', 'VERSION': '108.0'})
