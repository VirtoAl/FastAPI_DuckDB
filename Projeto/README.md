# Prova de conceito FastAPI, FastMCP, DuckDB, Docker, Docker Compose

#### Objetivo da Prova de conceito: Criar uma API RESTful cujo objetivo é analisar e fatorar os dados coletados pelas estações da Simepar para uma busca mais organizada e menos custosa o qual um agente de IA possa se comunicar com o servidor MCP, utilizar as tool com base nos endpoints da API, e retornar de forma eficiente ao usuário as diversas informações contidas na base de dados

#### Foram utilizadas as seguintes tecnologias para a realização do projeto

## FastAPI

#### Tecnologia solicitada para o desenvolvimento da API visto sua integração inerte com o python na utilização de type hints, como fácil visualização de implementação de funcionalidades utilizando o Swagger UI na porta do host local <http://127.0.0.1:8000/docs>

#### Os seguintes endpoints foram criados para a sumarização dos dados presente no Banco de Dados

<img width="1440" height="824" alt="FastAPI" src="https://github.com/user-attachments/assets/a6d346c8-4ea2-455f-ba66-1c7e0df398a0" />

#### Conforme a demanda, foi implementado

- Endpoint que busca os dados por meio de filtros de horário, nome curto do sensor, e id da estação.
- Endpoint que retorna arquivo GeoJson para os dados de raios.

#### Adicionalmente, foi implementado

- Endpoints que listam os dados de maneira compactada
- Endpoints que retornam todas as informações correlatadas ao objeto de interesse de um componente em específico.
- Endpoint que retorna um mapa interativo sobre os dados de raios na região de uma estação especificada.

#### Explicação detalhada de cada endpoint e seu propósito

- `/filtros` solicita 3 parâmetros de query [horário, nome curto do sensor, id da estação] e retorna os dados coletados filtrados pela solicitação da querry
- `listaEstacoes` retorna sem necessidade de parametrização a lista de todas as estações, fornecendo como resposta um Json com as informações de [id, nome, latitude, longitude]
- `listaSensores` retorna sem necessidade de parametrização a lista de todos os sensores, fornecendo como resposta um Json com as informações de [id, descricao, nome_curto]
- `infoEstacao` solicita 1 parâmetro de query [id_estacao] e retorna todas as informações da estação fornecida
- `infoSensor` solicita 1 parâmetro de query [nome_curto] e retorna todos as informações do sensor fornecido

<img width="1472" height="768" alt="estacoesRaios" src="https://github.com/user-attachments/assets/d0291c2e-9a0b-405a-938d-6de8338150b8" />

- `raiosRegiaoPlotagem` solicita 3 parâmetros de query [lista[id_estacao], data_inicio, data_fim] para plotar num mapa as informações dentro da área da estação [número de raios na região, média de intensidade, raio mais intenso, média de precisão] e informações de cada raio [lat, lon, Precisao da coleta, Chi_square_value, status do raio, intensidade do raio, max_rate_of_rise] de incidência na região das estações fornecidas.
- `raiosRegiaoGeojson` solicita os mesmos parâmetros e retorna as mesmas informações, porém num arquivo Geojson.
  
#### Vale notar que os dados de coleta de raio são todos exclusivamente referentes ao ano de 2025, e os dados de coleta gerais são referente ao período do dia 31/05/2026 à 11/06/2026

---

## Docker / Docker Compose

Para o teste unitário foi utilizado o Docker como tecnologia visto sua capacidade de empacotar, isolar e executar aplicativos em ambiente chamados contêiner.

de acordo com as propriedades ditas do docker, foi utilizado no Dockerfile `RUN curl -fsSL https://cli.devin.ai/install.sh | bash || true` para a instalação do agente de IA Devin CLI dentro da imagem visto que não há nenhuma imagem oficial da Cognition para a implementação por pull da imagem

A imagem docker está disponível para pull pelo DockerHub no seguinte diretório

<https://hub.docker.com/r/virtoal/fastapi-simepar>

Para a realização adequada do Contêiner, é necessário especificar no `docker-compose.yml` as seguintes especificações
```
services:
  api:
    image: virtoal/fastapi-simepar:1.0.3
    container_name: nome-do-container
    ports:
      - "8000:8000"
    volumes:
      - ./dados_estacao.duckdb:/app/dados_estacao.duckdb
```

Vale salientar que os dados utilizados estão localizados na máquina para fim de testes. Para a implementação completa do banco de dados seria necessário acesso ao AWS e referenciar ao volume `/app/dados_estacao.duckdb` como mostrado acima.

Com tudo configurado corretamente, utilizar o seguinte comando irá rodar o contêiner com a aplicação

`docker compose up`

E para acesso do agente de IA, será necessário rodar o seguinte comando, o qual será especificado na seção seguinte

`docker exec -it nome-do-container bash`

---

## FastMCP

Tecnologia utilizada para a criação do servidor MCP visto que é o principal framework para desenvolvimento em Python. Utilizando da biblioteca `from fastapi_mcp import FastApiMCP` que integra as duas tecnologias a deixar o desenvolvimento mais simplificada

Devin CLI foi utilizado como agente de IA para os testes do servidor MCP, configurado para atuar na porta 8000/mcp da aplicação.
Os endpoints foram desenvolvidos com respostas "repetitivas" para que dependendo da solicitação do usuário, o cliente da porta mcp saiba qual tool utilizar sem a necessidade de percorrer por todo o banco de dados instanciado pelo DuckDB

Para fazer o uso do Devin CLI dentro do container de maneira apropriada, após rodar o container da API, deve se utilizar o comando `docker exec -it nome_do_container bash` para abrir a linha de comando dentro do container, e conseguir utilizar da pre-configuração vinda junta com a imagem personalizada ao Devin Cli.

Após a entrada na linha de comando, apenas digite `devin`, que irá solicitar seu token de autenticação pessoal para uso próprio, basta seguir as instruções fornecidas pelo próprio Devin CLI. Após isto, o devin já estará conectado com o servidor MCP pronto para uso.

Recomendação de primeiro prompt: 

`Me forneça uma visão geral do que a aplicação é capaz de fazer`

---

## DuckDB

Base de dados a ser instanciada pela aplicação, permitindo buscas e manipulação a partir de querys SQL de maneira rápida e eficaz por conta de sua estrutura colunar, sendo uma opção desejada para uma aplicação cujo objetivo é filtrar milhares de dados arquivos .parquet

#### Conforme a demanda

foi utilizado operações query do tipo `JOIN` visto o objetivo de sumarização dos dados, aonde a concatenação de dados .parquet se mostra necessária para visualização dos dados de maneira organizada para o uso do usuário na API.

Foi utilizada suas funções padrões para a maior parte das queries sql, como também da biblioteca SPATIAL para manipulação de dados geográficos. É visto nos endpoints `raiosRegiaoPlotagem`, e `raiosRegiaoGeojson`, com a criação da área de instância de raios ao redor da estação, como na filtragem para os raios que estão somente dentro da região da estação específicada serem contabilizados, e instanciados pelo mapa interativo, ou, pelo arquivo Geojson
