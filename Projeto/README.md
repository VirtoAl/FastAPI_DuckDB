# Prova de conceito FastAPI, FastMCP, DuckDB, Docker

Objetivo da Prova de conceito: Criar uma API RESTful cujo objetivo é analisar e fatorar os dados coletados pelas estações em parceria da Simepar para uma busca mais organizada e menos custosa o qual um agente de IA possa se comunicar com o servidor MCP, utilizar as tool com base nos endpoints da API, e retornar de forma eficiente ao usuário as diversas informações contidas na base de dados.

Foram utilizadas as seguintes tecnologias para a realização do projeto:

## FastAPI

Criação dos endpoints a partir do FastAPI que possuí uma integração inerte com o Python, utilizando de type hints para o desenvolvimento apropriado da aplicação. Configurado para atuar na porta 8000 a aplicação

<img width="1440" height="824" alt="FastAPI" src="https://github.com/user-attachments/assets/a6d346c8-4ea2-455f-ba66-1c7e0df398a0" />

- `/filtros` solicita 3 parâmetros de query [horário, nome curto do sensor, id da estação] e retorna os dados coletados filtrados pela solicitação da querry
- `listaEstacoes` retorna sem necessidade de parametrização a lista de todas as estações, fornecendo como resposta um Json com as informações de [id, nome, latitude, longitude]
- `listaSensores` retorna sem necessidade de parametrização a lista de todos os sensores, fornecendo como resposta um Json com as informações de [id, descricao, nome_curto]
- `infoEstacao` solicita 1 parâmetro de query [id_estacao] e retorna todas as informações da estação fornecida
- `infoSensor` solicita 1 parâmetro de query [nome_curto] e retorna todos as informações do sensor fornecido
- `raiosRegiaoPlotagem` solicita 3 parâmetros de query [lista[id_estacao], data_inicio, data_fim] para plotar num mapa as informações pertinentes de incidência de raios na região das estações fornecidas
- `raiosRegiaoGeojson` solicita 3 parâmetros de query [lista[id_estacao], data_inicio, data_fim] fornecendo como resposta um GeoJson contendo as informações pertinentes de incidência de raios na região das estações fornecidas
  
Os endpoints foram desenvolvidos de tal maneira para facilitar a busca do agente de IA que será descrito na próxima seção

---

## FastMCP

Criação das tools do servidor MCP partir do FastMCP utilizando da biblioteca `from fastapi_mcp import FastApiMCP` que integra as duas tecnologias a deixar o desenvolvimento mais compreensível

Devin CLI foi utilizado como agente de IA para os testes do servidor MCP, configurado para atuar na porta 8000/mcp da aplicação.
Os endpoints foram desenvolvidos com respostas "repetitivas" para que dependendo da solicitação do usuário, o cliente saber qual tool utilizar sem a necessidade de percorrer por todo o banco de dados instanciado pelo DuckDB que será descrito da próxima seção

---

## DuckDB

Base de dados a ser instanciada pela aplicação por sua estrutura colunar, permitindo buscas e manipulção a partir de querys SQL, sendo uma opção desejada para uma aplicação cujo objetivo é filtrar base de dados com milhares de dados que continuam a ser atualizados constantemente.


