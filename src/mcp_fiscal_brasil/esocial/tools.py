"""Ferramentas MCP para eSocial."""

from lxml import etree

from ..shared.xml_utils import parse_xml
from .schemas import EventoESocial, ValidacaoESocialResponse

# Catálogo completo dos eventos eSocial (45+ eventos - S-1.0 e posteriores)
EVENTOS_ESOCIAL: dict[str, EventoESocial] = {
    # Eventos de Tabelas (11 eventos)
    "S-1000": EventoESocial(
        codigo="S-1000",
        nome="Informações do Empregador/Contribuinte/Órgão Público",
        grupo="Tabelas",
        descricao="Cadastro do empregador no eSocial. Deve ser o primeiro evento enviado.",
    ),
    "S-1005": EventoESocial(
        codigo="S-1005",
        nome="Tabela de Estabelecimentos, Obras ou Unidades de Órgão Público",
        grupo="Tabelas",
        descricao="Cadastro de estabelecimentos, CNPJ/CEI/CAEPF.",
    ),
    "S-1010": EventoESocial(
        codigo="S-1010",
        nome="Tabela de Rubricas",
        grupo="Tabelas",
        descricao="Definição das verbas/rubricas da folha de pagamento.",
    ),
    "S-1020": EventoESocial(
        codigo="S-1020",
        nome="Tabela de Lotações Tributárias",
        grupo="Tabelas",
        descricao="Definição das lotações tributárias para apuração de contribuições.",
    ),
    "S-1030": EventoESocial(
        codigo="S-1030",
        nome="Tabela de Cargos/Empregos Públicos",
        grupo="Tabelas",
        descricao="Cadastro de cargos e empregos públicos da organização.",
    ),
    "S-1035": EventoESocial(
        codigo="S-1035",
        nome="Tabela de Cargas Horárias/Horários de Trabalho",
        grupo="Tabelas",
        descricao="Definição de jornadas, horários e turnos de trabalho.",
    ),
    "S-1040": EventoESocial(
        codigo="S-1040",
        nome="Tabela de Funções/Cargos em Comissão",
        grupo="Tabelas",
        descricao="Cadastro de funções e cargos em comissão.",
    ),
    "S-1050": EventoESocial(
        codigo="S-1050",
        nome="Tabela de Horários/Turnos de Trabalho",
        grupo="Tabelas",
        descricao="Definição de horários e turnos da organização.",
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
        nome="Tabela de Operadores Portuários",
        grupo="Tabelas",
        descricao="Cadastro de operadores portuários e trabalho portuário.",
    ),
    # Eventos Não Periódicos - Cadastramento de Trabalhador (5 eventos)
    "S-2190": EventoESocial(
        codigo="S-2190",
        nome="Registro Preliminar de Trabalhador",
        grupo="Nao Periodicos",
        descricao="Registro preliminar do trabalhador antes da admissão.",
    ),
    "S-2200": EventoESocial(
        codigo="S-2200",
        nome="Cadastramento Inicial do Vínculo e Admissão/Ingresso de Trabalhador",
        grupo="Nao Periodicos",
        descricao="Admissão de empregado ou ingresso de trabalhador.",
    ),
    "S-2205": EventoESocial(
        codigo="S-2205",
        nome="Alteração de Dados Cadastrais do Trabalhador",
        grupo="Nao Periodicos",
        descricao="Alteração de dados pessoais do trabalhador.",
    ),
    "S-2206": EventoESocial(
        codigo="S-2206",
        nome="Alteração de Contrato de Trabalho",
        grupo="Nao Periodicos",
        descricao="Alteração de cargo, salário, jornada de trabalho etc.",
    ),
    "S-2207": EventoESocial(
        codigo="S-2207",
        nome="Alteração de Contrato - Fim de Obra",
        grupo="Nao Periodicos",
        descricao="Registro de fim de obra ou contrato com prazo determinado.",
    ),
    # Eventos Não Periódicos - Saúde e Segurança do Trabalho (5 eventos)
    "S-2210": EventoESocial(
        codigo="S-2210",
        nome="Comunicação de Acidente de Trabalho",
        grupo="Nao Periodicos",
        descricao="Registro de acidente de trabalho conforme Lei 8213/99.",
    ),
    "S-2220": EventoESocial(
        codigo="S-2220",
        nome="Monitoramento da Saúde do Trabalhador",
        grupo="Nao Periodicos",
        descricao="Informações de exames ocupacionais e ASO (Atestado de Saúde Ocupacional).",
    ),
    "S-2230": EventoESocial(
        codigo="S-2230",
        nome="Afastamento Temporário",
        grupo="Nao Periodicos",
        descricao="Registro de afastamento: férias, licença, atestado etc.",
    ),
    "S-2240": EventoESocial(
        codigo="S-2240",
        nome="Condições Ambientais do Trabalho - Agentes Nocivos",
        grupo="Nao Periodicos",
        descricao="Registro de ambientes com agentes nocivos e trabalho insalubre.",
    ),
    "S-2250": EventoESocial(
        codigo="S-2250",
        nome="Aviso Prévio",
        grupo="Nao Periodicos",
        descricao="Comunicação de aviso prévio de desligamento do trabalhador.",
    ),
    # Eventos Não Periódicos - Desligamento (3 eventos)
    "S-2260": EventoESocial(
        codigo="S-2260",
        nome="Convocação para Trabalho Intermitente",
        grupo="Nao Periodicos",
        descricao="Registro de convocação de trabalhador intermitente.",
    ),
    "S-2298": EventoESocial(
        codigo="S-2298",
        nome="Reintegração/Outros Provimentos",
        grupo="Nao Periodicos",
        descricao="Registro de reintegração ou outros provimentos trabalhistas.",
    ),
    "S-2299": EventoESocial(
        codigo="S-2299",
        nome="Desligamento",
        grupo="Nao Periodicos",
        descricao="Rescisão de contrato de trabalho. Prazo: 10 dias após desligamento.",
    ),
    # Eventos Não Periódicos - Benefícios (3 eventos)
    "S-2400": EventoESocial(
        codigo="S-2400",
        nome="Cadastro de Benefícios Previdenciários - RPPS",
        grupo="Nao Periodicos",
        descricao="Concessão de benefício previdenciário do RPPS.",
    ),
    "S-2405": EventoESocial(
        codigo="S-2405",
        nome="Alteração de Benefício - RPPS",
        grupo="Nao Periodicos",
        descricao="Alteração de dados de benefício previdenciário do RPPS.",
    ),
    "S-2410": EventoESocial(
        codigo="S-2410",
        nome="Termo de Cessação de Benefício - RPPS",
        grupo="Nao Periodicos",
        descricao="Cessação de benefício previdenciário do RPPS.",
    ),
    # Eventos Não Periódicos - Processos e Competências (3 eventos)
    "S-2500": EventoESocial(
        codigo="S-2500",
        nome="Processo Trabalhista",
        grupo="Nao Periodicos",
        descricao="Registro de reclamatória trabalhista e valores devidos.",
    ),
    "S-2501": EventoESocial(
        codigo="S-2501",
        nome="Alteração de Processo Trabalhista",
        grupo="Nao Periodicos",
        descricao="Alteração de dados de processo trabalhista registrado.",
    ),
    # Eventos Periódicos - Folha de Pagamento (6 eventos)
    "S-1200": EventoESocial(
        codigo="S-1200",
        nome="Remuneração de Trabalhador vinculado ao Regime Geral de Prev. Social",
        grupo="Periodicos",
        descricao="Folha de pagamento mensal - RGPS.",
    ),
    "S-1202": EventoESocial(
        codigo="S-1202",
        nome="Remuneração de Servidor vinculado ao Regime Próprio de Prev. Social",
        grupo="Periodicos",
        descricao="Folha de pagamento mensal - RPPS.",
    ),
    "S-1204": EventoESocial(
        codigo="S-1204",
        nome="Informações Complementares de Contribuinte sem Movimentação",
        grupo="Periodicos",
        descricao="Evento para contribuinte que não teve movimentação no período.",
    ),
    "S-1207": EventoESocial(
        codigo="S-1207",
        nome="Benefícios Previdenciários - RPPS",
        grupo="Periodicos",
        descricao="Pagamento de benefícios do RPPS.",
    ),
    "S-1210": EventoESocial(
        codigo="S-1210",
        nome="Pagamentos de Rendimentos do Trabalho",
        grupo="Periodicos",
        descricao="Pagamentos a trabalhadores sem vínculo (autônomos, etc.).",
    ),
    "S-1212": EventoESocial(
        codigo="S-1212",
        nome="Remuneração de Contribuinte Individual",
        grupo="Periodicos",
        descricao="Remuneração de contribuinte individual (autônomo).",
    ),
    # Eventos Periódicos - Produção Rural e Avulsos (3 eventos)
    "S-1260": EventoESocial(
        codigo="S-1260",
        nome="Comercialização da Produção Rural Pessoa Física",
        grupo="Periodicos",
        descricao="Produção rural comercializada pelo segurado especial.",
    ),
    "S-1270": EventoESocial(
        codigo="S-1270",
        nome="Contratação de Trabalhadores Avulsos Não Portuários",
        grupo="Periodicos",
        descricao="Contratação de trabalhador avulso não portuário.",
    ),
    "S-1280": EventoESocial(
        codigo="S-1280",
        nome="Informações Complementares do Contribuinte",
        grupo="Periodicos",
        descricao="Informações adicionais necessárias para complementação da folha.",
    ),
    # Eventos Periódicos - Totalizadores e Fechamento (3 eventos)
    "S-1295": EventoESocial(
        codigo="S-1295",
        nome="Solicitação de Totalizador para Pagamento em Atraso",
        grupo="Periodicos",
        descricao="Solicita totalizador para recolhimento em atraso.",
    ),
    "S-1298": EventoESocial(
        codigo="S-1298",
        nome="Reabertura dos Eventos Periódicos",
        grupo="Periodicos",
        descricao="Reabre competência fechada para correções.",
    ),
    "S-1299": EventoESocial(
        codigo="S-1299",
        nome="Fechamento dos Eventos Periódicos",
        grupo="Periodicos",
        descricao="Fecha a competência e gera DCTFWeb/GFIP.",
    ),
    # Eventos de Exclusão (1 evento)
    "S-3000": EventoESocial(
        codigo="S-3000",
        nome="Exclusão de Eventos",
        grupo="Exclusao",
        descricao="Exclui um evento anteriormente enviado.",
    ),
    # Eventos Retorno do Governo - Totalizadores (7 eventos)
    "S-5001": EventoESocial(
        codigo="S-5001",
        nome="Informações das Contribuições Sociais por Trabalhador",
        grupo="Totalizadores",
        descricao="Resumo das contribuições sociais por trabalhador no período.",
    ),
    "S-5002": EventoESocial(
        codigo="S-5002",
        nome="Totalização da Remuneração",
        grupo="Totalizadores",
        descricao="Totalização das remunerações da organização no período.",
    ),
    "S-5003": EventoESocial(
        codigo="S-5003",
        nome="Totalização de Contribuições",
        grupo="Totalizadores",
        descricao="Totalização de todas as contribuições devidas.",
    ),
    "S-5011": EventoESocial(
        codigo="S-5011",
        nome="Informações Consolidadas da Competência - Contribuinte",
        grupo="Totalizadores",
        descricao="Consolidação de informações do contribuinte na competência.",
    ),
    "S-5012": EventoESocial(
        codigo="S-5012",
        nome="Informações Consolidadas da Competência - Gestor de Pessoas Física",
        grupo="Totalizadores",
        descricao="Consolidação de informações para gestor de pessoas físicas.",
    ),
    "S-5013": EventoESocial(
        codigo="S-5013",
        nome="Informações Consolidadas da Competência - Produtor Rural",
        grupo="Totalizadores",
        descricao="Consolidação de informações para produtor rural.",
    ),
}


async def listar_eventos_esocial(grupo: str | None = None) -> list[EventoESocial]:
    """
    Lista os eventos do eSocial, opcionalmente filtrados por grupo.

    Args:
        grupo: Filtrar por grupo: 'Tabelas', 'Nao Periodicos', 'Periodicos', 'Exclusao'.
               Se None, retorna todos os eventos.

    Returns:
        Lista de eventos eSocial com código, nome, grupo e descrição.
    """
    eventos = list(EVENTOS_ESOCIAL.values())
    if grupo:
        grupo_lower = grupo.lower()
        eventos = [e for e in eventos if grupo_lower in e.grupo.lower()]
    return sorted(eventos, key=lambda e: e.codigo)


async def validar_evento_esocial(xml_conteudo: str) -> ValidacaoESocialResponse:
    """
    Realiza validação básica de estrutura de um XML de evento eSocial.

    Verifica:
    - Presença do elemento raiz correto
    - Código do evento
    - Versão do leiaute

    Não valida schema XSD completo (exige bibliotecas adicionais).

    Args:
        xml_conteudo: Conteúdo do XML do evento eSocial

    Returns:
        ValidacaoESocialResponse com resultado da validação.
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
        # Verifica versão no atributo ou elemento
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
                    f"Elemento raiz '{tag_local}' - não foi possível identificar o evento automaticamente"
                )

        # Verifica se o evento é conhecido
        evento_conhecido = any(
            e.nome.lower().replace(" ", "").find(evento_codigo[3:].lower()) >= 0
            for e in EVENTOS_ESOCIAL.values()
        )
        if not evento_conhecido and evento_codigo != "Desconhecido":
            avisos.append(
                f"Evento '{evento_codigo}' não encontrado no catálogo de eventos conhecidos"
            )

        valido = len(erros) == 0

    except Exception as e:
        erros.append(f"Erro ao processar XML: {e}")
        valido = False

    return ValidacaoESocialResponse(
        evento=evento_codigo,
        versao=versao,
        valido=valido,
        erros=erros,
        avisos=avisos,
    )
