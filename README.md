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

**14 ferramentas** cobrindo os principais modulos do sistema fiscal brasileiro.

---

### ✅ Ferramentas Funcionais (usaveis agora)

Funcionam 100% sem chaves de API. Instale e use imediatamente.

| Modulo | Ferramenta | Descricao | API |
|--------|-----------|-----------|-----|
| CNPJ | `consultar_cnpj` | Dados completos: razao social, socios, CNAE, endereco | BrasilAPI (gratis) |
| CNPJ | `consultar_simples_nacional` | Optante Simples/MEI com datas de entrada e exclusao | BrasilAPI (gratis) |
| NFe | `validar_chave_nfe` | Valida digito + extrai UF, CNPJ, data, numero | Offline |
| NFe | `consultar_status_sefaz` | Status do webservice SEFAZ por estado | BrasilAPI (gratis) |
| NFe | `consultar_nfe` | Consulta NFe completa pela chave de 44 digitos | BrasilAPI (gratis) |
| CPF | `validar_cpf` | Validacao de digito verificador | Offline |
| SPED | `analisar_sped` | Analisa arquivo EFD/ECD/ECF: periodo, empresa, erros | Offline |
| SPED | `listar_registros_sped` | Filtra registros por tipo (C100, E110, etc.) | Offline |
| eSocial | `listar_eventos_esocial` | Catalogo de eventos filtravel por grupo | Offline |
| eSocial | `validar_evento_esocial` | Validacao basica de estrutura XML | Offline |

---

### 🧭 Ferramentas de Orientacao

Retornam URLs e instrucoes - exigem acao manual nos portais governamentais.

| Modulo | Ferramenta | O que retorna |
|--------|-----------|--------------|
| NFSe | `consultar_nfse` | URL do portal NFSe do municipio + sistema utilizado |
| Certidoes | `consultar_certidao_federal` | URL do e-CAC para emissao de CND federal |
| Certidoes | `consultar_certidao_fgts` | URL do portal Caixa para consulta do CRF |

---

### 🧪 Ferramentas Experimentais

Requerem APIs pagas ou tem cobertura limitada.

| Modulo | Ferramenta | Limitacao |
|--------|-----------|-----------|
| CNPJ | `listar_cnpjs_por_nome` | Receita Federal nao disponibiliza busca por nome em API publica |

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

- [x] **v0.1.0** - Consultas CNPJ, CPF, NFe, Simples, SPED (atual)
- [ ] **v0.2.0** - NFSe 50+ municipios, eSocial catalogo completo
- [ ] **v0.3.0** - Emissao NFe/NFSe (requer certificado digital A1)
- [ ] **v1.0.0** - eSocial completo, LGPD audit, compliance suite

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
