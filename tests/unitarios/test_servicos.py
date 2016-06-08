# -*- coding: utf-8 -*-
from decimal import Decimal
import unittest
import mock
from pagador_paypal_transparente import servicos


class PayPalCredenciais(unittest.TestCase):
    def test_deve_definir_propriedades(self):
        credenciador = servicos.Credenciador(configuracao=mock.MagicMock())
        credenciador.tipo.should.be.equal(credenciador.TipoAutenticacao.form_urlencode)
        credenciador.chave.should.be.equal('SUBJECT')

    def test_deve_retornar_credencial_baseado_no_usuario(self):
        configuracao = mock.MagicMock(usuario='usuario@paypal.com')
        credenciador = servicos.Credenciador(configuracao=configuracao)
        credenciador.obter_credenciais().should.be.equal('usuario@paypal.com')


class PayPalAck(unittest.TestCase):
    def test_deve_definir_propriedades(self):
        ack = servicos.Ack('nada-ainda')
        ack.sucesso.should.be.falsy
        ack.falha.should.be.falsy

    def test_deve_ser_sucesso_se_success(self):
        ack = servicos.Ack('success')
        ack.sucesso.should.be.truthy
        ack.falha.should.be.falsy

    def test_deve_ser_sucesso_se_successwithwarning(self):
        ack = servicos.Ack('successwithwarning')
        ack.sucesso.should.be.truthy
        ack.falha.should.be.falsy

    def test_deve_ser_falha_se_failure(self):
        ack = servicos.Ack('failure')
        ack.sucesso.should.be.falsy
        ack.falha.should.be.truthy


class PayPalEntregaPagamento(unittest.TestCase):
    @mock.patch('pagador_paypal.servicos.EntregaPagamento.obter_conexao', mock.MagicMock())
    def test_deve_dizer_que_tem_malote(self):
        entregador = servicos.EntregaPagamento(1234)
        entregador.tem_malote.should.be.truthy

    @mock.patch('pagador_paypal.servicos.EntregaPagamento.obter_conexao', mock.MagicMock())
    def test_deve_dizer_que_faz_http(self):
        entregador = servicos.EntregaPagamento(1234)
        entregador.faz_http.should.be.truthy

    @mock.patch('pagador_paypal.servicos.EntregaPagamento.obter_conexao', mock.MagicMock())
    def test_deve_definir_resposta(self):
        entregador = servicos.EntregaPagamento(1234)
        entregador.resposta.should.be.none

    @mock.patch('pagador_paypal.servicos.EntregaPagamento.obter_conexao', mock.MagicMock())
    def test_deve_definir_url_com_sandbox(self):
        entregador = servicos.EntregaPagamento(1234)
        entregador.url.should.be.equal('https://api-3t.sandbox.paypal.com/nvp')

    @mock.patch('pagador_paypal.servicos.EntregaPagamento.obter_conexao', mock.MagicMock())
    @mock.patch('pagador_paypal.servicos.EntregaPagamento.sandbox', '')
    def test_deve_definir_url_sem_sandbox(self):
        entregador = servicos.EntregaPagamento(1234)
        entregador.url.should.be.equal('https://api-3t.paypal.com/nvp')

    @mock.patch('pagador_paypal.servicos.EntregaPagamento.obter_conexao')
    def test_deve_montar_conexao(self, obter_mock):
        obter_mock.return_value = 'conexao'
        entregador = servicos.EntregaPagamento(1234)
        entregador.conexao.should.be.equal('conexao')
        obter_mock.assert_called_with(formato_envio='application/x-www-form-urlencoded', formato_resposta='application/x-www-form-urlencoded')

    @mock.patch('pagador_paypal.servicos.EntregaPagamento.obter_conexao', mock.MagicMock())
    @mock.patch('pagador_paypal.servicos.Credenciador')
    def test_deve_definir_credenciais(self, credenciador_mock):
        entregador = servicos.EntregaPagamento(1234)
        credenciador_mock.return_value = 'credenciador'
        entregador.configuracao = 'configuracao'
        entregador.define_credenciais()
        entregador.conexao.credenciador.should.be.equal('credenciador')
        credenciador_mock.assert_called_with(configuracao='configuracao')

    @mock.patch('pagador_paypal.servicos.EntregaPagamento.obter_conexao', mock.MagicMock())
    def test_deve_enviar_pagamento(self):
        entregador = servicos.EntregaPagamento(1234)
        entregador.malote = mock.MagicMock()
        entregador.malote.to_dict.return_value = 'malote-como-dicionario'
        entregador.conexao = mock.MagicMock()
        entregador.conexao.post.return_value = 'resposta'
        entregador.envia_pagamento()
        entregador.dados_enviados.should.be.equal('malote-como-dicionario')
        entregador.resposta.should.be.equal('resposta')

    @mock.patch('pagador_paypal.servicos.EntregaPagamento.obter_conexao', mock.MagicMock())
    def test_deve_usar_post_ao_enviar_pagamento(self):
        entregador = servicos.EntregaPagamento(1234)
        entregador.malote = mock.MagicMock()
        entregador.malote.to_dict.return_value = 'malote-como-dicionario'
        entregador.conexao = mock.MagicMock()
        entregador.envia_pagamento()
        entregador.conexao.post.assert_called_with(entregador.url, 'malote-como-dicionario')

    @mock.patch('pagador_paypal.servicos.EntregaPagamento.obter_conexao', mock.MagicMock())
    def test_deve_processar_dados_de_pagamento(self):
        entregador = servicos.EntregaPagamento(1234)
        entregador._processa_resposta = mock.MagicMock()
        entregador._processa_resposta.return_value = 'resposta-processada'
        entregador.processa_dados_pagamento()
        entregador._processa_resposta.assert_called_with()
        entregador.resultado.should.be.equal('resposta-processada')

    @mock.patch('pagador_paypal.servicos.EntregaPagamento.obter_conexao', mock.MagicMock())
    def test_deve_processar_resposta_sucesso(self):
        entregador = servicos.EntregaPagamento(1234)
        entregador.resposta = mock.MagicMock(conteudo={'ack': 'success', 'token': 'TOKEN'}, status_code=200, sucesso=True, erro_servidor=False, timeout=False, nao_autenticado=False, nao_autorizado=False)
        entregador.processa_dados_pagamento()
        entregador.resultado.should.be.equal({'url': 'https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_express-checkout&token=TOKEN', 'pago': False, 'fatal': False})

    @mock.patch('pagador_paypal.servicos.EntregaPagamento.obter_conexao', mock.MagicMock())
    def test_deve_processar_resposta_erro(self):
        entregador = servicos.EntregaPagamento(1234)
        entregador.resposta = mock.MagicMock(conteudo={}, status_code=500, sucesso=False, erro_servidor=True, timeout=False, nao_autenticado=False, nao_autorizado=False)
        entregador.processa_dados_pagamento()
        entregador.resultado.should.be.equal({'mensagem': u'O servidor do PayPal está indisponível nesse momento.', 'status_code': 500, 'pago': False, 'fatal': False})

    @mock.patch('pagador_paypal.servicos.EntregaPagamento.obter_conexao', mock.MagicMock())
    def test_deve_processar_resposta_timeout(self):
        entregador = servicos.EntregaPagamento(1234)
        entregador.resposta = mock.MagicMock(conteudo={}, status_code=408, sucesso=False, erro_servidor=False, timeout=True, nao_autenticado=False, nao_autorizado=False)
        entregador.processa_dados_pagamento()
        entregador.resultado.should.be.equal({'mensagem': u'O servidor do PayPal não respondeu em tempo útil.', 'status_code': 408, 'pago': False, 'fatal': False})

    @mock.patch('pagador_paypal.servicos.EntregaPagamento.obter_conexao', mock.MagicMock())
    def test_deve_processar_resposta_nao_autenticado(self):
        entregador = servicos.EntregaPagamento(1234)
        entregador.resposta = mock.MagicMock(conteudo={}, status_code=401, sucesso=False, erro_servidor=False, timeout=False, nao_autenticado=True, nao_autorizado=False)
        entregador.processa_dados_pagamento()
        entregador.resultado.should.be.equal({'mensagem': u'Autenticação da loja com o PayPal Falhou. Contate o SAC da loja.', 'status_code': 401, 'pago': False, 'fatal': False})

    @mock.patch('pagador_paypal.servicos.EntregaPagamento.obter_conexao', mock.MagicMock())
    def test_deve_processar_resposta_se_sucesso_com_ack_falha_de_autenticacao(self):
        entregador = servicos.EntregaPagamento(1234)
        entregador.resposta = mock.MagicMock(conteudo={'ack': 'failure', 'l_shortmessage0': 'authentication/authorization failed'}, status_code=401, sucesso=True, erro_servidor=False, timeout=False, nao_autenticado=False, nao_autorizado=False)
        entregador.processa_dados_pagamento()
        entregador.resultado.should.be.equal({'mensagem': u'Autenticação da loja com o PayPal Falhou. Contate o SAC da loja.', 'status_code': 401, 'pago': False, 'fatal': True})

    @mock.patch('pagador_paypal.servicos.EntregaPagamento.obter_conexao', mock.MagicMock())
    def test_deve_processar_resposta_se_sucesso_com_ack_falha_erro_qq(self):
        entregador = servicos.EntregaPagamento(1234)
        entregador.resposta = mock.MagicMock(conteudo={'ack': 'failure', 'l_shortmessage0': 'outra-coisa', 'l_longmessage0': 'message-zas'}, status_code=401, sucesso=True, erro_servidor=False, timeout=False, nao_autenticado=False, nao_autorizado=False)
        entregador.processa_dados_pagamento()
        entregador.resultado.should.be.equal({'mensagem': u'O PayPal retornou a seguinte mensagem de erro: message-zas', 'status_code': 401, 'pago': False, 'fatal': False})

    @mock.patch('pagador_paypal.servicos.EntregaPagamento.obter_conexao', mock.MagicMock())
    def test_deve_processar_resposta_nao_autorizado(self):
        entregador = servicos.EntregaPagamento(1234)
        entregador.resposta = mock.MagicMock(conteudo={}, status_code=400, sucesso=False, erro_servidor=False, timeout=False, nao_autenticado=False, nao_autorizado=True)
        entregador.processa_dados_pagamento()
        entregador.resultado.should.be.equal({'mensagem': u'Autenticação da loja com o PayPal Falhou. Contate o SAC da loja.', 'status_code': 400, 'pago': False, 'fatal': False})

    @mock.patch('pagador_paypal.servicos.EntregaPagamento.obter_conexao', mock.MagicMock())
    def test_deve_disparar_erro_se_resposta_vier_com_status_nao_conhecido(self):
        entregador = servicos.EntregaPagamento(1234)
        entregador.pedido = mock.MagicMock(numero=123)
        entregador.malote = mock.MagicMock()
        entregador.malote.to_dict.return_value = 'malote'
        entregador.resposta = mock.MagicMock(conteudo={'erro': 'zas'}, status_code=666, sucesso=False, erro_servidor=False, timeout=False, nao_autenticado=False, nao_autorizado=False)
        entregador.processa_dados_pagamento.when.called_with().should.throw(entregador.EnvioNaoRealizado)


class PayPalRegistraResultado(unittest.TestCase):

    @mock.patch('pagador_paypal.servicos.RegistraResultado.obter_conexao', mock.MagicMock())
    def test_deve_dizer_que_faz_http(self):
        registrador = servicos.RegistraResultado(1234, dados={})
        registrador.faz_http.should.be.truthy

    @mock.patch('pagador_paypal.servicos.RegistraResultado.obter_conexao', mock.MagicMock())
    def test_deve_definir_resposta(self):
        registrador = servicos.RegistraResultado(1234, dados={})
        registrador.resposta.should.be.none

    @mock.patch('pagador_paypal.servicos.RegistraResultado.obter_conexao', mock.MagicMock())
    def test_deve_definir_url_com_sandbox(self):
        registrador = servicos.RegistraResultado(1234, dados={})
        registrador.url.should.be.equal('https://api-3t.sandbox.paypal.com/nvp')

    @mock.patch('pagador_paypal.servicos.RegistraResultado.obter_conexao', mock.MagicMock())
    @mock.patch('pagador_paypal.servicos.RegistraResultado.sandbox', '')
    def test_deve_definir_url_sem_sandbox(self):
        registrador = servicos.RegistraResultado(1234, dados={})
        registrador.url.should.be.equal('https://api-3t.paypal.com/nvp')

    @mock.patch('pagador_paypal.servicos.RegistraResultado.obter_conexao')
    def test_deve_montar_conexao(self, obter_mock):
        obter_mock.return_value = 'conexao'
        registrador = servicos.RegistraResultado(1234, dados={})
        registrador.conexao.should.be.equal('conexao')
        obter_mock.assert_called_with(formato_envio='text/html', formato_resposta='text/html')

    @mock.patch('pagador_paypal.servicos.RegistraResultado.obter_conexao', mock.MagicMock())
    @mock.patch('pagador_paypal.servicos.Credenciador')
    def test_deve_definir_credenciais(self, credenciador_mock):
        registrador = servicos.RegistraResultado(1234, dados={})
        credenciador_mock.return_value = 'credenciador'
        registrador.configuracao = 'configuracao'
        registrador.define_credenciais()
        registrador.conexao.credenciador.should.be.equal('credenciador')
        credenciador_mock.assert_called_with(configuracao='configuracao')

    def test_deve_ter_redirect_para(self):
        registrador = servicos.RegistraResultado(1234, dados={'next_url': 'url-next'})
        registrador.redirect_para.should.be.equal('url-next')

    @mock.patch('pagador_paypal.servicos.RegistraResultado.obter_conexao', mock.MagicMock())
    def test_deve_montar_dados_de_pagamento_qdo_sucesso(self):
        registrador = servicos.RegistraResultado(1234, dados={'sucesso': 'true', 'referencia': 2222})
        registrador.resposta = mock.MagicMock(
            sucesso=True,
            conteudo={
                'ack': 'success',
                'paymentinfo_0_transactionid': 'transacao-id',
                'token': 'token-zas',
                'paymentinfo_0_amt': '233.40',
                'paymentinfo_0_paymentstatus': 'completed'
            }
        )
        registrador.monta_dados_pagamento()
        registrador.resultado.should.be.equal({'fatal': False, 'pago': True, 'resultado': 'sucesso'})
        registrador.dados_pagamento.should.be.equal({'identificador_id': 'TOKEN-ZAS', 'transacao_id': 'TRANSACAO-ID', 'valor_pago': 233.40})
        registrador.situacao_pedido.should.be.equal(4)

    @mock.patch('pagador_paypal.servicos.RegistraResultado.obter_conexao', mock.MagicMock())
    def test_deve_montar_dados_de_pagamento_sem_valor(self):
        registrador = servicos.RegistraResultado(1234, dados={'sucesso': 'true', 'referencia': 2222})
        registrador.resposta = mock.MagicMock(
            sucesso=True,
            conteudo={
                'ack': 'success',
                'paymentinfo_0_transactionid': 'transacao-id',
                'token': 'token-zas',
                'paymentinfo_0_paymentstatus': 'completed'
            }
        )
        registrador.monta_dados_pagamento()
        registrador.resultado.should.be.equal({'fatal': False, 'pago': True, 'resultado': 'sucesso'})
        registrador.dados_pagamento.should.be.equal({'identificador_id': 'TOKEN-ZAS', 'transacao_id': 'TRANSACAO-ID'})
        registrador.situacao_pedido.should.be.equal(4)

    @mock.patch('pagador_paypal.servicos.RegistraResultado.obter_conexao', mock.MagicMock())
    def test_deve_montar_dados_de_pagamento_sem_token(self):
        registrador = servicos.RegistraResultado(1234, dados={'sucesso': 'true', 'referencia': 2222})
        registrador.resposta = mock.MagicMock(
            sucesso=True,
            conteudo={
                'ack': 'success',
                'paymentinfo_0_transactionid': 'transacao-id',
                'paymentinfo_0_amt': '233.40',
                'paymentinfo_0_paymentstatus': 'completed'
            }
        )
        registrador.monta_dados_pagamento()
        registrador.resultado.should.be.equal({'fatal': False, 'pago': True, 'resultado': 'sucesso'})
        registrador.dados_pagamento.should.be.equal({'transacao_id': 'TRANSACAO-ID', 'valor_pago': 233.40})
        registrador.situacao_pedido.should.be.equal(4)

    @mock.patch('pagador_paypal.servicos.RegistraResultado.obter_conexao', mock.MagicMock())
    def test_deve_montar_dados_de_pagamento_sem_transacao(self):
        registrador = servicos.RegistraResultado(1234, dados={'sucesso': 'true', 'referencia': 2222})
        registrador.resposta = mock.MagicMock(
            sucesso=True,
            conteudo={
                'ack': 'success',
                'token': 'token-zas',
                'paymentinfo_0_amt': '233.40',
                'paymentinfo_0_paymentstatus': 'refunded'
            }
        )
        registrador.monta_dados_pagamento()
        registrador.resultado.should.be.equal({'fatal': False, 'pago': False, 'resultado': 'sucesso'})
        registrador.dados_pagamento.should.be.equal({'identificador_id': 'TOKEN-ZAS', 'valor_pago': 233.40})
        registrador.situacao_pedido.should.be.equal(7)

    @mock.patch('pagador_paypal.servicos.RegistraResultado.obter_conexao', mock.MagicMock())
    def test_deve_montar_dados_de_pagamento_com_falha(self):
        registrador = servicos.RegistraResultado(1234, dados={'sucesso': 'true', 'referencia': 2222})
        registrador.resposta = mock.MagicMock(
            sucesso=True,
            conteudo={
                'ack': 'failure',
            }
        )
        registrador.monta_dados_pagamento()
        registrador.resultado.should.be.equal({'fatal': False, 'pago': False, 'resultado': 'pendente'})
        registrador.dados_pagamento.should.be.equal({})
        registrador.situacao_pedido.should.be.none

    @mock.patch('pagador_paypal.servicos.RegistraResultado.obter_conexao', mock.MagicMock())
    def test_deve_montar_dados_de_pagamento_qdo_cancelado(self):
        registrador = servicos.RegistraResultado(1234, dados={'sucesso': 'false', 'referencia': 2222})
        registrador.resposta = mock.MagicMock(
            sucesso=False,
            conteudo={}
        )
        registrador.monta_dados_pagamento()
        registrador.resultado.should.be.equal({'fatal': False, 'pago': False, 'resultado': 'cancelado'})
        registrador.dados_pagamento.should.be.equal({})
        registrador.situacao_pedido.should.be.none

    @mock.patch('pagador_paypal.servicos.RegistraResultado.obter_conexao', mock.MagicMock())
    @mock.patch('pagador_paypal.servicos.RegistraResultado._gera_dados_envio')
    def test_nao_deve_obter_informacaoes_de_pagamento_qdo_cancelado(self, gera_mock):
        registrador = servicos.RegistraResultado(1234, dados={'sucesso': 'false', 'referencia': 2222})
        registrador.obtem_informacoes_pagamento()
        gera_mock.called.should.be.falsy

    @mock.patch('pagador_paypal.servicos.RegistraResultado.obter_conexao')
    @mock.patch('pagador_paypal.servicos.RegistraResultado._gera_dados_envio')
    def test_deve_obter_informacaoes_de_pagamento_qdo_sucesso(self, gera_mock, conexao_mock):
        gera_mock.return_value = 'dados_envio'
        conexao_mock.return_value.get.return_value = 'resultado-get'
        registrador = servicos.RegistraResultado(1234, dados={'sucesso': 'true', 'referencia': 2222})
        registrador.obtem_informacoes_pagamento()
        registrador.resposta.should.be.equal('resultado-get')
        registrador.dados_enviados = 'dados_envio'

    @mock.patch('pagador_paypal.servicos.RegistraResultado.obter_conexao')
    @mock.patch('pagador_paypal.servicos.RegistraResultado._gera_dados_envio')
    def test_deve_obter_informacaoes_de_pagamento_chamando_metodos(self, gera_mock, conexao_mock):
        gera_mock.return_value = 'dados_envio'
        conexao_mock.return_value.get.return_value = 'resultado-get'
        registrador = servicos.RegistraResultado(1234, dados={'sucesso': 'true', 'referencia': 2222})
        registrador.obtem_informacoes_pagamento()
        gera_mock.called.should.be.truthy
        conexao_mock.return_value.get.assert_called_with('https://api-3t.sandbox.paypal.com/nvp', dados='dados_envio')

    @mock.patch('pagador_paypal.servicos.RegistraResultado.obter_conexao', mock.MagicMock())
    @mock.patch('pagador_paypal.servicos.RegistraResultado.cria_entidade_extensao')
    @mock.patch('pagador_paypal.servicos.RegistraResultado.cria_entidade_pagador')
    def test_deve_gerar_dados_envio(self, pagador_mock, extensao_mock):
        registrador = servicos.RegistraResultado(1234, dados={'sucesso': 'true', 'referencia': 2222})
        pagador_mock.side_effect = ['pedido', mock.MagicMock()]
        malote_mock = mock.MagicMock()
        malote_mock.to_dict.return_value = 'dados-gerados'
        extensao_mock.return_value = malote_mock
        registrador.obtem_informacoes_pagamento()
        registrador.dados_enviados.should.be.equal('dados-gerados')

    @mock.patch('pagador_paypal.servicos.RegistraResultado.obter_conexao', mock.MagicMock())
    @mock.patch('pagador_paypal.servicos.RegistraResultado.cria_entidade_extensao')
    @mock.patch('pagador_paypal.servicos.RegistraResultado.cria_entidade_pagador')
    def test_deve_gerar_dados_envio_criando_entidades(self, pagador_mock, extensao_mock):
        registrador = servicos.RegistraResultado(1234, dados={'sucesso': 'true', 'referencia': 2222})
        registrador.configuracao = 'configuracao'
        parametros_mock = mock.MagicMock()
        parametros_mock.return_value.obter_para.return_value = 'parametros-extensao'
        pagador_mock.side_effect = ['pedido', parametros_mock]
        malote_mock = mock.MagicMock()
        extensao_mock.return_value = malote_mock
        registrador.obtem_informacoes_pagamento()
        pagador_mock.call_args_list[0].should.be.equal(mock.call('Pedido', numero=2222, loja_id=1234))
        extensao_mock.assert_called_with('Malote', configuracao='configuracao', metodo='DoExpressCheckoutPayment')
        pagador_mock.call_args_list[1].should.be.equal(mock.call('ParametrosDeContrato', loja_id=1234))

    @mock.patch('pagador_paypal.servicos.RegistraResultado.obter_conexao', mock.MagicMock())
    @mock.patch('pagador_paypal.servicos.RegistraResultado.cria_entidade_extensao')
    @mock.patch('pagador_paypal.servicos.RegistraResultado.cria_entidade_pagador')
    def test_deve_gerar_dados_envio_chamando_metodos(self, pagador_mock, extensao_mock):
        registrador = servicos.RegistraResultado(1234, dados={'sucesso': 'true', 'referencia': 2222})
        registrador.configuracao = 'configuracao'
        registrador.extensao = 'extensao_teste'
        parametros_mock = mock.MagicMock()
        parametros_mock.obter_para.return_value = 'parametros-extensao'
        pagador_mock.side_effect = ['pedido', parametros_mock]
        malote_mock = mock.MagicMock()
        extensao_mock.return_value = malote_mock
        registrador.obtem_informacoes_pagamento()
        parametros_mock.obter_para.assert_called_with('extensao_teste')
        malote_mock.monta_conteudo.assert_called_with(parametros_contrato='parametros-extensao', dados={'referencia': 2222, 'sucesso': 'true'}, pedido='pedido')


class PayPalSituacoesPagamento(unittest.TestCase):
    def test_deve_retornar_em_analise_para_pending(self):
        servicos.SituacoesDePagamento.do_tipo('pending').should.be.equal(servicos.servicos.SituacaoPedido.SITUACAO_PAGTO_EM_ANALISE)

    def test_deve_retornar_pago_para_completed(self):
        servicos.SituacoesDePagamento.do_tipo('completed').should.be.equal(servicos.servicos.SituacaoPedido.SITUACAO_PEDIDO_PAGO)

    def test_deve_retornar_devolvido_para_refunded(self):
        servicos.SituacoesDePagamento.do_tipo('refunded').should.be.equal(servicos.servicos.SituacaoPedido.SITUACAO_PAGTO_DEVOLVIDO)

    def test_deve_retornar_none_para_desconhecido(self):
        servicos.SituacoesDePagamento.do_tipo('zas').should.be.none


class PayPalRegistraNotificacao(unittest.TestCase):
    def test_deve_ter_loja_e_dados(self):
        registrador = servicos.RegistraNotificacao(1234, dados={'invoice': 2222})
        registrador.loja_id.should.be.equal(1234)
        registrador.dados.should.be.equal({'invoice': 2222})

    def test_deve_montar_dados_de_pagamento_com_referencia(self):
        registrador = servicos.RegistraNotificacao(1234, dados={'referencia': 2222})
        registrador.monta_dados_pagamento()
        registrador.pedido_numero.should.be.equal(2222)
        registrador.situacao_pedido.should.be.none

    def test_deve_montar_dados_de_pagamento_com_invoice(self):
        registrador = servicos.RegistraNotificacao(1234, dados={'invoice': 2222})
        registrador.monta_dados_pagamento()
        registrador.pedido_numero.should.be.equal(2222)
        registrador.resultado.should.be.equal({'resultado': 'OK'})

    def test_deve_montar_dados_de_pagamento_com_situacao_pedido(self):
        registrador = servicos.RegistraNotificacao(1234, dados={'invoice': 2222, 'payment_status': 'pending'})
        registrador.monta_dados_pagamento()
        registrador.situacao_pedido.should.be.equal(3)