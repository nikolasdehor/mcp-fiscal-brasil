<p align="center">
  <img src="assets/banner.svg" width="800" alt="MCP Fiscal Brasil">
</p>

<p align="center">
  <strong>O primeiro servidor MCP para o sistema fiscal brasileiro</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/mcp-fiscal-brasil/"><img src="https://img.shields.io/pypi/v/mcp-fiscal-brasil?color=009c3b&label=PyPI" alt="PyPI version"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10%2B-002776?logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/licenca-MIT-FFDF00?labelColor=002776" alt="License MIT"></a>
  <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-compativel-7c3aed" alt="MCP Compatible"></a>
  <img src="https://img.shields.io/github/stars/nikolasdehor/mcp-fiscal-brasil?style=flat&color=009c3b" alt="Stars">
  <img src="https://img.shields.io/github/issues/nikolasdehor/mcp-fiscal-brasil?color=FFDF00&labelColor=002776" alt="Issues">
</p>

<p align="center">
  <a href="#-instalacao">Instalacao</a> ·
  <a href="#-ferramentas-disponiveis">Ferramentas</a> ·
  <a href="#-demonstracao">Exemplos</a> ·
  <a href="#-roadmap">Roadmap</a> ·
  <a href="#-contribuindo">Contribuindo</a>
</p>

---

## Por que este projeto existe?

O Brasil tem o sistema fiscal mais complexo do mundo. Sao **27 SEFAZs** estaduais, **NFe + NFSe + SPED + eSocial**, cada municipio com seu proprio portal de servicos, e mais de **500 mil PMEs** tentando manter conformidade fiscal todos os dias.

Antes deste projeto, integrar IA com qualquer dado fiscal brasileiro exigia desenvolvimento customizado, autenticacao em multiplos portais, e conhecimento profundo de cada API governamental. Cada consulta era um projeto.

**MCP Fiscal Brasil** resolve isso em uma linha: instale o servidor, conecte ao seu assistente de IA, e comece a fazer perguntas em linguagem natural. O servidor cuida de tudo, consultando diretamente Receita Federal, BrasilAPI e SEFAZs estaduais.

---

## 🎬 Demonstracao

```
Voce:  "Consulte o CNPJ 00.000.000/0001-91 e liste os socios"

IA:    Empresa: Banco do Brasil S.A.
       Fundada em: 12/10/1808
       Situacao: ATIVA
       CNAE principal: 6422100 - Bancos multiplos com carteira comercial

       Socios (QSA):
       - Uniao Federal - Socio-Administrador (60,82%)
       - BNDESPar - Socio (10,32%)
```

```
Voce:  "A chave NFe 35240300623904000197550010000012341234567890 e valida?"

IA:    Chave valida!
       Estado de origem: SP (Sao Paulo)
       Data de emissao: marco/2024
       CNPJ emitente: 00.623.904/0001-97
       Numero da nota: 000001234
       Digito verificador: correto (modulo 11)
```

```
Voce:  "A empresa 12.345.678/0001-90 e do Simples Nacional?"

IA:    Sim! Empresa optante do Simples Nacional.
       Data de opcao: 01/01/2020
       Modalidade: MEI - Microempreendedor Individual
```

```
Voce:  "O SEFAZ de Sao Paulo esta online agora?"

IA:    Status SEFAZ SP: OPERACIONAL
       Servico de autorizacao de NFe funcionando normalmente.
       Ultima verificacao: agora.
```

---

## 🛠 Ferramentas Disponiveis

**14 ferramentas** cobrindo os principais modulos do sistema fiscal brasileiro:

### 🏢 CNPJ
| Ferramenta | O que faz |
|------------|-----------|
| `consultar_cnpj` | Dados cadastrais completos: razao social, endereco, CNAE, socios (QSA), situacao e porte |
| `listar_cnpjs_por_nome` | Busca empresas por nome ou razao social |

### 👤 CPF
| Ferramenta | O que faz |
|------------|-----------|
| `validar_cpf` | Valida digito verificador matematicamente (offline, sem API externa) |

### 📄 NFe - Nota Fiscal Eletronica
| Ferramenta | O que faz |
|------------|-----------|
| `consultar_nfe` | Consulta NFe pela chave de 44 digitos: emitente, destinatario, itens e totais |
| `validar_chave_nfe` | Valida formato e digito verificador; extrai UF, data, CNPJ emitente e numero |
| `consultar_status_sefaz` | Status em tempo real do webservice SEFAZ de qualquer estado |

### 📋 NFSe - Nota Fiscal de Servicos
| Ferramenta | O que faz |
|------------|-----------|
| `consultar_nfse` | Orienta sobre o portal correto para cada municipio |

### 📊 Simples Nacional
| Ferramenta | O que faz |
|------------|-----------|
| `consultar_simples_nacional` | Situacao atual: opcao Simples/MEI, datas de entrada e exclusao |

### 📁 SPED
| Ferramenta | O que faz |
|------------|-----------|
| `analisar_sped` | Analisa arquivo EFD-ICMS/IPI, EFD-Contribuicoes, ECD ou ECF: periodo, empresa e erros |
| `listar_registros_sped` | Extrai todas as ocorrencias de um tipo de registro (ex: C100, E110) |

### 👥 eSocial
| Ferramenta | O que faz |
|------------|-----------|
| `listar_eventos_esocial` | Lista eventos com nome, grupo e descricao; filtravel por grupo |
| `validar_evento_esocial` | Valida estrutura basica de XML: elemento raiz, codigo e versao do leiaute |

### 📜 Certidoes
| Ferramenta | O que faz |
|------------|-----------|
| `consultar_certidao_federal` | URLs e orientacoes para emissao da CND na Receita Federal e PGFN |
| `consultar_certidao_fgts` | URL e orientacoes para consulta da CRF do FGTS na Caixa |

---

## 🚀 Instalacao

Tres linhas para comecar:

```bash
pip install mcp-fiscal-brasil
claude mcp add fiscal-brasil -- mcp-fiscal-brasil
# Pronto! Pergunte ao Claude sobre qualquer empresa brasileira.
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

## ⚙️ Configuracao Detalhada

### Claude Desktop

Edite `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) ou `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "fiscal-brasil": {
      "command": "mcp-fiscal-brasil"
    }
  }
}
```

Reinicie o Claude Desktop. As 14 ferramentas fiscais aparecem automaticamente.

### Claude Code (CLI)

```bash
claude mcp add fiscal-brasil -- mcp-fiscal-brasil
```

### Cursor

Adicione ao `.cursor/mcp.json` do projeto:

```json
{
  "mcpServers": {
    "fiscal-brasil": {
      "command": "mcp-fiscal-brasil"
    }
  }
}
```

### VS Code + Continue

Adicione ao `settings.json`:

```json
{
  "continue.mcpServers": {
    "fiscal-brasil": {
      "command": "mcp-fiscal-brasil"
    }
  }
}
```

### Docker

```bash
docker run --rm -i \
  -e MCP_FISCAL_LOG_LEVEL=INFO \
  ghcr.io/nikolasdehor/mcp-fiscal-brasil:latest
```

---

## 🔑 Variaveis de Ambiente

Todas as variaveis sao opcionais. O servidor funciona sem nenhuma configuracao.

| Variavel | Descricao | Padrao |
|----------|-----------|--------|
| `MCP_FISCAL_LOG_LEVEL` | Nivel de log: `DEBUG`, `INFO`, `WARNING` | `INFO` |
| `BRASILAPI_BASE_URL` | URL base da BrasilAPI (para ambientes customizados) | `https://brasilapi.com.br/api` |
| `HTTP_TIMEOUT` | Timeout em segundos para chamadas HTTP | `30` |

---

## 🏗 Arquitetura

```
Claude / GPT / Cursor / qualquer cliente MCP
           |
           | Model Context Protocol (stdio)
           v
    mcp-fiscal-brasil
           |
    +------+-------+--------+--------+--------+-------+--------+
    |      |       |        |        |        |       |        |
   CNPJ   CPF    NFe      NFSe   Simples    SPED  eSocial Certidoes
    |      |       |        |        |        |       |        |
    v      v       v        v        v        v       v        v
BrasilAPI  --   SEFAZ   Portais   Receita  Parser  Catalogo  URLs
ReceitaWS       estaduais municipais Federal  local   local  governamentais
```

**Fontes de dados:**
- [BrasilAPI](https://brasilapi.com.br) - CNPJ, CEP, bancos (open source, sem autenticacao)
- [ReceitaWS](https://www.receitaws.com.br) - CNPJ (fallback)
- SEFAZs estaduais - Status de servico e consulta de NFe
- Receita Federal - Simples Nacional e certidoes (orientacao de acesso)

---

## 📍 Roadmap

- [x] **v0.1** - Consultas read-only: CNPJ, CPF, NFe, NFSe, Simples Nacional, SPED, eSocial, Certidoes
- [ ] **v0.2** - NFSe completo (municipios principais), SPED layouts detalhados, certidoes automatizadas
- [ ] **v0.3** - Emissao de NFe/NFSe (operacoes de escrita), integracao com certificado digital A1/A3
- [ ] **v1.0** - eSocial completo, auditoria LGPD, suite de compliance fiscal full

---

## 🤝 Contribuindo

Contribuicoes sao bem-vindas!

```bash
# 1. Fork e clone
git clone https://github.com/SEU_USUARIO/mcp-fiscal-brasil.git
cd mcp-fiscal-brasil

# 2. Instale dependencias de desenvolvimento
pip install -e ".[dev]"
pre-commit install

# 3. Crie sua branch
git checkout -b feature/meu-recurso

# 4. Implemente, teste e verifique
pytest
ruff check src/
mypy src/

# 5. Abra um Pull Request
```

Veja as [issues abertas](https://github.com/nikolasdehor/mcp-fiscal-brasil/issues) - especialmente as marcadas com `good first issue`.

Cada modulo segue o padrao `client.py` + `schemas.py` + `tools.py`, o que torna simples adicionar novos modulos fiscais.

---

## 📄 Licenca

MIT - veja [LICENSE](LICENSE) para detalhes.

---

<p align="center">
  Feito com 💚💛 para o Brasil
  <br>
  <sub>Conectando inteligencia artificial ao sistema fiscal mais complexo do mundo</sub>
</p>
