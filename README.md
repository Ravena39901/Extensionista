# API de Normalização de Viagens

API desenvolvida com **FastAPI** para identificar e normalizar diferentes formatos de viagens de empresas de transporte.

## Tecnologias

* Python 3.13
* FastAPI
* Pytest
* Uvicorn
* Pydantic

## Instalação

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Execução

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Documentação:

```text
http://127.0.0.1:8000/docs
```

## API

**POST**

```text
/api/v1/viagens/normalizar
```

Recebe uma lista de viagens e identifica automaticamente o formato de cada companhia pela estrutura do payload.

A resposta possui um formato padronizado, preservando a ordem dos elementos.

## Arquitetura

O projeto utiliza:

* **Adapter:** cada companhia possui seu próprio adaptador.
* **Strategy:** cada adapter implementa a estratégia de identificação e normalização.
* **Registry:** localiza automaticamente o adapter adequado.
* **SOLID/OOP:** responsabilidades separadas, baixo acoplamento e uso de abstrações.

Companhias suportadas:

* Progresso
* Rota Transportes
* Gontijo
* Sertão Bus

A seleção das companhias não utiliza `if/elif` ou `match/case`.

## Validações e erros

São validados campos obrigatórios, datas, duração, preço, categoria, UF e quantidade de assentos.

Dados inválidos retornam:

```text
HTTP 422
```

com informações sobre o índice, companhia, campo e mensagem de erro.

Não são retornados resultados parciais.

## Extensibilidade

Para adicionar uma nova companhia:

1. Criar um novo adapter em `app/adapters/`.
2. Implementar `CompanyAdapter`.
3. Implementar `can_handle()` e `normalize()`.
4. Registrar o novo adapter no `IntegrationRegistry`.

O fluxo principal da API não precisa ser alterado.

## Testes

Executar:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Resultado atual:

```text
6 passed
```

Os testes verificam normalização, identificação de formatos, validações, erros e preservação da ordem.

## Organização

```text
app/
├── adapters/
├── api/
├── domain/
├── factories/
├── services/
└── main.py

examples/
tests/
requirements.txt
README.md
```
