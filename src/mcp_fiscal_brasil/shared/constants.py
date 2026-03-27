"""Constantes fiscais brasileiras: UFs, CFOP, CST, NCM e codigos SEFAZ."""

# Codigos de UF (IBGE)
UF_CODES: dict[str, int] = {
    "AC": 12,
    "AL": 27,
    "AP": 16,
    "AM": 13,
    "BA": 29,
    "CE": 23,
    "DF": 53,
    "ES": 32,
    "GO": 52,
    "MA": 21,
    "MT": 51,
    "MS": 50,
    "MG": 31,
    "PA": 15,
    "PB": 25,
    "PR": 41,
    "PE": 26,
    "PI": 22,
    "RJ": 33,
    "RN": 24,
    "RS": 43,
    "RO": 11,
    "RR": 14,
    "SC": 42,
    "SP": 35,
    "SE": 28,
    "TO": 17,
}

# Siglas de UF por codigo IBGE
CODIGO_UF: dict[int, str] = {v: k for k, v in UF_CODES.items()}

# Nomes completos das UFs
NOME_UF: dict[str, str] = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapa",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceara",
    "DF": "Distrito Federal",
    "ES": "Espirito Santo",
    "GO": "Goias",
    "MA": "Maranhao",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Para",
    "PB": "Paraiba",
    "PR": "Parana",
    "PE": "Pernambuco",
    "PI": "Piaui",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondonia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "Sao Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}

# Status de autorizacao NFe retornados pela SEFAZ
STATUS_SEFAZ: dict[int, str] = {
    100: "Autorizado o uso da NF-e",
    101: "Cancelamento de NF-e homologado",
    102: "Inutilizacao de numero homologado",
    110: "Uso Denegado",
    135: "Evento registrado e vinculado a NF-e",
    136: "Evento registrado, mas nao vinculado a NF-e",
    150: "Autorizado o uso da NF-e, autorização fora de prazo",
    151: "NF-e nao localizada",
    155: "Cancelamento homologado fora de prazo",
    204: "Duplicidade de NF-e com divergencia",
    205: "NF-e esta denegada na base de dados da SEFAZ",
    207: "CNPJ do emitente invalido",
    208: "CNPJ do destinatario invalido",
    211: "IE do emitente invalida",
    226: "Codigo Municipal do Emitente diverge do cadastrado",
    235: "Chave de Acesso invalida",
    302: "CNPJ invalido",
    303: "CPF do destinatario invalido",
    305: "Rejeicao: NF-e ja numerada",
    401: "Rejeicao: Certificado transmissor invalido",
    402: "Rejeicao: Certificado transmissor fora de validade",
    403: "Rejeicao: Certificado transmissor revogado",
    501: "Rejeicao: Prazo de Cancelamento Superior ao Permitido",
    539: "Rejeicao: CSOSN invalido",
    591: "Rejeicao: Informar a chave de acesso da NF-e referenciada",
    999: "Rejeicao: Erro nao catalogado",
}

# Modelos de documentos fiscais
MODELOS_DOCUMENTO: dict[str, str] = {
    "01": "NF (Nota Fiscal modelo 1/1A)",
    "02": "NF de Venda a Consumidor",
    "04": "NF de Produtor Rural",
    "06": "Nota Fiscal/Conta de Energia Eletrica",
    "07": "Nota Fiscal de Servico de Transporte",
    "08": "CF-e (Cupom Fiscal Eletronico)",
    "10": "Nota Fiscal de Servico de Comunicacao",
    "11": "Nota Fiscal de Servico de Telecomunicacao",
    "13": "Bilhete de Passagem Rodoviario",
    "14": "Bilhete de Passagem Aquaviario",
    "15": "Bilhete de Passagem e Nota de Bagagem",
    "17": "Despacho de Transporte",
    "21": "Bilhete de Passagem Aereo",
    "55": "NF-e (Nota Fiscal Eletronica)",
    "57": "CT-e (Conhecimento de Transporte Eletronico)",
    "59": "CF-e-SAT (Cupom Fiscal Eletronico - SAT)",
    "65": "NFC-e (Nota Fiscal de Consumidor Eletronica)",
}

# CFOPs mais comuns (amostra)
CFOP_DESCRICAO: dict[str, str] = {
    "1101": "Compra para industrializacao dentro do estado",
    "1102": "Compra para comercializacao dentro do estado",
    "1202": "Devolucao de venda de producao propria dentro do estado",
    "1556": "Compra de material para uso ou consumo dentro do estado",
    "2101": "Compra para industrializacao de outro estado",
    "2102": "Compra para comercializacao de outro estado",
    "3101": "Compra para industrializacao do exterior",
    "3102": "Compra para comercializacao do exterior",
    "5101": "Venda de producao do estabelecimento dentro do estado",
    "5102": "Venda de mercadoria adquirida ou recebida de terceiros dentro do estado",
    "5103": "Venda de producao do estabelecimento em operacao com produto diferente",
    "5110": "Venda de producao do estabelecimento, destinada a exportacao",
    "5202": "Devolucao de compra para comercializacao dentro do estado",
    "5401": "Venda de producao do estabelecimento em operacao com ST",
    "5403": "Venda de mercadoria adquirida com ST dentro do estado",
    "5405": "Venda de mercadoria adquirida com ST para nao contribuinte",
    "5501": "Remessa para industrializacao por encomenda",
    "5556": "Venda de material de uso ou consumo dentro do estado",
    "5910": "Remessa em bonificacao, doacao ou brinde",
    "5911": "Remessa de amostra gratis",
    "6101": "Venda de producao do estabelecimento para outro estado",
    "6102": "Venda de mercadoria adquirida ou recebida de terceiros para outro estado",
    "6108": "Venda de producao do estabelecimento destinada ao exterior",
    "6401": "Venda de producao com ST para outro estado",
    "7101": "Exportacao de producao propria",
    "7102": "Exportacao de mercadoria adquirida de terceiros",
}

# CST do ICMS (Tabela A - origem da mercadoria)
CST_ICMS_ORIGEM: dict[str, str] = {
    "0": "Nacional",
    "1": "Estrangeira - Importacao direta",
    "2": "Estrangeira - Adquirida no mercado interno",
    "3": "Nacional com mais de 40% de conteudo de importacao",
    "4": "Nacional com processo produtivo basico",
    "5": "Nacional com menos de 40% de conteudo de importacao",
    "6": "Estrangeira - Importacao direta sem similar nacional",
    "7": "Estrangeira - Adquirida no mercado interno sem similar nacional",
    "8": "Nacional com mais de 70% de conteudo de importacao",
}

# Situacoes tributarias do ICMS (Tabela B - tributacao)
CST_ICMS_TRIBUTACAO: dict[str, str] = {
    "00": "Tributada integralmente",
    "10": "Tributada e com cobranca do ICMS por ST",
    "20": "Com reducao de BC",
    "30": "Isenta ou nao tributada e com cobranca do ICMS por ST",
    "40": "Isenta",
    "41": "Nao tributada",
    "50": "Suspensao",
    "51": "Diferimento",
    "60": "ICMS cobrado anteriormente por ST",
    "70": "Com reducao da BC e cobranca do ICMS por ST",
    "90": "Outras",
}

# CSOSN - Codigo de Situacao da Operacao no Simples Nacional
CSOSN: dict[str, str] = {
    "101": "Tributada pelo Simples Nacional com permissao de credito",
    "102": "Tributada pelo Simples Nacional sem permissao de credito",
    "103": "Isencao do ICMS no Simples Nacional para faixa de receita bruta",
    "201": "Tributada pelo Simples Nacional com permissao de credito e com cobranca do ICMS por ST",
    "202": "Tributada pelo Simples Nacional sem permissao de credito e com cobranca do ICMS por ST",
    "203": "Isencao do ICMS no Simples Nacional para faixa de receita bruta e com cobranca do ICMS por ST",
    "300": "Imune",
    "400": "Nao tributada pelo Simples Nacional",
    "500": "ICMS cobrado anteriormente por ST ou por antecipacao",
    "900": "Outros",
}

# Natureza juridica das empresas (amostra dos mais comuns)
NATUREZA_JURIDICA: dict[str, str] = {
    "1015": "Orgao Publico do Poder Executivo Federal",
    "1023": "Orgao Publico do Poder Executivo Estadual ou do Distrito Federal",
    "1031": "Orgao Publico do Poder Executivo Municipal",
    "2011": "Empresa Publica",
    "2038": "Sociedade de Economia Mista",
    "2046": "Sociedade Anonima Aberta",
    "2054": "Sociedade Anonima Fechada",
    "2062": "Sociedade Empresaria Limitada",
    "2070": "Sociedade Empresaria em Nome Coletivo",
    "2089": "Sociedade Empresaria em Comandita Simples",
    "2097": "Sociedade Empresaria em Comandita por Acoes",
    "2127": "Sociedade em Conta de Participacao",
    "2135": "Empresario Individual",
    "2143": "Cooperativa",
    "2216": "Empresa Individual de Responsabilidade Limitada (EIRELI)",
    "2232": "Sociedade Unipessoal de Advocacia",
    "2305": "Liquidacao Extrajudicial",
    "3034": "Organizacao Social (OS)",
    "3069": "Fundacao Privada",
    "3077": "Servico Notarial e Registral (Cartorio)",
    "3085": "Orgao de Direcao Nacional de Partido Politico",
    "3204": "Entidade Sindical",
    "3999": "Associacao Privada",
    "4014": "Empresa Domiciliada no Exterior",
    "4081": "Representacao Diplomatica Estrangeira",
    "4120": "Servico Autonomo",
    "5010": "Orgao de Representacao Municipal",
    "5053": "MEI - Microempreendedor Individual",
    "5070": "Producao Rural (Pessoa Fisica)",
}

# Porte da empresa
PORTE_EMPRESA: dict[str, str] = {
    "00": "Nao informado",
    "01": "Micro Empresa",
    "03": "Empresa de Pequeno Porte",
    "05": "Demais",
}

# Situacao cadastral na Receita Federal
SITUACAO_CNPJ: dict[str, str] = {
    "01": "Nula",
    "02": "Ativa",
    "03": "Suspensa",
    "04": "Inapta",
    "08": "Baixada",
}
