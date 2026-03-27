"""
Cliente para certidoes negativas.

As certidoes negativas da Receita Federal e PGFN requerem resolucao de CAPTCHA
e nao possuem API publica oficial. Este modulo fornece orientacoes de acesso.
"""
# A Receita Federal disponibiliza certidoes via:
# - Portal e-CAC: https://cav.receita.fazenda.gov.br/autenticacao/login
# - Consulta publica (com CAPTCHA): https://solucoes.receita.fazenda.gov.br/Servicos/certidaointernet/PJ/Emitir
# Para automacao em producao, use servicos como Serasa Experian ou Boa Vista SCPC.
