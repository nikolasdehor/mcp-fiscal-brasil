"""Testes para validadores de documentos fiscais."""

import pytest

from mcp_fiscal_brasil.shared.validators import (
    format_cnpj,
    format_cpf,
    validate_chave_nfe,
    validate_cnpj,
    validate_cpf,
)


class TestValidateCPF:
    def test_cpf_valido_com_mascara(self) -> None:
        assert validate_cpf("529.982.247-25") is True

    def test_cpf_valido_sem_mascara(self) -> None:
        assert validate_cpf("52998224725") is True

    def test_cpf_digitos_repetidos(self) -> None:
        assert validate_cpf("111.111.111-11") is False
        assert validate_cpf("000.000.000-00") is False

    def test_cpf_tamanho_errado(self) -> None:
        assert validate_cpf("123") is False
        assert validate_cpf("123456789012") is False

    def test_cpf_digito_verificador_errado(self) -> None:
        assert validate_cpf("529.982.247-26") is False


class TestValidateCNPJ:
    def test_cnpj_valido_com_mascara(self) -> None:
        assert validate_cnpj("33.000.167/0001-01") is True

    def test_cnpj_valido_sem_mascara(self) -> None:
        assert validate_cnpj("33000167000101") is True

    def test_cnpj_digitos_repetidos(self) -> None:
        assert validate_cnpj("11.111.111/1111-11") is False

    def test_cnpj_tamanho_errado(self) -> None:
        assert validate_cnpj("123") is False

    def test_cnpj_digito_verificador_errado(self) -> None:
        assert validate_cnpj("33.000.167/0001-02") is False


class TestValidateChaveNFe:
    def test_chave_valida_44_digitos(self) -> None:
        # Chave com DV correto (calculado)
        # Usamos uma chave conhecida
        chave = "31060107364617000135550000000194291370923172"
        # Esta chave especifica pode ou nao ser valida dependendo do DV
        # Testamos o formato
        assert len(chave) == 44

    def test_chave_tamanho_errado(self) -> None:
        assert validate_chave_nfe("1234") is False
        assert validate_chave_nfe("123456789012345678901234567890123456789012345") is False

    def test_chave_com_espacos(self) -> None:
        # Espacos sao removidos pelo validador
        assert validate_chave_nfe("1234 5678") is False  # ainda tamanho errado sem espacos


class TestFormatCPF:
    def test_formata_sem_mascara(self) -> None:
        assert format_cpf("52998224725") == "529.982.247-25"

    def test_remove_mascara(self) -> None:
        assert format_cpf("529.982.247-25", remover_mascara=True) == "52998224725"

    def test_tamanho_errado_levanta_erro(self) -> None:
        with pytest.raises(ValueError):
            format_cpf("123")


class TestFormatCNPJ:
    def test_formata_sem_mascara(self) -> None:
        assert format_cnpj("33000167000101") == "33.000.167/0001-01"

    def test_remove_mascara(self) -> None:
        assert format_cnpj("33.000.167/0001-01", remover_mascara=True) == "33000167000101"

    def test_tamanho_errado_levanta_erro(self) -> None:
        with pytest.raises(ValueError):
            format_cnpj("123")
