# 🇧🇷 MCP Fiscal Brasil

> **O primeiro servidor MCP para o sistema fiscal brasileiro.**
> Conecte qualquer IA ao universo de CNPJ, NFe, SPED, eSocial e certidoes via linguagem natural.

[![PyPI version](https://img.shields.io/pypi/v/mcp-fiscal-brasil?color=blue&label=PyPI)](https://pypi.org/project/mcp-fiscal-brasil/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-purple)](https://modelcontextprotocol.io)

---

## O que e

**MCP Fiscal Brasil** e um servidor [Model Context Protocol (MCP)](https://modelcontextprotocol.io) que expoe o sistema fiscal brasileiro como ferramentas para assistentes de IA como Claude, GPT, Cursor e outros clientes MCP.

Com ele, voce pode perguntar ao seu assistente:

> _"Quais sao os socios da empresa com CNPJ 00.000.000/0001-91?"_
> _"Essa chave de NFe e valida? O que ela representa?"_
> _"A empresa XYZ e optante do Simples Nacional?"_

E o assistente consulta os dados diretamente nas fontes publicas - Receita Federal, BrasilAPI, SEFAZ - sem nenhuma configuracao adicional.

**Para quem e:**
- Contadores e escritorios de contabilidade que usam IA no dia a dia
- Desenvolvedores que integram sistemas fiscais
- Empresas que precisam automatizar validacoes e consultas tributarias
- Qualquer pessoa que lida com documentos fiscais brasileiros

---

## Ferramentas Disponiveis

| Modulo | Ferramenta | Descricao |
|--------|-----------|-----------|
| **CNPJ** | `consultar_cnpj` | Dados cadastrais completos: razao social, endereco, CNAE, QSA (socios), situacao e porte |
| **CNPJ** | `listar_cnpjs_por_nome` | Busca empresas por nome ou razao social (disponibilidade limitada em APIs publicas) |
| **CPF** | `validar_cpf` | Valida digito verificador de CPF (verificacao matematica offline) |
| **NFe** | `consultar_nfe` | Consulta NFe pela chave de acesso de 44 digitos: emitente, destinatario, itens e totais |
| **NFe** | `validar_chave_nfe` | Valida formato e digito verificador da chave; extrai UF, data, CNPJ emitente e numero |
| **NFe** | `consultar_status_sefaz` | Status em tempo real do webservice SEFAZ de qualquer estado brasileiro |
| **NFSe** | `consultar_nfse` | Orienta sobre como consultar NFSe no portal do municipio correto |
| **Simples Nacional** | `consultar_simples_nacional` | Situacao atual no Simples Nacional / MEI: opcao, datas de entrada e exclusao |
| **SPED** | `analisar_sped` | Analisa arquivo SPED (EFD-ICMS/IPI, EFD-Contribuicoes, ECD, ECF): periodo, empresa, registros e erros |
| **SPED** | `listar_registros_sped` | Extrai todas as ocorrencias de um tipo de registro do SPED (ex: C100, E110) |
| **eSocial** | `listar_eventos_esocial` | Lista eventos eSocial com nome, grupo e descricao; filtravel por grupo |
| **eSocial** | `validar_evento_esocial` | Valida estrutura basica de XML de evento eSocial: elemento raiz, codigo e versao do leiaute |
| **Certidoes** | `consultar_certidao_federal` | Orientacoes e URLs para emissao da CND (Certidao Negativa de Debitos) na Receita Federal |
| **Certidoes** | `consultar_certidao_fgts` | Orientacoes e URL para consulta da CRF (Certidao de Regularidade do FGTS) na Caixa |

**Total: 14 ferramentas** cobrindo os principais modulos do sistema fiscal brasileiro.

---

## Instalacao

### Via pip

```bash
pip install mcp-fiscal-brasil
```

### Via uv (recomendado)

```bash
uv add mcp-fiscal-brasil
```

### A partir do codigo-fonte

```bash
git clone https://github.com/nikolasdehor/mcp-fiscal-brasil.git
cd mcp-fiscal-brasil
pip install -e .
```

---

## Configuracao

### Claude Desktop

Edite o arquivo `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) ou `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "fiscal-brasil": {
      "command": "mcp-fiscal-brasil"
    }
  }
}
```

Reinicie o Claude Desktop. As 14 ferramentas fiscais aparecerao automaticamente.

### Claude Code (CLI)

```bash
claude mcp add fiscal-brasil -- mcp-fiscal-brasil
```

### Cursor / VS Code

Adicione ao `settings.json` do Cursor ou ao arquivo `.cursor/mcp.json` do projeto:

```json
{
  "mcpServers": {
    "fiscal-brasil": {
      "command": "mcp-fiscal-brasil"
    }
  }
}
```

### Outros clientes MCP

O servidor usa o transporte `stdio` padrao. Qualquer cliente MCP compativel pode conectar com:

```
command: mcp-fiscal-brasil
```

---

## Exemplos de Uso

Pergunte ao seu assistente em linguagem natural:

**Consultas de empresa:**
- _"Consulte o CNPJ 00.000.000/0001-91 e me diga quem sao os socios"_
- _"Qual a situacao cadastral da empresa com CNPJ 11.222.333/0001-81?"_
- _"Essa empresa esta ativa ou baixada?"_

**Notas fiscais:**
- _"Valide a chave de NFe 35240300623904000197550010000012341234567890 e me explique o que ela representa"_
- _"De qual estado veio essa nota? Quem e o emitente?"_
- _"A SEFAZ de SP esta operacional agora?"_
- _"Qual o status do webservice de emissao de NFe no Rio de Janeiro?"_

**Simples Nacional e regime tributario:**
- _"Verifique se a empresa com CNPJ 12.345.678/0001-90 e optante do Simples Nacional"_
- _"Essa empresa e MEI? Quando entrou no Simples?"_

**CPF e validacoes:**
- _"O CPF 123.456.789-09 e valido?"_
- _"Valide esse CPF: 00000000000"_

**SPED e obrigacoes acessorias:**
- _"Analise esse arquivo SPED e me diga quais registros estao presentes"_
- _"Liste todos os registros C100 do meu arquivo EFD-ICMS"_
- _"Tem algum erro de estrutura nesse SPED?"_

**eSocial:**
- _"Quais eventos do eSocial pertencem ao grupo 'Nao Periodicos'?"_
- _"Esse XML de evento eSocial tem a estrutura correta?"_

**Certidoes:**
- _"Como emito a CND para o CNPJ 12.345.678/0001-90?"_
- _"Onde consulto a Certidao de Regularidade do FGTS dessa empresa?"_

---

## Arquitetura

```
mcp-fiscal-brasil
├── server.py              - Servidor FastMCP, registro de ferramentas
├── cnpj/                  - Consulta Receita Federal via BrasilAPI / ReceitaWS
├── cpf/                   - Validacao matematica offline
├── nfe/                   - Consulta SEFAZ + validacao de chaves
├── nfse/                  - Orientacao por municipio
├── simples/               - Optante Simples Nacional / MEI
├── sped/                  - Parser de arquivos pipe-delimitados
├── esocial/               - Catalogo de eventos + validacao XML
├── certidoes/             - Links e orientacoes CND/CRF
└── shared/                - Validators, schemas, exceptions, constants
```

**Fontes de dados:**
- [BrasilAPI](https://brasilapi.com.br) - CNPJ, CEP, bancos
- [ReceitaWS](https://www.receitaws.com.br) - CNPJ (fallback)
- SEFAZ estaduais - Status de servico e consulta de NFe
- Receita Federal - Simples Nacional, certidoes (orientacao de acesso)

---

## Variaveis de Ambiente

Todas as variaveis sao opcionais. O servidor funciona sem nenhuma configuracao.

| Variavel | Descricao | Padrao |
|----------|-----------|--------|
| `MCP_FISCAL_LOG_LEVEL` | Nivel de log (`DEBUG`, `INFO`, `WARNING`) | `INFO` |
| `BRASILAPI_BASE_URL` | URL base da BrasilAPI (para ambientes customizados) | `https://brasilapi.com.br/api` |
| `HTTP_TIMEOUT` | Timeout em segundos para chamadas HTTP | `30` |

---

## Desenvolvimento

### Requisitos

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recomendado) ou pip

### Setup

```bash
# Clone o repositorio
git clone https://github.com/nikolasdehor/mcp-fiscal-brasil.git
cd mcp-fiscal-brasil

# Instale dependencias de desenvolvimento
pip install -e ".[dev]"

# Instale pre-commit hooks
pre-commit install
```

### Testes

```bash
# Rodar todos os testes
pytest

# Com cobertura
pytest --cov=mcp_fiscal_brasil

# Testes de um modulo especifico
pytest tests/test_cnpj.py -v
```

### Linting e formatacao

```bash
# Verificar codigo
ruff check src/

# Formatar
ruff format src/

# Verificar tipos
mypy src/
```

### Estrutura de um novo modulo

Cada modulo segue o padrao:

```
modulo/
├── __init__.py
├── client.py    - Chamadas HTTP para APIs externas
├── schemas.py   - Modelos Pydantic de request/response
└── tools.py     - Funcoes chamadas pelo servidor MCP
```

---

## Roadmap

| Versao | Status | O que traz |
|--------|--------|-----------|
| **v0.1** | ✅ Lancado | Consultas read-only: CNPJ, CPF, NFe, NFSe, Simples Nacional, SPED, eSocial, Certidoes |
| **v0.2** | Planejado | NFSe completo (municipios principais), SPED layouts detalhados, Certidoes automatizadas |
| **v0.3** | Planejado | Emissao de NFe/NFSe (operacoes de escrita), integracao com certificado digital A1/A3 |
| **v1.0** | Futuro | eSocial completo, auditoria LGPD, suite de compliance fiscal full |

---

## Contribuindo

Contribuicoes sao muito bem-vindas! Para contribuir:

1. Fork o repositorio
2. Crie sua branch: `git checkout -b feature/meu-recurso`
3. Implemente e adicione testes
4. Rode `ruff check` e `mypy` antes de commitar
5. Abra um Pull Request descrevendo o que foi feito

Para bugs e sugestoes, abra uma [issue](https://github.com/nikolasdehor/mcp-fiscal-brasil/issues).

---

## Licenca

MIT - veja [LICENSE](LICENSE) para detalhes.

---

<p align="center">Feito com amor para o Brasil 🇧🇷</p>
<p align="center"><a href="https://github.com/nikolasdehor/mcp-fiscal-brasil/graphs/contributors">Contribuidores</a></p>
