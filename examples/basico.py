"""
Exemplo basico de uso do mcp-fiscal-brasil como biblioteca Python.

Demonstra as operacoes mais comuns: consulta de CNPJ, validacao de CPF
e verificacao de status do SEFAZ.

Executar:
    python examples/basico.py
"""

import asyncio

from mcp_fiscal_brasil import FiscalBrasil, validate_cnpj, validate_cpf


async def main() -> None:
    async with FiscalBrasil() as fiscal:
        # --- Validacao offline (sem chamada de API, instantanea) ---
        print("=== Validacao offline ===")
        print(f"CPF 529.982.247-25 valido: {fiscal.validar_cpf('529.982.247-25')}")
        print(f"CPF 111.111.111-11 valido: {fiscal.validar_cpf('111.111.111-11')}")
        print(f"CNPJ 33.000.167/0001-01 valido: {fiscal.validar_cnpj('33.000.167/0001-01')}")
        print(f"CNPJ 00.000.000/0000-00 valido: {fiscal.validar_cnpj('00.000.000/0000-00')}")

        # Validadores tambem disponíveis como funcoes avulsas
        print(f"\nvalidate_cpf('52998224725'): {validate_cpf('52998224725')}")
        print(f"validate_cnpj('33000167000101'): {validate_cnpj('33000167000101')}")

        # --- Consulta CNPJ (requer internet) ---
        print("\n=== Consulta CNPJ (Petrobras) ===")
        try:
            empresa = await fiscal.consultar_cnpj("33.000.167/0001-01")
            print(f"Razao Social: {empresa.razao_social}")
            print(f"Nome Fantasia: {empresa.nome_fantasia}")
            print(f"Situacao: {empresa.situacao_cadastral}")
            print(f"Natureza Juridica: {empresa.natureza_juridica}")
            if empresa.atividade_principal:
                print(
                    f"CNAE Principal: {empresa.atividade_principal.codigo} - "
                    f"{empresa.atividade_principal.descricao}"
                )
            if empresa.endereco:
                print(f"Endereco: {empresa.endereco.formatado()}")
            print(f"Fonte: {empresa.origem}")
        except Exception as e:
            print(f"Erro na consulta: {e}")

        # --- Chave NFe: validacao e extracao de campos ---
        print("\n=== Chave NFe ===")
        chave = "35230112345678901234550010000000011000000018"
        info = fiscal.validar_chave_nfe(chave)
        print(f"Chave: {chave}")
        print(f"Valida: {info['valida']}")
        print(f"UF: {info['uf']}")
        print(f"Emissao: {info['ano_mes']}")
        print(f"CNPJ Emitente: {info['cnpj_emitente']}")
        print(f"Modelo: {info['modelo']} ({'NFe' if info['modelo'] == '55' else 'NFCe/outro'})")
        print(f"Serie: {info['serie']}, Numero: {info['numero']}")

        # --- Status SEFAZ ---
        print("\n=== Status SEFAZ SP ===")
        try:
            status = await fiscal.status_sefaz("SP")
            print(f"UF: {status.uf}")
            print(f"Status: {status.status}")
            print(f"Descricao: {status.descricao}")
            print(f"Ambiente: {status.ambiente}")
        except Exception as e:
            print(f"Erro ao consultar SEFAZ: {e}")

        # --- eSocial: listagem de eventos ---
        print("\n=== Eventos eSocial (grupo Periodicos) ===")
        eventos = await fiscal.listar_eventos_esocial("Periodicos")
        for evento in eventos[:5]:
            print(f"  {evento['codigo']}: {evento['nome']}")
        print(f"  ... ({len(eventos)} eventos no grupo Periodicos)")


if __name__ == "__main__":
    asyncio.run(main())
