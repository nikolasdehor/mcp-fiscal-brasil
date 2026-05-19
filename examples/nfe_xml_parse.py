"""Demonstra o parse de um XML NFe mockado sem depender de API externa."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from mcp_fiscal_brasil.nfe.xml_parser import parse_nfe_xml  # noqa: E402, I001


MOCK_NFE_XML = """
<NFe xmlns="http://www.portalfiscal.inf.br/nfe">
  <infNFe Id="NFe35240112345678000195550010000001231000000012">
    <ide>
      <mod>55</mod>
      <serie>1</serie>
      <nNF>123</nNF>
      <dhEmi>2024-01-31T10:30:00-03:00</dhEmi>
      <natOp>Venda de mercadoria</natOp>
      <tpNF>1</tpNF>
    </ide>
    <emit>
      <CNPJ>12345678000195</CNPJ>
      <xNome>EMPRESA TESTE LTDA</xNome>
      <enderEmit>
        <xLgr>Rua Fiscal</xLgr>
        <nro>100</nro>
        <xBairro>Centro</xBairro>
        <xMun>Sao Paulo</xMun>
        <UF>SP</UF>
        <CEP>01001000</CEP>
      </enderEmit>
    </emit>
    <dest>
      <CPF>52998224725</CPF>
      <xNome>CONSUMIDOR TESTE</xNome>
    </dest>
    <det nItem="1">
      <prod>
        <cProd>SKU-1</cProd>
        <xProd>Produto fiscal de teste</xProd>
        <NCM>01012100</NCM>
        <CFOP>5102</CFOP>
        <uCom>UN</uCom>
        <qCom>2.0000</qCom>
        <vUnCom>50.00</vUnCom>
        <vProd>100.00</vProd>
      </prod>
      <imposto>
        <ICMS>
          <ICMS00>
            <CST>00</CST>
            <pICMS>18.00</pICMS>
            <vICMS>18.00</vICMS>
          </ICMS00>
        </ICMS>
      </imposto>
    </det>
    <total>
      <ICMSTot>
        <vProd>100.00</vProd>
        <vBC>100.00</vBC>
        <vICMS>18.00</vICMS>
        <vNF>100.00</vNF>
      </ICMSTot>
    </total>
  </infNFe>
</NFe>
"""


def main() -> None:
    nfe = parse_nfe_xml(MOCK_NFE_XML, "35240112345678000195550010000001231000000012")

    print("=== XML NFe mock ===")
    print(f"Numero: {nfe.numero}")
    print(f"Serie: {nfe.serie}")
    print(f"Natureza: {nfe.natureza_operacao}")
    print(f"Emitente: {nfe.emitente.nome if nfe.emitente else '-'}")
    print(f"Itens: {len(nfe.itens)}")
    if nfe.itens:
        item = nfe.itens[0]
        print(f"Item 1: {item.codigo_produto} - {item.descricao}")
        print(f"Valor do item: {item.valor_total:.2f}")
    if nfe.totais:
        print(f"Valor da nota: {nfe.totais.valor_nota:.2f}")


if __name__ == "__main__":
    main()
