"""
Cliente NFSe.

NFSe não tem padrao nacional unico - cada municipio implementa seu próprio
webservice (ABRASF, Betha, ISS.net, Curitiba, etc.). Este modulo fornece
uma interface unificada que abstrai essas diferencas.
"""
# Implementacao futura: detectar padrao pelo municipio e rotear para o webservice correto.
# Municipios que adotam padrao ABRASF: São Paulo, Rio de Janeiro, Belo Horizonte, etc.
# Referencia: https://www.abrasf.org.br/
