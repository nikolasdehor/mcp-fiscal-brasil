"""Utilitarios para parse e geracao de XML fiscal (NFe, NFSe, SPED)."""

import re
from typing import Any

from lxml import etree

from .exceptions import XMLParseError

# Namespaces NFe (versao 4.00)
NS_NFE = {
    "nfe": "http://www.portalfiscal.inf.br/nfe",
    "ds": "http://www.w3.org/2000/09/xmldsig#",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}

# Namespace CTe
NS_CTE = {"cte": "http://www.portalfiscal.inf.br/cte"}

# Namespace MDFe
NS_MDFE = {"mdfe": "http://www.portalfiscal.inf.br/mdfe"}


_SAFE_PARSER = etree.XMLParser(
    resolve_entities=False,
    no_network=True,
    load_dtd=False,
)


def parse_xml(content: str | bytes) -> etree._Element:
    """
    Parseia XML e retorna o elemento raiz.

    Usa parser seguro contra XXE (resolve_entities=False, no_network=True).
    Lanca XMLParseError em caso de XML invalido.
    """
    try:
        if isinstance(content, str):
            content = content.encode("utf-8")
        return etree.fromstring(content, parser=_SAFE_PARSER)
    except etree.XMLSyntaxError as e:
        raw = (
            content.decode("utf-8", errors="replace")[:500]
            if isinstance(content, bytes)
            else str(content)[:500]
        )
        raise XMLParseError(f"XML invalido: {e}", raw_content=raw) from e


def xpath_text(
    element: etree._Element, xpath: str, namespaces: dict[str, str] | None = None
) -> str | None:
    """Extrai o texto do primeiro elemento encontrado pelo XPath."""
    results = element.xpath(xpath, namespaces=namespaces or NS_NFE)
    if not results:
        return None
    node = results[0]
    if isinstance(node, str):
        return node
    if hasattr(node, "text"):
        return str(node.text) if node.text is not None else None
    return str(node)


def xpath_all_text(
    element: etree._Element, xpath: str, namespaces: dict[str, str] | None = None
) -> list[str]:
    """Extrai o texto de todos os elementos encontrados pelo XPath."""
    results = element.xpath(xpath, namespaces=namespaces or NS_NFE)
    texts = []
    for node in results:
        if isinstance(node, str):
            texts.append(node)
        elif hasattr(node, "text") and node.text:
            texts.append(node.text)
    return texts


def element_to_dict(element: etree._Element) -> dict[str, Any] | str:
    """
    Converte um elemento XML para dicionario Python.

    Util para serializar partes de NFe para JSON.
    """
    result: dict[str, Any] = {}

    # Atributos do elemento
    if element.attrib:
        result["@attrs"] = dict(element.attrib)

    # Texto direto do elemento
    element_text: str | None = element.text
    if element_text and element_text.strip():
        if not list(element):  # folha sem filhos
            return element_text.strip()
        result["#text"] = element_text.strip()

    # Filhos recursivos
    for child in element:
        # Remove namespace do tag
        tag = etree.QName(child.tag).localname
        child_value = element_to_dict(child)

        if tag in result:
            # Converte em lista se ja existe a chave
            if not isinstance(result[tag], list):
                result[tag] = [result[tag]]
            result[tag].append(child_value)
        else:
            result[tag] = child_value

    return result


def strip_namespace(xml_string: str) -> str:
    """Remove declaracoes de namespace do XML para facilitar parsing simples."""
    xml_string = re.sub(r'\s+xmlns(?::\w+)?="[^"]*"', "", xml_string)
    xml_string = re.sub(r"<(\w+):", "<", xml_string)
    xml_string = re.sub(r"</(\w+):", "</", xml_string)
    return xml_string


def build_soap_envelope(body_content: str, namespace: str = "") -> str:
    """
    Monta um envelope SOAP para envio a webservices da SEFAZ.

    Retorna a string XML completa com o envelope.
    """
    ns_attr = f' xmlns="{namespace}"' if namespace else ""
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
        'xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">'
        f"<soap12:Body{ns_attr}>"
        f"{body_content}"
        "</soap12:Body>"
        "</soap12:Envelope>"
    )


def extract_soap_body(soap_response: str) -> etree._Element:
    """
    Extrai o conteudo do Body de uma resposta SOAP.

    Lanca XMLParseError se o envelope for invalido.
    """
    root = parse_xml(soap_response)
    ns = {
        "soap": "http://www.w3.org/2003/05/soap-envelope",
        "soap11": "http://schemas.xmlsoap.org/soap/envelope/",
    }
    # Tenta SOAP 1.2 e depois 1.1
    body = root.xpath("//soap:Body/*[1]", namespaces=ns) or root.xpath(
        "//soap11:Body/*[1]", namespaces=ns
    )
    if not body:
        raise XMLParseError("Nao foi possivel encontrar o Body na resposta SOAP")
    return body[0]
