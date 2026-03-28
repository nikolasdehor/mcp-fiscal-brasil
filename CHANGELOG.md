# Changelog

## [0.1.1] - 2026-03-27

### Added
- 8 modules: CNPJ, CPF, NFe, NFSe, Simples Nacional, SPED, eSocial, Certidoes
- 14 MCP tools for fiscal queries via natural language
- SDK mode: FiscalBrasil class for direct Python integration
- 5 integration examples: basic, FastAPI, Django, batch validation, ERP
- NFe fallback chain: BrasilAPI -> Portal Nacional -> partial key data
- eSocial catalog expanded to 45+ events (S-1.0 complete)
- NFSe coverage expanded to 50+ municipalities (all state capitals + major cities)
- CI/CD: GitHub Actions (lint, test, publish PyPI), Docker, pre-commit
- Published on PyPI: pip install mcp-fiscal-brasil

### Fixed
- XXE vulnerability in xml_utils.py (safe parser with resolve_entities=False)
- Chave NFe validator: weights and direction corrected (SEFAZ spec right-to-left)
- HTTP client: leading slash in paths breaking httpx URLs
- FastMCP: description -> instructions (breaking change v3.1.1)
- datetime.utcnow() deprecated -> datetime.now(timezone.utc)
- 28 ruff lint errors, 5 mypy errors corrected
- Portuguese text review across all 17 source files (~530 corrections)

## [0.1.0] - 2026-03-27

### Added
- Initial release
- Project structure with 41 Python files
- Shared module: HTTP client, rate limiter, validators, XML utils
- Basic tools for all 8 fiscal modules
