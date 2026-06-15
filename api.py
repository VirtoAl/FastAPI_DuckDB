import duckdb
import numpy as np
from fastapi import FastAPI, Query
from typing import Annotated
from pydantic import BaseModel, Field


def carregar_queries(caminho: str = "queries.sql"):
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

con = duckdb.connect(":memory:")

app = FastAPI(
    title="Minha API com DuckDB",
    summary="Dados retirados do banco de dados do DuckDB serão demonstrados a seguir",
)

con.execute(
    "CREATE TABLE IF NOT EXISTS data_0 as SELECT * FROM read_parquet('reatividadedeestgioduckdb/data_0.parquet');"
)

con.execute(
    "CREATE TABLE IF NOT EXISTS estacao as SELECT * FROM read_parquet('reatividadedeestgioduckdb/estacao.parquet');"
)

con.execute(
    "CREATE TABLE IF NOT EXISTS operacao as SELECT * FROM read_parquet('reatividadedeestgioduckdb/operacao.parquet');"
)

con.execute(
    "CREATE TABLE IF NOT EXISTS orgao as SELECT * FROM read_parquet('reatividadedeestgioduckdb/orgao.parquet');"
)

con.execute(
    "CREATE TABLE IF NOT EXISTS qualidade as SELECT * FROM read_parquet('reatividadedeestgioduckdb/qualidade.parquet');"
)

con.execute(
    "CREATE TABLE IF NOT EXISTS sensor as SELECT * FROM read_parquet('reatividadedeestgioduckdb/sensor.parquet');"
)

con.execute(
    "CREATE TABLE IF NOT EXISTS tipo_coleta as SELECT * FROM read_parquet('reatividadedeestgioduckdb/tipo_coleta.parquet');"
)

con.execute(
    "CREATE TABLE IF NOT EXISTS tipo_estacao as SELECT * FROM read_parquet('reatividadedeestgioduckdb/tipo_estacao.parquet');"
)

con.execute(
    "CREATE TABLE IF NOT EXISTS unidade_medida as SELECT * FROM read_parquet('reatividadedeestgioduckdb/unidade_medida.parquet');"
)

# con.execute("CREATE INDEX IF NOT EXISTS s_idx ON data_0 (sensor_id)").df()


class Filtro(BaseModel):
    model_config = {"extra": "forbid"}

    data_hora: bool = Field(description="listar por data e hora", default=None)
    estacao_id: bool = Field(description="listar por ID da estação", default=None)
    sensor_id: bool = Field(description="listar por ID do sensor", default=None)
    qualidade_id: bool = Field(description="listar por ID da qualidade", default=None)


@app.get("/filtros")
async def filtro_de_dados_geral(
    filtroHorario: Annotated[str | None, Query(description="Exemplo de entrada válida: 07:40-08:30")] = None,
    filtroSensor: Annotated[str | None, Query(description="Exemplo de entrada válida: tmax")] = None,
    filtroEstacao: Annotated[int | None, Query(description="Exemplo de entrada válida: 25424926")] = None,
):


    filtros = []


    df = con.execute("CREATE OR REPLACE TABLE dados as SELECT * FROM data_0;")

    

    if filtroHorario is None:
        exit
    else:
        try:

            

            intervalo = filtroHorario.split("-")

            filtroHorario1 = intervalo[0]
            filtroHorario2 = intervalo[1]
            hora = con.execute(QUERIES["hora"], [filtroHorario1]).df()
            hora = con.execute(QUERIES["hora"], [filtroHorario2]).df()

            print(f'{intervalo} {filtroHorario1} {filtroHorario2}')

            
            con.execute(QUERIES["hora_dados_filtro"], [filtroHorario1, filtroHorario2]).df()
            
   
            hora.replace({np.nan: None}, inplace=True)
            filtros += [{"data_hora": intervalo}]
        except Exception as e:
            print(e)
            return "formatos esperado:|  HH:MM-HH:MM  |  HH:MM:SS-HH:MM:SS  |" 

    if filtroSensor is None:
        exit
    else:

        sensor = con.execute(QUERIES["sensor"], [filtroSensor]).df()

        if sensor.empty:
            return "Nenhum sensor com o nome curto fornecido"

        con.execute(QUERIES["sensor_dados_filtro"], [filtroSensor]).df()

        sensor.replace({np.nan: None}, inplace=True)
        filtros += sensor.to_dict("records")

    if filtroEstacao is None:
        exit
    else:
        estacao = con.execute(QUERIES["estacao"], [filtroEstacao]).df()

        if estacao.empty:
            return "Nenhuma estação com o id fornecido"

        con.execute(QUERIES["estacao_dados_filtro"], [filtroEstacao]).df()

        estacao.replace({np.nan: None}, inplace=True)
        filtros += estacao.to_dict("records")

    tabelaAux = con.execute(QUERIES["dados_filtrados"])

    lista_chaves = set().union(*filtros)
    lista_chaves.discard("data_hora")
    colunas = ", ".join(lista_chaves)

    tabelaAux = con.execute(f"SELECT * EXCLUDE({colunas}) FROM dadosFiltro").df()


    tabelaAux.replace({np.nan: None}, inplace=True)

    result = tabelaAux.to_dict("records")

    return (
        {"filtros:": filtros, "dados": result} if filtros is not None else {"dados": result}
    )


@app.get("/dadosBrutos")
async def estacoes():
    df = con.execute("SELECT id, nome FROM estacao ORDER BY nome").df()
    df.replace({np.nan: None}, inplace=True)  # Substitui NaN por None
    dados = df.to_dict("records")

    return dados


@app.get("/listaDeDados")
async def bases_em_funcionamento(
    dados_filtro: Annotated[
        Filtro, Query(title="Base de dados em execução", description="filtro de dados")
    ],
):

    lista_de_tuplas: list = []

    for dados in dados_filtro:
        if dados[1]:
            lista_de_tuplas.append(dados)

    info = dict(lista_de_tuplas)

    lista = list(info.keys())
    print(lista)

    try:
        df = con.execute(
            "SELECT DISTINCT COlUMNS(c -> c IN ?)FROM data_0 ORDER BY ALL", [lista]
        ).df()
    except Exception as e:
        print(e)
        return "Por favor selecionar ao menos um campo para busca"

    resultado = df.to_dict("records")

    return {"dados listados": resultado}


@app.get("/filtroEstacao")
async def filtro_de_dados_por_estacao(
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


@app.get("/filtroHora")
async def filtro_de_dados_por_horario(datahora: Annotated[str, Query()]):

    try:
        df = con.execute(
            "SELECT data_hora FROM data_0  WHERE data_hora::TIMETZ = ?::TIMETZ LIMIT 1",
            [datahora],
        ).df()
    except Exception as e:
        print(e)
        return "formatos esperado:|  HH:MM  |  HH:MM:SS  |  HH:MM:SS-TT[:tt]  |"

    df = df.to_dict("records")

    return df


@app.get("/filtroSensor")
async def filtro_de_dados_por_sensor(filtroSensor: Annotated[str, Query()]):

    sensor = con.execute(QUERIES["sensor"], [filtroSensor]).df()
    if sensor.empty:
        return "Nenhum sensor com o nome curto fornecido"

    resultado = con.execute(QUERIES["sensor_dados"], [filtroSensor]).df()

    resultado.replace({np.nan: None}, inplace=True)

    sensor = sensor.to_dict("records")
    resultado = resultado.to_dict("records")

    return {"Sensor:": sensor, "Dados obtidos": resultado}


# @app.get("/estacoes/{id}")
# async def funcao(id: Annotated[int, Path()]):

#     df = con.execute("SELECT * FROM estacao WHERE id = ?", [id]).df()
#     df.replace({np.nan: None}, inplace=True)  # Substitui NaN por None
#     dados = df.to_dict('records')

#     return dados


# @app.get("/estacoes")
# async def funcao():
#     # DuckDB puro - mais rápido
#     df = con.execute("SELECT * FROM estacao LIMIT 10").df()

#     #colunas = [desc[0] for desc in con.description]
#     #dados = [dict(zip(colunas, row)) for row in resultado]
#     df.replace({np.nan: None}, inplace=True)  # Substitui NaN por None

#     dados = df.to_dict('records')

#     return dados


'''

# Carrega dados do parquet se existir, senão cria tabela vazia

if os.path.exists('backup.parquet'):
    try:
        df = con.execute(QUERIES["backup"])
        print("✓ Dados carregados do backup.parquet")
    except Exception as e:
        print(f"✗ Erro ao carregar backup.parquet: {e}")
else:
    # Se não existir backup, cria tabela vazia
    df = con.sql(QUERIES["teste2"])
    print("✓ Tabela test criada vazia")




class usuario(BaseModel):
    titulo: str
    conteudo: str
    publicado: bool
    nota: int


@app.get("/dados")
async def dados():

    result = con.sql(QUERIES["leitura"]).fetchall()
    return {"teste": result}


@app.post("/dados")
async def dados(file: UploadFile):
    # Leitura do dado json
    conteudo = await file.read()
    json_data = json.loads(conteudo)
    
    # Converte para objetos usuario
    usuarios = [usuario(**item) for item in (json_data if isinstance(json_data, list) else [json_data])]
    
    # Inserção de dados na tabela
    for item in usuarios:
        con.execute(
            QUERIES["inserir_tabela"], 
            (item.titulo, item.conteudo, item.publicado, item.nota)
        )
    
    return {"sucesso": True, "items_inseridos": len(usuarios)}



@app.post("/files/")
async def create_file():
    # Salva dados em Parquet (no disco)
    con.sql("COPY test TO 'backup.parquet'(FORMAT parquet);")
    
    # Também salva em JSON
    df = con.sql("SELECT * FROM test").df()
    dados = df.to_dict('records')
    
    with open('dados_exportados.json', 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    
    return {
        "sucesso": True, 
        "arquivo_parquet": "backup.parquet",
        "arquivo_json": "dados_exportados.json",
        "registros": len(dados)
    }


@app.get("/teste")
async def teste():
    
 
    con.execute("INSERT INTO empregados VALUES(1, 'Vitor', 1500), (2, 'Eu', 29292)")

    df = con.execute("SELECT * FROM empregados").fetchall()
    return{"emprego": df}




# Defining the patient model
class Patient(BaseModel):
    name: str
    age: int
    gender: str

# Connecting to the DuckDB database
con = duckdb.connect(database=':memory:', read_only=False)

# Creating the patients table
con.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER,
    name TEXT,
    age INTEGER,
    gender TEXT
)
""")

@app.post("/patients/")
def register_patient(patient: Patient):
    con.execute("""
    INSERT INTO patients (name, age, gender) 
    VALUES (?, ?, ?)
    """, (patient.name, patient.age, patient.gender))
    
    return {"message": "Patient successfully registered!"}

@app.get("/patients/")
def list_patients():
    result = con.execute("SELECT * FROM patients").fetchall()
    return {"patients": result}

    try:
    with duckdb.connect('my_database.db') as con:
        con.execute("SELECT 42")
except Exception as e:
    print(f"Connection failed: {e}")
'''
