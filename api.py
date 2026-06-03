import os
import duckdb
import glob
import time
import json
from fastapi import FastAPI, Path, Body, UploadFile
from typing import Annotated
from pydantic import BaseModel

def carregar_queries(caminho: str =  "queries.sql"):
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

con = duckdb.connect(':memory:')

app = FastAPI(title="Minha API com DuckDB", summary="Dados retirados do banco de dados do DuckDB serão demonstrados a seguir")

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


'''


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