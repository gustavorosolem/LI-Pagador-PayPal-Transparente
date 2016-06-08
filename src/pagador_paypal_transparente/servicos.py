# -*- coding: utf-8 -*-
from urllib import urlencode

from li_common.comunicacao import requisicao

from pagador import servicos


class Credenciador(servicos.Credenciador):
    def __init__(self, tipo=None, configuracao=None):
        super(Credenciador, self).__init__(tipo, configuracao)
        self.tipo = self.TipoAutenticacao.form_urlencode
        self.usuario = getattr(configuracao, 'usuario', '')
        self.chave = 'SUBJECT'

    def obter_credenciais(self):
        return self.usuario


class Ack(object):
    def __init__(self, ack_code):
        ack = ack_code.lower()
        self.sucesso = ack in ('success', 'successwithwarning')
        self.falha = ack == 'failure'


class EntregaPagamento(servicos.EntregaPagamento):
    def __init__(self, loja_id, plano_indice=1, dados=None):
        super(EntregaPagamento, self).__init__(loja_id, plano_indice, dados=dados)
        self.tem_malote = True
        self.faz_http = True
        self.conexao = self.obter_conexao(formato_envio=requisicao.Formato.form_urlencode, formato_resposta=requisicao.Formato.form_urlencode)
        self.resposta = None
        self.url = 'https://api-3t.{}paypal.com/nvp'.format(self.sandbox)

    def define_credenciais(self):
        self.conexao.credenciador = Credenciador(configuracao=self.configuracao)

    def envia_pagamento(self, tentativa=1):
        self.dados_enviados = self.malote.to_dict()
        self.resposta = self.conexao.post(self.url, self.dados_enviados)

    def processa_dados_pagamento(self):
        self.resultado = self._processa_resposta()

    def _processa_resposta(self):
        status_code = self.resposta.status_code
        if self.resposta.erro_servidor:
            return {'mensagem': u'O servidor do PayPal está indisponível nesse momento.', 'status_code': status_code, 'fatal': False, 'pago': False}
        if self.resposta.timeout:
            return {'mensagem': u'O servidor do PayPal não respondeu em tempo útil.', 'status_code': status_code, 'fatal': False, 'pago': False}
        if self.resposta.nao_autenticado or self.resposta.nao_autorizado:
            return {'mensagem': u'Autenticação da loja com o PayPal Falhou. Contate o SAC da loja.', 'status_code': status_code, 'fatal': False, 'pago': False}
        if self.resposta.sucesso and Ack(self.resposta.conteudo.get('ack', '')).sucesso:
            token = self.resposta.conteudo['token'].upper()
            url = 'https://www.{}paypal.com/cgi-bin/webscr?cmd=_express-checkout&token={}'.format(self.sandbox, token)
            return {'url': url, 'fatal': False, 'pago': False}
        if self.resposta.sucesso and Ack(self.resposta.conteudo.get('ack', '')).falha:
            mensagem_erro = self.resposta.conteudo.get('l_shortmessage0', '')
            if mensagem_erro == 'authentication/authorization failed':
                return {'mensagem': u'Autenticação da loja com o PayPal Falhou. Contate o SAC da loja.', 'status_code': 401, 'fatal': True, 'pago': False}
            mensagem_longa = self.resposta.conteudo.get('l_longmessage0', '')
            return {'mensagem': u'O PayPal retornou a seguinte mensagem de erro: {}'.format(mensagem_longa), 'status_code': status_code, 'fatal': False, 'pago': False}
        raise self.EnvioNaoRealizado(u'Ocorreram erros no envio dos dados para o PayPal', self.loja_id, self.pedido.numero, dados_envio=self.malote.to_dict(), erros=urlencode(self.resposta.conteudo))


class SituacoesDePagamento(servicos.SituacoesDePagamento):
    DE_PARA = {
        'pending': servicos.SituacaoPedido.SITUACAO_PAGTO_EM_ANALISE,
        'completed': servicos.SituacaoPedido.SITUACAO_PEDIDO_PAGO,
        'refunded': servicos.SituacaoPedido.SITUACAO_PAGTO_DEVOLVIDO,
    }


class RegistraResultado(servicos.RegistraResultado):
    def __init__(self, loja_id, dados=None):
        super(RegistraResultado, self).__init__(loja_id, dados)
        self.conexao = self.obter_conexao(formato_envio=requisicao.Formato.querystring, formato_resposta=requisicao.Formato.querystring)
        self.resposta = None
        self.redirect_para = dados.get('next_url', None)
        self.faz_http = True
        self.url = 'https://api-3t.{}paypal.com/nvp'.format(self.sandbox)

    def define_credenciais(self):
        self.conexao.credenciador = Credenciador(configuracao=self.configuracao)

    def monta_dados_pagamento(self):
        if self.deve_obter_informacoes_paypal and self.resposta.sucesso:
            ack = Ack(self.resposta.conteudo.get('ack', ''))
            if ack.sucesso:
                self.pedido_numero = self.dados['referencia']
                retorno_paypal = self.resposta.conteudo
                if 'paymentinfo_0_transactionid' in retorno_paypal:
                    self.dados_pagamento['transacao_id'] = retorno_paypal['paymentinfo_0_transactionid'].upper()
                if 'token' in retorno_paypal:
                    self.dados_pagamento['identificador_id'] = retorno_paypal['token'].upper()
                if 'paymentinfo_0_amt' in retorno_paypal:
                    self.dados_pagamento['valor_pago'] = self.formatador.formata_decimal(self.formatador.converte_para_decimal(retorno_paypal['paymentinfo_0_amt']), como_float=True)
                self.situacao_pedido = SituacoesDePagamento.do_tipo(retorno_paypal['paymentinfo_0_paymentstatus'])
                self.resultado = {'resultado': 'sucesso', 'fatal': False, 'pago': self.situacao_pedido in [servicos.SituacaoPedido.SITUACAO_PEDIDO_PAGO, servicos.SituacaoPedido.SITUACAO_PAGTO_EM_ANALISE]}
            if ack.falha:
                self.resultado = {'resultado': 'pendente', 'fatal': False, 'pago': False}
        if self.dados.get('sucesso', 'true') == 'false':
            self.resultado = {'resultado': 'cancelado', 'fatal': False, 'pago': False}

    def obtem_informacoes_pagamento(self):
        if self.deve_obter_informacoes_paypal:
            self.dados_enviados = self._gera_dados_envio()
            self.resposta = self.conexao.get(self.url, dados=self.dados_enviados)

    def _gera_dados_envio(self):
        pedido_numero = int(self.dados.get('referencia', '-1'))
        pedido = self.cria_entidade_pagador('Pedido', numero=pedido_numero, loja_id=self.loja_id)
        malote = self.cria_entidade_extensao('Malote', configuracao=self.configuracao, metodo='DoExpressCheckoutPayment')
        parametros = self.cria_entidade_pagador('ParametrosDeContrato', loja_id=self.loja_id).obter_para(self.extensao)
        malote.monta_conteudo(pedido=pedido, parametros_contrato=parametros, dados=self.dados)
        return malote.to_dict()

    @property
    def deve_obter_informacoes_paypal(self):
        return self.dados.get('sucesso', '') == 'true'


class RegistraNotificacao(servicos.RegistraResultado):
    def __init__(self, loja_id, dados=None):
        super(RegistraNotificacao, self).__init__(loja_id, dados)

    def monta_dados_pagamento(self):
        self.pedido_numero = self.dados.get('referencia', None) or self.dados['invoice']
        if 'payment_status' in self.dados:
            self.situacao_pedido = SituacoesDePagamento.do_tipo(self.dados['payment_status'])
        self.resultado = {'resultado': 'OK'}
