import duckdb
import time
import numpy as np
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from typing import Annotated
from pydantic import BaseModel, Field
from fastapi_mcp import FastApiMCP
import geopandas as gpd
import pandas as pd
import geojson
import folium
from folium import LayerControl
import subprocess
import os

def carregar_queries(caminho: str = "../queries.sql"):
    queries: dict = {}
    nome_atual: None = None
    linhas_comando: list = []

    with open(caminho, "r", encoding="utf-8") as f:
        for linha in f:
            if linha.startswith("-- name:"):
                if nome_atual:
                    queries[nome_atual] = "".join(linhas_comando).strip()
                nome_atual = linha.replace("-- name:", "").strip()
                linhas_comando = []
            elif nome_atual:
                linhas_comando.append(linha)

        if nome_atual:
            queries[nome_atual] = "".join(linhas_comando).strip()

    return queries


QUERIES = carregar_queries()

con = duckdb.connect("dados_estacaos.duckdb")
con.sql("INSTALL spatial")
con.sql("LOAD spatial")

# Tratamento de dados espaciais

# con.install_extension("spatial")
# con.load_extension("spatial")
# con.install_extension("aws")
# con.load_extension("aws")

app = FastAPI(
    title="Minha API com DuckDB",
    summary="Dados retirados do banco de dados do DuckDB serão demonstrados a seguir",
)

con.execute(
    "CREATE TABLE IF NOT EXISTS data_0 as SELECT * FROM read_parquet('../dadosSimepar/data_0.parquet');"
)

con.execute(
    "CREATE TABLE IF NOT EXISTS estacao as SELECT * FROM read_parquet('../dadosSimepar/estacao.parquet');"
)

con.execute(
    "CREATE TABLE IF NOT EXISTS operacao as SELECT * FROM read_parquet('../dadosSimepar/operacao.parquet');"
)

con.execute(
    "CREATE TABLE IF NOT EXISTS orgao as SELECT * FROM read_parquet('../dadosSimepar/orgao.parquet');"
)

con.execute(
    "CREATE TABLE IF NOT EXISTS qualidade as SELECT * FROM read_parquet('../dadosSimepar/qualidade.parquet');"
)

con.execute(
    "CREATE TABLE IF NOT EXISTS sensor as SELECT * FROM read_parquet('../dadosSimepar/sensor.parquet');"
)

con.execute(
    "CREATE TABLE IF NOT EXISTS tipo_coleta as SELECT * FROM read_parquet('../dadosSimepar/tipo_coleta.parquet');"
)

con.execute(
    "CREATE TABLE IF NOT EXISTS tipo_estacao as SELECT * FROM read_parquet('../dadosSimepar/tipo_estacao.parquet');"
)

con.execute(
    "CREATE TABLE IF NOT EXISTS unidade_medida as SELECT * FROM read_parquet('../dadosSimepar/unidade_medida.parquet');"
)
con.execute(
    "CREATE TABLE IF NOT EXISTS areaDesconhecida as SELECT * FROM read_parquet('/home/vitor.oliveira/Downloads/estudo/git-demo/dadosSimepar/dadosRaios/ano=2025/*/*/*.parquet')"
)

# con.execute("CREATE INDEX IF NOT EXISTS s_idx ON data_0 (sensor_id)").df()


class Info(BaseModel):
    model_config = {"extra": "forbid"}

    estacao_id: bool = Field(description="listar por ID da estação", default=None)
    sensor_id: bool = Field(description="listar por ID do sensor", default=None)
    # qualidade_id: bool = Field(description="listar por ID da qualidade", default=None)


@app.get("/filtros", operation_id="filtros")
async def filtro_de_dados_geral(
    filtroHorario: Annotated[
        str | None, Query(description="Exemplo de entrada válida: 07:40-08:30")
    ] = None,
    filtroSensor: Annotated[
        str | None, Query(description="Exemplo de entrada válida: tmax")
    ] = None,
    filtroEstacao: Annotated[
        int | None, Query(description="Exemplo de entrada válida: 25424926")
    ] = None,
):

    cur_time = time.time()

    filtros = []

    con.execute("CREATE OR REPLACE TABLE dados as SELECT * FROM data_0;")

    print(f"tempo inicial: {(time.time() - cur_time)}")

    if filtroHorario is not None:
        try:
            intervalo = filtroHorario.split("-")

            filtroHorario1 = intervalo[0]
            filtroHorario2 = intervalo[1]
            hora = con.execute(QUERIES["hora"], [filtroHorario1]).df()
            hora = con.execute(QUERIES["hora"], [filtroHorario2]).df()

            print(f"{intervalo} {filtroHorario1} {filtroHorario2}")

            con.execute(
                QUERIES["hora_dados_filtro"], [filtroHorario1, filtroHorario2]
            ).df()

            hora.replace({np.nan: None}, inplace=True)
            filtros += [{"data_hora": intervalo}]
        except Exception as e:
            print(e)
            return "formatos esperado:|  HH:MM-HH:MM  |  HH:MM:SS-HH:MM:SS  |"

    if filtroSensor is not None:
        sensor = con.execute(QUERIES["sensor"], [filtroSensor, filtroSensor]).df()

        if sensor.empty:
            return "Nenhum sensor com o nome curto fornecido"

        con.execute(QUERIES["sensor_dados_filtro"], [filtroSensor]).df()

        sensor.replace({np.nan: None}, inplace=True)
        filtros += sensor.to_dict("records")

    if filtroEstacao is not None:
        estacao = con.execute(QUERIES["estacao"], [filtroEstacao]).df()

        if estacao.empty:
            return "Nenhuma estação com o id fornecido"

        con.execute(QUERIES["estacao_dados_filtro"], [filtroEstacao]).df()

        estacao.replace({np.nan: None}, inplace=True)
        filtros += estacao.to_dict("records")

    tabelaAux = con.execute(QUERIES["dados_filtrados"])

    dfColunas = con.execute(
        "SELECT column_name FROM information_schema.columns WHERE table_name = 'dadosFiltro'"
    ).df()
    colunas_permitidas = set(dfColunas["column_name"])
    lista_chaves = set().union(*filtros)
    lista_chaves.discard("data_hora")

    chaves_validadas = lista_chaves & colunas_permitidas

    colunas = ", ".join(chaves_validadas)

    QUERIES["tabela_final"] = f"SELECT * EXCLUDE({colunas}) FROM dadosFiltro"
    tabelaAux = con.execute(QUERIES["tabela_final"]).df()

    tabelaAux.replace({np.nan: None}, inplace=True)

    result = tabelaAux.to_dict("records")

    return (
        {"Filtros:": filtros, "Dados": result}
        if filtros is not None
        else {"Dados": result}
    )


@app.get("/listaEstacoes", operation_id="listar_estacoes")
async def estacoes():
    df = con.execute("SELECT id, nome FROM estacao ORDER BY nome").df()
    df.replace({np.nan: None}, inplace=True)  # Substitui NaN por None
    dados = df.to_dict("records")

    return {"Estações": dados}


@app.get("/listaSensores", operation_id="listar_sensores")
async def sensores():
    df = con.execute("SELECT id, descricao, nome_curto FROM sensor ORDER BY id").df()
    df.replace({np.nan: None}, inplace=True)
    dados = df.to_dict("records")

    return {"Sensores": dados}


@app.get("/infoEstacao", operation_id="info_estacoes")
async def info_estacao(
    id_estacao: Annotated[int | None, Query()] = None,
):

    if id_estacao is None:
        exit
    else:
        estacao = con.execute(QUERIES["estacao"], [id_estacao]).df()

        if estacao.empty:
            return "Nenhuma estação com o id fornecido"

        df = con.execute(QUERIES["estacao_dados"], [id_estacao]).df()

        df.replace({np.nan: None}, inplace=True)  # Substitui NaN por None
        estacao.replace({np.nan: None}, inplace=True)

        estacao = estacao.to_dict("records")
        resultado = df.to_dict("records")

        return {"Estação": estacao, "Dados obtidos": resultado}

    return "nenhum dado fornecido"


@app.get("/infoSensor", operation_id="info_sensores")
async def info_sensor(filtroSensor: Annotated[str, Query()]):

    sensor = con.execute(QUERIES["sensor"], [filtroSensor, filtroSensor]).df()
    if sensor.empty:
        return "Nenhum sensor com o nome curto fornecido"

    sensor = sensor.to_dict("records")

    return {"Sensor:": sensor}

@app.get("/raiosRegiaoPlotagem", operation_id="plotagem_mapa")
async def raios_regiao(id_estacao: Annotated[list[int], Query()]):

    if id_estacao is None:
        exit
    else:
        con.execute(QUERIES["pontos_estacoes"], [id_estacao])
        con.execute(QUERIES["area_raios"], [id_estacao])

        with open("geometria_estacoes.geojson") as f:
            arquivoEstacaoes = geojson.load(f)
        with open("geometria_raios.geojson") as f:
            arquivoRaios = geojson.load(f)

        gdf_raios = gpd.read_file(arquivoRaios)
        gdf_estacoes = gpd.read_file(arquivoEstacaoes)
        


        if gdf_estacoes['geometry'].isna().all():
            return "Nenhuma estação com o id fornecido"
        if gdf_raios['geometry'].isna().all():
            return "Nenhum raio na região selecionada"

        # Mapeamento de cores
        color_map = {
            'Leve': 'yellow',
            'Média': 'red',
            'Alta': 'darkred'
        }

        m = gdf_raios.explore(
            popup=True,
            tooltip=['Data_hora', 'lon', 'lat', 'Precisao_coleta', 'chi_square_value', 'Status_Raio','Intensidade_do_Raio', 'max_rate_of_rise'],
            marker_type='marker',
            marker_kwds=dict(icon=folium.DivIcon(), z_index_offset=100),
            style_kwds=dict(
                style_function=lambda x: {
                    "html": f"""<div style="position: absolute;font-size: 24px; color: {color_map.get(x['properties']['Intensidade_do_Raio'], 'yellow')}; text-shadow: 2px 2px 2px black;">
                        <i class="fa fa-bolt"></i>
                    </div>"""
                }
            ), control_scale=False, overlay=True,
            name="Areas de incidência de raio"
        )
        
        m = gdf_estacoes.explore(
            m=m,
            tooltip=['lon', 'lat', 'estacao_id', 'inicio_operacao', 'fim_operacao', 'nome', 'nome_orgao', 'tipo_coleta', 'tipo_estacao'],
            marker_type='marker',
            marker_kwds=dict(icon=folium.DivIcon(icon_anchor=(48, 48)), z_index_offset=1000),
            style_kwds=dict(
                style_function=lambda x: {
                    "html": f"""<div style="position: absolute;font-size: 96px; color: blue; opacity: 0.7; text-shadow: 2px 2px 2px  black;">
                        <i class="fa fa-satellite-dish"></i>
                    </div>"""
                }
            ),
            name="Estações"
        )
        LayerControl().add_to(m)

        mapa_html = m._repr_html_()

        return HTMLResponse(content=mapa_html)
    return "nenhum dado fornecido"  


@app.get("/raiosRegiaoGeojson", operation_id="raios_geojson")
async def raios_regiao(id_estacao: Annotated[list[int], Query()]):

    if id_estacao is None:
        exit
    else:
        con.execute(QUERIES["pontos_estacoes"], [id_estacao])
        con.execute(QUERIES["area_raios"], [id_estacao])

        with open("geometria_estacoes.geojson") as f:
            arquivoEstacoes = geojson.load(f)
        with open("geometria_raios.geojson") as f:
            arquivoRaios = geojson.load(f)

        if not arquivoEstacoes['features']:
            return "Nenhuma estação com o id fornecido"
        if not arquivoRaios['features']:
            return "Nenhum raio na região selecionada"


        return {"Dados Estações": arquivoEstacoes, "Dados Raios": arquivoRaios}
    
    return "nenhum dado fornecido"  





"""
@app.get("/listaDeDados")
async def bases_em_funcionamento(
    dados_info: Annotated[
        Info, Query(title="Base de dados em execução", description="filtro de dados")
    ],
):

    lista_de_tuplas: list = []
    print(dados_info)
    for dados in dados_info:
        if dados[1]:
            lista_de_tuplas.append(dados)

    info = dict(lista_de_tuplas)

    lista = list(info.keys())
    print(lista)

    if dados_info.estacao_id is True and dados_info.sensor_id is True:
        df = con.execute("SELECT id, nome from estacao UNION SELECT id, descricao, nome_curto FROM sensor").df()
        df.replace({np.nan: None}, inplace=True)  # Substitui NaN por None
        dados = df.to_dict("records")
        return {"União": dados}
    elif dados_info.estacao_id is True:
        df = con.execute("SELECT id, nome FROM estacao ORDER BY nome").df()
        df.replace({np.nan: None}, inplace=True)  # Substitui NaN por None
        dados = df.to_dict("records")
        return {"Estações": dados}
    elif dados_info.sensor_id is True:
        df = con.execute("SELECT id, descricao, nome_curto FROM sensor ORDER BY id").df()
        df.replace({np.nan: None}, inplace=True)
        dados = df.to_dict("records")

        return {"Sensores": dados}

    



    try:
        df = con.execute(
            "SELECT DISTINCT COlUMNS(c -> c IN ?)FROM data_0 ORDER BY ALL", [lista]
        ).df()
    except Exception as e:
        print(e)
        return "Por favor selecionar ao menos um campo para busca"

    resultado = df.to_dict("records")

    return {"dados listados": resultado}
"""

mcp = FastApiMCP(
    app,
    name="Minha API com DuckDB",
    description="Dados retirados do banco de dados do DuckDB serão demonstrados a seguir",
    include_operations=[
        "filtros",
        "listar_estacoes",
        "listar_sensores",
        "info_estacoes",
        "info_sensores",
        "raios_geojson",
        "plotagem_mapa"
    ],
)
mcp.mount_http()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
