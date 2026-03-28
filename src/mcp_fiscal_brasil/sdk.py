"""
MCP Fiscal Brasil - SDK para integracao direta em aplicacoes Python.

Permite usar todas as funcionalidades fiscais como biblioteca Python,
sem precisar rodar o servidor MCP.

Uso basico:

    from mcp_fiscal_brasil import FiscalBrasil

    fiscal = FiscalBrasil()

    # Consultar CNPJ
    empresa = await fiscal.consultar_cnpj("00.000.000/0001-91")
    print(empresa.razao_social)

    # Validar CPF
    valido = fiscal.validar_cpf("123.456.789-09")

    # Status SEFAZ
    status = await fiscal.status_sefaz("SP")

Uso como context manager (recomendado para multiplas consultas):

    async with FiscalBrasil() as fiscal:
        empresa = await fiscal.consultar_cnpj("33.000.167/0001-01")
        simples = await fiscal.consultar_simples("33.000.167/0001-01")
"""

from __future__ import annotations

import asyncio
from types import TracebackType
from typing import Any

from .cnpj.client import CNPJClient
from .cnpj.schemas import CNPJResponse
from .nfe.client import NFEClient
from .nfe.schemas import NFeResponse, StatusSEFAZResponse
from .shared.validators import validate_chave_nfe, validate_cnpj, validate_cpf
from .simples.client import SimplesClient
from .simples.schemas import SimplesNacionalResponse


class FiscalBrasil:
    """
    Interface unificada para consultas fiscais brasileiras.

    Encapsula todos os clientes do pacote (CNPJ, NFe, Simples Nacional,
    eSocial, SPED, NFSe) em um unico ponto de entrada.

    Pode ser usada como context manager assincrono para garantir o
    encerramento correto de recursos de rede:

        async with FiscalBrasil() as fiscal:
            empresa = await fiscal.consultar_cnpj("33000167000101")

    Ou instanciada diretamente quando o ciclo de vida e gerenciado
    externamente (ex: variavel de modulo em FastAPI):

        fiscal = FiscalBrasil()
        empresa = await fiscal.consultar_cnpj("33000167000101")
    """

    def __init__(self) -> None:
        self._cnpj_client = CNPJClient()
        self._nfe_client = NFEClient()
        self._simples_client = SimplesClient()

    # ------------------------------------------------------------------
    # Context manager assincrono
    # ------------------------------------------------------------------

    async def __aenter__(self) -> FiscalBrasil:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.fechar()

    async def fechar(self) -> None:
        """Encerra recursos de rede (conexoes HTTP). Opcional quando usado como variavel global."""
        # Os clientes criam e fecham conexoes por chamada via context manager interno,
        # portanto nao ha recursos persistentes a liberar nesta versao.
        # Este metodo existe para compatibilidade futura e para uso explicito.

    # ------------------------------------------------------------------
    # CNPJ
    # ------------------------------------------------------------------

    async def consultar_cnpj(self, cnpj: str) -> CNPJResponse:
        """
        Consulta os dados de um CNPJ na Receita Federal.

        Tenta BrasilAPI primeiro; em caso de falha, usa ReceitaWS como
        fallback automatico.

        Args:
            cnpj: CNPJ com ou sem mascara (ex: "33.000.167/0001-01" ou "33000167000101").

        Returns:
            CNPJResponse com razao social, endereco, CNAE, QSA e mais.

        Raises:
            ValueError: Se o CNPJ for invalido.
            Exception: Se todas as APIs externas falharem.

        Exemplo:
            empresa = await fiscal.consultar_cnpj("33.000.167/0001-01")
            print(empresa.razao_social)  # "PETROLEO BRASILEIRO S A PETROBRAS"
        """
        if not validate_cnpj(cnpj):
            raise ValueError(f"CNPJ invalido: {cnpj}")
        return await self._cnpj_client.consultar(cnpj)

    def validar_cnpj(self, cnpj: str) -> bool:
        """
        Valida o digito verificador de um CNPJ (offline, sem chamada de API).

        Args:
            cnpj: CNPJ com ou sem mascara.

        Returns:
            True se o CNPJ for matematicamente valido, False caso contrario.

        Exemplo:
            fiscal.validar_cnpj("33.000.167/0001-01")  # True
            fiscal.validar_cnpj("11.111.111/1111-11")  # False
        """
        return validate_cnpj(cnpj)

    # ------------------------------------------------------------------
    # CPF
    # ------------------------------------------------------------------

    def validar_cpf(self, cpf: str) -> bool:
        """
        Valida o digito verificador de um CPF (offline, sem chamada de API).

        A Receita Federal nao disponibiliza API publica para consulta de CPF.
        Esta validacao verifica apenas o calculo do digito verificador.

        Args:
            cpf: CPF com ou sem mascara (ex: "529.982.247-25" ou "52998224725").

        Returns:
            True se o CPF for matematicamente valido, False caso contrario.

        Exemplo:
            fiscal.validar_cpf("529.982.247-25")  # True
            fiscal.validar_cpf("111.111.111-11")  # False (sequencia repetida)
        """
        return validate_cpf(cpf)

    # ------------------------------------------------------------------
    # NFe
    # ------------------------------------------------------------------

    async def consultar_nfe(self, chave: str) -> NFeResponse:
        """
        Consulta os dados de uma NFe pela chave de acesso de 44 digitos.

        Cadeia de fallback automatica:
          1. BrasilAPI
          2. Portal Nacional NFe (SEFAZ federal)
          3. Dados parciais extraidos da propria chave

        Args:
            chave: Chave de acesso da NFe com 44 digitos numericos.

        Returns:
            NFeResponse com emitente, destinatario, itens, totais e situacao.

        Raises:
            ValueError: Se a chave de acesso for invalida.

        Exemplo:
            nfe = await fiscal.consultar_nfe("35230112345678901234550010000000011000000018")
            print(nfe.situacao)
        """
        if not validate_chave_nfe(chave):
            raise ValueError(f"Chave de acesso NFe invalida: {chave}")
        return await self._nfe_client.consultar_por_chave(chave)

    def validar_chave_nfe(self, chave: str) -> dict[str, Any]:
        """
        Valida e extrai os campos estruturais de uma chave de acesso NFe/NFCe.

        A validacao verifica o digito verificador pelo modulo 11 (offline).
        A extracao decodifica os campos embutidos na chave (UF, CNPJ, serie, etc.).

        Args:
            chave: Chave de acesso com 44 digitos numericos.

        Returns:
            Dicionario com campos extraidos:
            - valida (bool): Se o digito verificador e correto.
            - uf (str): UF de emissao.
            - ano_mes (str): Ano/mes de emissao no formato MM/AAAA.
            - cnpj_emitente (str): CNPJ do emitente (14 digitos).
            - modelo (str): Modelo do documento ("55"=NFe, "65"=NFCe).
            - serie (str): Serie da nota.
            - numero (str): Numero da nota fiscal.

        Exemplo:
            info = fiscal.validar_chave_nfe("35230112345678901234550010000000011000000018")
            print(info["uf"])          # "SP"
            print(info["cnpj_emitente"])  # "12345678901234"
        """
        from .shared.constants import CODIGO_UF

        numeros = "".join(c for c in chave if c.isdigit())
        valida = validate_chave_nfe(chave)

        if len(numeros) != 44:
            return {"valida": False, "erro": f"Chave deve ter 44 digitos, recebeu {len(numeros)}"}

        cod_uf = int(numeros[:2])
        return {
            "valida": valida,
            "uf": CODIGO_UF.get(cod_uf, f"UF {cod_uf}"),
            "ano_mes": f"{numeros[4:6]}/{numeros[2:4]}",
            "cnpj_emitente": numeros[6:20],
            "modelo": numeros[20:22],
            "serie": numeros[22:25],
            "numero": numeros[25:34],
            "tipo_emissao": numeros[34],
            "codigo_numerico": numeros[35:43],
            "digito_verificador": numeros[43],
        }

    async def status_sefaz(self, uf: str, ambiente: str = "producao") -> StatusSEFAZResponse:
        """
        Consulta o status do servico SEFAZ de uma UF.

        Usa BrasilAPI como proxy para o webservice do SEFAZ estadual.
        Em caso de falha, retorna status "Indisponivel".

        Args:
            uf: Sigla do estado (ex: "SP", "RJ", "MG"). Nao diferencia maiusculas.
            ambiente: "producao" ou "homologacao" (padrao: "producao").

        Returns:
            StatusSEFAZResponse com status, descricao e codigo de retorno.

        Exemplo:
            status = await fiscal.status_sefaz("SP")
            print(status.status)   # "Em Operacao"
        """
        return await self._nfe_client.consultar_status_servico(uf, ambiente)

    # ------------------------------------------------------------------
    # Simples Nacional
    # ------------------------------------------------------------------

    async def consultar_simples(self, cnpj: str) -> SimplesNacionalResponse:
        """
        Consulta a situacao de um CNPJ no Simples Nacional e MEI.

        Args:
            cnpj: CNPJ com ou sem mascara.

        Returns:
            SimplesNacionalResponse com optante_simples, optante_mei e datas de opcao/exclusao.

        Raises:
            ValueError: Se o CNPJ for invalido.

        Exemplo:
            simples = await fiscal.consultar_simples("33.000.167/0001-01")
            print(simples.optante_simples)  # False (Petrobras nao e optante)
            print(simples.optante_mei)      # False
        """
        if not validate_cnpj(cnpj):
            raise ValueError(f"CNPJ invalido: {cnpj}")
        return await self._simples_client.consultar(cnpj)

    # ------------------------------------------------------------------
    # SPED
    # ------------------------------------------------------------------

    async def analisar_sped(self, conteudo: str, nome_arquivo: str | None = None) -> dict[str, Any]:
        """
        Analisa um arquivo SPED e extrai informacoes estruturais.

        Suporta EFD-ICMS/IPI, EFD-Contribuicoes, ECD e ECF.
        O arquivo deve ser passado como string (conteudo completo no formato pipe-delimitado).

        Args:
            conteudo: Conteudo do arquivo SPED como string.
            nome_arquivo: Nome do arquivo (opcional, usado apenas para log).

        Returns:
            Dicionario com:
            - tipo_sped (str): Tipo identificado ("EFD-ICMS-IPI", "EFD-Contribuicoes", etc.)
            - abertura (dict | None): Dados do registro 0000 (empresa, CNPJ, UF).
            - resumo (dict): Periodo, total de registros e contagem por tipo.
            - erros (list[str]): Erros encontrados na estrutura.
            - avisos (list[str]): Avisos sobre o arquivo.

        Exemplo:
            with open("sped.txt") as f:
                conteudo = f.read()
            resultado = await fiscal.analisar_sped(conteudo)
            print(resultado["tipo_sped"])  # "EFD-ICMS-IPI"
        """
        from .sped.tools import analisar_sped

        resposta = await analisar_sped(conteudo, nome_arquivo)
        return resposta.model_dump()

    # ------------------------------------------------------------------
    # NFSe
    # ------------------------------------------------------------------

    async def portal_nfse(self, municipio: str, uf: str) -> dict[str, str]:
        """
        Retorna o portal de consulta de NFSe para um municipio.

        NFSe nao possui padrao nacional unico; cada municipio tem seu sistema
        (ABRASF, ISS.net, Betha, Curitiba, etc.). Este metodo localiza o portal
        correto para o municipio informado e, quando nao encontrado, retorna
        o Portal Nacional ABRASF como alternativa.

        Args:
            municipio: Nome do municipio (ex: "Sao Paulo", "Belo Horizonte").
            uf: Sigla do estado (ex: "SP", "MG").

        Returns:
            Dicionario com:
            - portal_municipio (str): URL do portal de consulta.
            - sistema_nfse (str): Sistema utilizado (ABRASF, ISS.net, etc.)
            - alternativa (str): Alternativa para integracao automatizada.
            - status (str): "consulta_manual_necessaria".

        Exemplo:
            portal = await fiscal.portal_nfse("Sao Paulo", "SP")
            print(portal["portal_municipio"])  # URL da prefeitura de SP
            print(portal["sistema_nfse"])      # "ABRASF"
        """
        from .nfse.tools import consultar_nfse

        resultado = await consultar_nfse(
            numero="",
            municipio=municipio,
            uf=uf,
        )
        return resultado

    # ------------------------------------------------------------------
    # eSocial
    # ------------------------------------------------------------------

    async def listar_eventos_esocial(self, grupo: str | None = None) -> list[dict[str, Any]]:
        """
        Lista os eventos do eSocial, com opcao de filtro por grupo.

        Args:
            grupo: Filtrar por grupo do evento. Valores validos:
                   "Tabelas", "Nao Periodicos", "Periodicos",
                   "Exclusao", "Totalizadores".
                   Se None, retorna todos os 45+ eventos catalogados.

        Returns:
            Lista de dicionarios com campos:
            - codigo (str): Codigo do evento (ex: "S-2200").
            - nome (str): Nome completo do evento.
            - grupo (str): Grupo ao qual pertence.
            - descricao (str): Descricao do proposito do evento.

        Exemplo:
            eventos = await fiscal.listar_eventos_esocial("Periodicos")
            for e in eventos:
                print(f"{e['codigo']}: {e['nome']}")
        """
        from .esocial.tools import listar_eventos_esocial

        eventos = await listar_eventos_esocial(grupo)
        return [e.model_dump() for e in eventos]

    # ------------------------------------------------------------------
    # Metodos sincronos (wrappers com asyncio.run)
    # ------------------------------------------------------------------

    def consultar_cnpj_sync(self, cnpj: str) -> CNPJResponse:
        """
        Versao sincrona de consultar_cnpj. Util em contextos nao-async (Django, scripts).

        Nao use dentro de um event loop ja ativo (ex: FastAPI, Jupyter).
        Prefira o metodo assincrono nesses casos.

        Args:
            cnpj: CNPJ com ou sem mascara.

        Returns:
            CNPJResponse com os dados da empresa.
        """
        return asyncio.run(self.consultar_cnpj(cnpj))

    def consultar_simples_sync(self, cnpj: str) -> SimplesNacionalResponse:
        """
        Versao sincrona de consultar_simples. Util em contextos nao-async.

        Args:
            cnpj: CNPJ com ou sem mascara.

        Returns:
            SimplesNacionalResponse com situacao no Simples Nacional.
        """
        return asyncio.run(self.consultar_simples(cnpj))

    def status_sefaz_sync(self, uf: str, ambiente: str = "producao") -> StatusSEFAZResponse:
        """
        Versao sincrona de status_sefaz. Util em contextos nao-async.

        Args:
            uf: Sigla do estado.
            ambiente: "producao" ou "homologacao".

        Returns:
            StatusSEFAZResponse com status do servico.
        """
        return asyncio.run(self.status_sefaz(uf, ambiente))
