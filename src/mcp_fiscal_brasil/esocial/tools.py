"""Ferramentas MCP para eSocial."""

from lxml import etree

from ..shared.xml_utils import parse_xml
from .schemas import EventoESocial, ValidacaoESocialResponse

# Catalogo completo dos eventos eSocial (45+ eventos - S-1.0 e posteriores)
EVENTOS_ESOCIAL: dict[str, EventoESocial] = {
    # Eventos de Tabelas (11 eventos)
    "S-1000": EventoESocial(
        codigo="S-1000",
        nome="Informacoes do Empregador/Contribuinte/Orgao Publico",
        grupo="Tabelas",
        descricao="Cadastro do empregador no eSocial. Deve ser o primeiro evento enviado.",
    ),
    "S-1005": EventoESocial(
        codigo="S-1005",
        nome="Tabela de Estabelecimentos, Obras ou Unidades de Orgao Publico",
        grupo="Tabelas",
        descricao="Cadastro de estabelecimentos, CNPJ/CEI/CAEPF.",
    ),
    "S-1010": EventoESocial(
        codigo="S-1010",
        nome="Tabela de Rubricas",
        grupo="Tabelas",
        descricao="Definicao das verbas/rubricas da folha de pagamento.",
    ),
    "S-1020": EventoESocial(
        codigo="S-1020",
        nome="Tabela de Lotacoes Tributarias",
        grupo="Tabelas",
        descricao="Definicao das lotacoes tributarias para apuracao de contribuicoes.",
    ),
    "S-1030": EventoESocial(
        codigo="S-1030",
        nome="Tabela de Cargos/Empregos Publicos",
        grupo="Tabelas",
        descricao="Cadastro de cargos e empregos publicos da organizacao.",
    ),
    "S-1035": EventoESocial(
        codigo="S-1035",
        nome="Tabela de Cargas Horarias/Horarios de Trabalho",
        grupo="Tabelas",
        descricao="Definicao de jornadas, horarios e turnos de trabalho.",
    ),
    "S-1040": EventoESocial(
        codigo="S-1040",
        nome="Tabela de Funcoes/Cargos em Comissao",
        grupo="Tabelas",
        descricao="Cadastro de funcoes e cargos em comissao.",
    ),
    "S-1050": EventoESocial(
        codigo="S-1050",
        nome="Tabela de Horarios/Turnos de Trabalho",
        grupo="Tabelas",
        descricao="Definicao de horarios e turnos da organizacao.",
    ),
    "S-1060": EventoESocial(
        codigo="S-1060",
        nome="Tabela de Ambientes de Trabalho",
        grupo="Tabelas",
        descricao="Cadastro de ambientes e locais de trabalho.",
    ),
    "S-1070": EventoESocial(
        codigo="S-1070",
        nome="Tabela de Processos Administrativos/Judiciais",
        grupo="Tabelas",
        descricao="Registro de processos judiciais e administrativos.",
    ),
    "S-1080": EventoESocial(
        codigo="S-1080",
        nome="Tabela de Operadores Portuarios",
        grupo="Tabelas",
        descricao="Cadastro de operadores portuarios e trabalho portuario.",
    ),
    # Eventos Nao Periodicos - Cadastramento de Trabalhador (5 eventos)
    "S-2190": EventoESocial(
        codigo="S-2190",
        nome="Registro Preliminar de Trabalhador",
        grupo="Nao Periodicos",
        descricao="Registro preliminar do trabalhador antes da admissao.",
    ),
    "S-2200": EventoESocial(
        codigo="S-2200",
        nome="Cadastramento Inicial do Vinculo e Admissao/Ingresso de Trabalhador",
        grupo="Nao Periodicos",
        descricao="Admissao de empregado ou ingresso de trabalhador.",
    ),
    "S-2205": EventoESocial(
        codigo="S-2205",
        nome="Alteracao de Dados Cadastrais do Trabalhador",
        grupo="Nao Periodicos",
        descricao="Alteracao de dados pessoais do trabalhador.",
    ),
    "S-2206": EventoESocial(
        codigo="S-2206",
        nome="Alteracao de Contrato de Trabalho",
        grupo="Nao Periodicos",
        descricao="Alteracao de cargo, salario, jornada de trabalho etc.",
    ),
    "S-2207": EventoESocial(
        codigo="S-2207",
        nome="Alteracao de Contrato - Fim de Obra",
        grupo="Nao Periodicos",
        descricao="Registro de fim de obra ou contrato com prazo determinado.",
    ),
    # Eventos Nao Periodicos - Saude e Seguranca do Trabalho (5 eventos)
    "S-2210": EventoESocial(
        codigo="S-2210",
        nome="Comunicacao de Acidente de Trabalho",
        grupo="Nao Periodicos",
        descricao="Registro de acidente de trabalho conforme Lei 8213/99.",
    ),
    "S-2220": EventoESocial(
        codigo="S-2220",
        nome="Monitoramento da Saude do Trabalhador",
        grupo="Nao Periodicos",
        descricao="Informacoes de exames ocupacionais e ASO (Atestado de Saude Ocupacional).",
    ),
    "S-2230": EventoESocial(
        codigo="S-2230",
        nome="Afastamento Temporario",
        grupo="Nao Periodicos",
        descricao="Registro de afastamento: ferias, licenca, atestado etc.",
    ),
    "S-2240": EventoESocial(
        codigo="S-2240",
        nome="Condicoes Ambientais do Trabalho - Agentes Nocivos",
        grupo="Nao Periodicos",
        descricao="Registro de ambientes com agentes nocivos e trabalho insalubre.",
    ),
    "S-2250": EventoESocial(
        codigo="S-2250",
        nome="Aviso Previo",
        grupo="Nao Periodicos",
        descricao="Comunicacao de aviso previo de desligamento do trabalhador.",
    ),
    # Eventos Nao Periodicos - Desligamento (3 eventos)
    "S-2260": EventoESocial(
        codigo="S-2260",
        nome="Convocacao para Trabalho Intermitente",
        grupo="Nao Periodicos",
        descricao="Registro de convocacao de trabalhador intermitente.",
    ),
    "S-2298": EventoESocial(
        codigo="S-2298",
        nome="Reintegracao/Outros Provimentos",
        grupo="Nao Periodicos",
        descricao="Registro de reintegracao ou outros provimentos trabalhistas.",
    ),
    "S-2299": EventoESocial(
        codigo="S-2299",
        nome="Desligamento",
        grupo="Nao Periodicos",
        descricao="Rescisao de contrato de trabalho. Prazo: 10 dias apos desligamento.",
    ),
    # Eventos Nao Periodicos - Beneficios (3 eventos)
    "S-2400": EventoESocial(
        codigo="S-2400",
        nome="Cadastro de Beneficios Previdenciarios - RPPS",
        grupo="Nao Periodicos",
        descricao="Concessao de beneficio previdenciario do RPPS.",
    ),
    "S-2405": EventoESocial(
        codigo="S-2405",
        nome="Alteracao de Beneficio - RPPS",
        grupo="Nao Periodicos",
        descricao="Alteracao de dados de beneficio previdenciario do RPPS.",
    ),
    "S-2410": EventoESocial(
        codigo="S-2410",
        nome="Termo de Cessacao de Beneficio - RPPS",
        grupo="Nao Periodicos",
        descricao="Cessacao de beneficio previdenciario do RPPS.",
    ),
    # Eventos Nao Periodicos - Processos e Competencias (3 eventos)
    "S-2500": EventoESocial(
        codigo="S-2500",
        nome="Processo Trabalhista",
        grupo="Nao Periodicos",
        descricao="Registro de reclamatoria trabalhista e valores devidos.",
    ),
    "S-2501": EventoESocial(
        codigo="S-2501",
        nome="Alteracao de Processo Trabalhista",
        grupo="Nao Periodicos",
        descricao="Alteracao de dados de processo trabalhista registrado.",
    ),
    # Eventos Periodicos - Folha de Pagamento (6 eventos)
    "S-1200": EventoESocial(
        codigo="S-1200",
        nome="Remuneracao de Trabalhador vinculado ao Regime Geral de Prev. Social",
        grupo="Periodicos",
        descricao="Folha de pagamento mensal - RGPS.",
    ),
    "S-1202": EventoESocial(
        codigo="S-1202",
        nome="Remuneracao de Servidor vinculado ao Regime Proprio de Prev. Social",
        grupo="Periodicos",
        descricao="Folha de pagamento mensal - RPPS.",
    ),
    "S-1204": EventoESocial(
        codigo="S-1204",
        nome="Informacoes Complementares de Contribuinte sem Movimentacao",
        grupo="Periodicos",
        descricao="Evento para contribuinte que nao teve movimentacao no periodo.",
    ),
    "S-1207": EventoESocial(
        codigo="S-1207",
        nome="Beneficios Previdenciarios - RPPS",
        grupo="Periodicos",
        descricao="Pagamento de beneficios do RPPS.",
    ),
    "S-1210": EventoESocial(
        codigo="S-1210",
        nome="Pagamentos de Rendimentos do Trabalho",
        grupo="Periodicos",
        descricao="Pagamentos a trabalhadores sem vinculo (autonomos, etc.).",
    ),
    "S-1212": EventoESocial(
        codigo="S-1212",
        nome="Remuneracao de Contribuinte Individual",
        grupo="Periodicos",
        descricao="Remuneracao de contribuinte individual (autonomo).",
    ),
    # Eventos Periodicos - Producao Rural e Avulsos (3 eventos)
    "S-1260": EventoESocial(
        codigo="S-1260",
        nome="Comercializacao da Producao Rural Pessoa Fisica",
        grupo="Periodicos",
        descricao="Producao rural comercializada pelo segurado especial.",
    ),
    "S-1270": EventoESocial(
        codigo="S-1270",
        nome="Contratacao de Trabalhadores Avulsos Nao Portuarios",
        grupo="Periodicos",
        descricao="Contratacao de trabalhador avulso nao portuario.",
    ),
    "S-1280": EventoESocial(
        codigo="S-1280",
        nome="Informacoes Complementares do Contribuinte",
        grupo="Periodicos",
        descricao="Informacoes adicionais necessarias para complementacao da folha.",
    ),
    # Eventos Periodicos - Totalizadores e Fechamento (3 eventos)
    "S-1295": EventoESocial(
        codigo="S-1295",
        nome="Solicitacao de Totalizador para Pagamento em Atraso",
        grupo="Periodicos",
        descricao="Solicita totalizador para recolhimento em atraso.",
    ),
    "S-1298": EventoESocial(
        codigo="S-1298",
        nome="Reabertura dos Eventos Periodicos",
        grupo="Periodicos",
        descricao="Reabre competencia fechada para correcoes.",
    ),
    "S-1299": EventoESocial(
        codigo="S-1299",
        nome="Fechamento dos Eventos Periodicos",
        grupo="Periodicos",
        descricao="Fecha a competencia e gera DCTFWeb/GFIP.",
    ),
    # Eventos de Exclusao (1 evento)
    "S-3000": EventoESocial(
        codigo="S-3000",
        nome="Exclusao de Eventos",
        grupo="Exclusao",
        descricao="Exclui um evento anteriormente enviado.",
    ),
    # Eventos Retorno do Governo - Totalizadores (7 eventos)
    "S-5001": EventoESocial(
        codigo="S-5001",
        nome="Informacoes das Contribuicoes Sociais por Trabalhador",
        grupo="Totalizadores",
        descricao="Resumo das contribuicoes sociais por trabalhador no periodo.",
    ),
    "S-5002": EventoESocial(
        codigo="S-5002",
        nome="Totalizacao da Remuneracao",
        grupo="Totalizadores",
        descricao="Totalizacao das remuneracoes da organizacao no periodo.",
    ),
    "S-5003": EventoESocial(
        codigo="S-5003",
        nome="Totalizacao de Contribuicoes",
        grupo="Totalizadores",
        descricao="Totalizacao de todas as contribuicoes devidas.",
    ),
    "S-5011": EventoESocial(
        codigo="S-5011",
        nome="Informacoes Consolidadas da Competencia - Contribuinte",
        grupo="Totalizadores",
        descricao="Consolidacao de informacoes do contribuinte na competencia.",
    ),
    "S-5012": EventoESocial(
        codigo="S-5012",
        nome="Informacoes Consolidadas da Competencia - Gestor de Pessoas Fisica",
        grupo="Totalizadores",
        descricao="Consolidacao de informacoes para gestor de pessoas fisicas.",
    ),
    "S-5013": EventoESocial(
        codigo="S-5013",
        nome="Informacoes Consolidadas da Competencia - Produtor Rural",
        grupo="Totalizadores",
        descricao="Consolidacao de informacoes para produtor rural.",
    ),
}


async def listar_eventos_esocial(grupo: str | None = None) -> list[EventoESocial]:
    """
    Lista os eventos do eSocial, opcionalmente filtrados por grupo.

    Args:
        grupo: Filtrar por grupo: 'Tabelas', 'Nao Periodicos', 'Periodicos', 'Exclusao'.
               Se None, retorna todos os eventos.

    Returns:
        Lista de eventos eSocial com codigo, nome, grupo e descricao.
    """
    eventos = list(EVENTOS_ESOCIAL.values())
    if grupo:
        grupo_lower = grupo.lower()
        eventos = [e for e in eventos if grupo_lower in e.grupo.lower()]
    return sorted(eventos, key=lambda e: e.codigo)


async def validar_evento_esocial(xml_conteudo: str) -> ValidacaoESocialResponse:
    """
    Realiza validacao basica de estrutura de um XML de evento eSocial.

    Verifica:
    - Presenca do elemento raiz correto
    - Codigo do evento
    - Versao do leiaute

    Nao valida schema XSD completo (exige bibliotecas adicionais).

    Args:
        xml_conteudo: Conteudo do XML do evento eSocial

    Returns:
        ValidacaoESocialResponse com resultado da validacao.
    """
    erros: list[str] = []
    avisos: list[str] = []
    evento_codigo = "Desconhecido"
    versao = None

    try:
        root = parse_xml(xml_conteudo)

        # Extrai o nome do elemento raiz (sem namespace)
        tag_local = etree.QName(root.tag).localname

        # Tenta identificar o evento pelo nome do elemento raiz
        # Ex: "eSocial" com filho "evtAdmissao" = S-2200
        # Verifica versao no atributo ou elemento
        versao = root.get("versao") or root.get("version")
        if versao is None:
            # Tenta extrair do namespace
            for _key, val in root.nsmap.items() if hasattr(root, "nsmap") else {}.items():
                if val and "esocial" in val.lower():
                    partes = val.rstrip("/").split("/")
                    if partes:
                        versao = partes[-1]

        # Verifica elemento evtXxx dentro do eSocial
        evento_el = None
        for child in root:
            tag_child = etree.QName(child.tag).localname
            if tag_child.startswith("evt"):
                evento_el = child
                evento_codigo = tag_child
                break

        if evento_el is None:
            # Pode ser evento raiz com nome direto
            if tag_local.startswith("evt"):
                evento_codigo = tag_local
            else:
                avisos.append(
                    f"Elemento raiz '{tag_local}' - nao foi possivel identificar o evento automaticamente"
                )

        # Verifica se o evento e conhecido
        evento_conhecido = any(
            e.nome.lower().replace(" ", "").find(evento_codigo[3:].lower()) >= 0
            for e in EVENTOS_ESOCIAL.values()
        )
        if not evento_conhecido and evento_codigo != "Desconhecido":
            avisos.append(
                f"Evento '{evento_codigo}' nao encontrado no catalogo de eventos conhecidos"
            )

        valido = len(erros) == 0

    except Exception as e:
        erros.append(f"Erro ao parsear XML: {e}")
        valido = False

    return ValidacaoESocialResponse(
        evento=evento_codigo,
        versao=versao,
        valido=valido,
        erros=erros,
        avisos=avisos,
    )
