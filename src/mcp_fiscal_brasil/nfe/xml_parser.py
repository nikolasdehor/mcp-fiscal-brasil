"""Parser de XML de NFe (versao 4.00)."""

from datetime import datetime

from lxml import etree

from ..shared.xml_utils import NS_NFE, parse_xml, xpath_text
from .schemas import EnderecoNFe, ItemNFe, NFeResponse, TotaisNFe


def _safe_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _parse_endereco(element: etree._Element | None, ns: dict[str, str]) -> EnderecoNFe | None:
    if element is None:
        return None
    return EnderecoNFe(
        nome=xpath_text(element, "nfe:xNome/text()", ns),
        cnpj=xpath_text(element, "nfe:CNPJ/text()", ns),
        cpf=xpath_text(element, "nfe:CPF/text()", ns),
        ie=xpath_text(element, "nfe:IE/text()", ns),
        logradouro=xpath_text(element, "nfe:enderEmit/nfe:xLgr/text()", ns)
        or xpath_text(element, "nfe:enderDest/nfe:xLgr/text()", ns),
        numero=xpath_text(element, "nfe:enderEmit/nfe:nro/text()", ns)
        or xpath_text(element, "nfe:enderDest/nfe:nro/text()", ns),
        bairro=xpath_text(element, "nfe:enderEmit/nfe:xBairro/text()", ns)
        or xpath_text(element, "nfe:enderDest/nfe:xBairro/text()", ns),
        municipio=xpath_text(element, "nfe:enderEmit/nfe:xMun/text()", ns)
        or xpath_text(element, "nfe:enderDest/nfe:xMun/text()", ns),
        uf=xpath_text(element, "nfe:enderEmit/nfe:UF/text()", ns)
        or xpath_text(element, "nfe:enderDest/nfe:UF/text()", ns),
        cep=xpath_text(element, "nfe:enderEmit/nfe:CEP/text()", ns)
        or xpath_text(element, "nfe:enderDest/nfe:CEP/text()", ns),
    )


def _parse_item(det: etree._Element, ns: dict[str, str]) -> ItemNFe:
    numero_str = det.get("nItem", "0")
    prod = det.find("nfe:prod", ns)
    imposto = det.find("nfe:imposto", ns)

    icms_el = None
    if imposto is not None:
        icms_group = imposto.find("nfe:ICMS", ns)
        if icms_group is not None and len(icms_group):
            icms_el = icms_group[0]  # ICMS00, ICMS10, etc.

    return ItemNFe(
        numero=int(numero_str),
        codigo_produto=xpath_text(prod, "nfe:cProd/text()", ns) or "" if prod is not None else "",
        descricao=xpath_text(prod, "nfe:xProd/text()", ns) or "" if prod is not None else "",
        ncm=xpath_text(prod, "nfe:NCM/text()", ns) if prod is not None else None,
        cfop=xpath_text(prod, "nfe:CFOP/text()", ns) or "" if prod is not None else "",
        unidade=xpath_text(prod, "nfe:uCom/text()", ns) or "" if prod is not None else "",
        quantidade=_safe_float(
            xpath_text(prod, "nfe:qCom/text()", ns) if prod is not None else None
        )
        or 0.0,
        valor_unitario=_safe_float(
            xpath_text(prod, "nfe:vUnCom/text()", ns) if prod is not None else None
        )
        or 0.0,
        valor_total=_safe_float(
            xpath_text(prod, "nfe:vProd/text()", ns) if prod is not None else None
        )
        or 0.0,
        cst_icms=xpath_text(icms_el, "nfe:CST/text()", ns) if icms_el is not None else None,
        aliquota_icms=_safe_float(
            xpath_text(icms_el, "nfe:pICMS/text()", ns) if icms_el is not None else None
        ),
        valor_icms=_safe_float(
            xpath_text(icms_el, "nfe:vICMS/text()", ns) if icms_el is not None else None
        ),
    )


def parse_nfe_xml(xml_content: str | bytes, chave: str) -> NFeResponse:
    """
    Parseia o XML de uma NFe e retorna NFeResponse.

    Suporta NFe versao 4.00 com namespace do portal fiscal.
    """
    root = parse_xml(xml_content)
    ns = NS_NFE

    # A raiz pode ser <nfeProc> ou diretamente <NFe>
    nfe_el = root.find(".//nfe:NFe", ns) or root
    inf_nfe = nfe_el.find(".//nfe:infNFe", ns)

    if inf_nfe is None:
        # Tenta sem namespace
        inf_nfe = root.find(".//infNFe")

    ide = inf_nfe.find("nfe:ide", ns) if inf_nfe is not None else None
    emit = inf_nfe.find("nfe:emit", ns) if inf_nfe is not None else None
    dest = inf_nfe.find("nfe:dest", ns) if inf_nfe is not None else None
    total = inf_nfe.find("nfe:total/nfe:ICMSTot", ns) if inf_nfe is not None else None

    # Data de emissao
    data_emissao = None
    raw_dhemi = xpath_text(ide, "nfe:dhEmi/text()", ns) if ide is not None else None
    if raw_dhemi:
        try:
            data_emissao = datetime.fromisoformat(raw_dhemi.replace("Z", "+00:00"))
        except ValueError:
            pass

    # Protocolo de autorizacao
    prot_nfe = root.find(".//nfe:protNFe", ns)
    protocolo = (
        xpath_text(prot_nfe, "nfe:infProt/nfe:nProt/text()", ns) if prot_nfe is not None else None
    )

    # Itens
    itens = []
    if inf_nfe is not None:
        for det in inf_nfe.findall("nfe:det", ns):
            itens.append(_parse_item(det, ns))

    # Totais
    totais = None
    if total is not None:
        totais = TotaisNFe(
            valor_produtos=_safe_float(xpath_text(total, "nfe:vProd/text()", ns)),
            valor_desconto=_safe_float(xpath_text(total, "nfe:vDesc/text()", ns)),
            valor_frete=_safe_float(xpath_text(total, "nfe:vFrete/text()", ns)),
            base_calculo_icms=_safe_float(xpath_text(total, "nfe:vBC/text()", ns)),
            valor_icms=_safe_float(xpath_text(total, "nfe:vICMS/text()", ns)),
            valor_icms_st=_safe_float(xpath_text(total, "nfe:vST/text()", ns)),
            valor_ipi=_safe_float(xpath_text(total, "nfe:vIPI/text()", ns)),
            valor_pis=_safe_float(xpath_text(total, "nfe:vPIS/text()", ns)),
            valor_cofins=_safe_float(xpath_text(total, "nfe:vCOFINS/text()", ns)),
            valor_nota=_safe_float(xpath_text(total, "nfe:vNF/text()", ns)),
        )

    return NFeResponse(
        chave_acesso=chave,
        numero=xpath_text(ide, "nfe:nNF/text()", ns) if ide is not None else None,
        serie=xpath_text(ide, "nfe:serie/text()", ns) if ide is not None else None,
        modelo=xpath_text(ide, "nfe:mod/text()", ns) or "55" if ide is not None else "55",
        emitente=_parse_endereco(emit, ns),
        destinatario=_parse_endereco(dest, ns),
        data_emissao=data_emissao,
        natureza_operacao=xpath_text(ide, "nfe:natOp/text()", ns) if ide is not None else None,
        tipo_operacao=xpath_text(ide, "nfe:tpNF/text()", ns) if ide is not None else None,
        itens=itens,
        totais=totais,
        protocolo_autorizacao=protocolo,
    )
