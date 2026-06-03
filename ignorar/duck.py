import duckdb
import pandas as pd
import glob
import time

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

conn = duckdb.connect("teste.db")


#df = conn.sql(QUERIES["inserir"])
#df = conn.sql(QUERIES["teste"])
#df = conn.sql(QUERIES["teste_l"])
#df = conn.sql(QUERIES["cidades"])
#df = conn.sql(QUERIES["retorno"])
#df = conn.sql(QUERIES["maximo"])
#df = conn.sql(QUERIES["atualiza"])
#df = conn.sql(QUERIES["deletar"])

#conn.sql(QUERIES["tabela"])

#df = conn.execute(QUERIES["leitura2"]).df()


#DROP TABLE nometabela;

#print(f"time: {(time.time() - cur_time)}")
#print(df)

#df = conn.sql(QUERIES["descricao"])
#print(df)







#df = pd.concat([pd.read_csv(f) for f in glob.glob('*.csv')])

#print(df.head(10))
cur_time = time.time()
print(f"timessss: {(time.time() - cur_time)}")
df = conn.sql("""
    SELECT *
    FROM read_csv_auto('*.csv', header=True)
""")

df = conn.execute(QUERIES["testes"]).df()

print(f"timessss: {(time.time() - cur_time)}")


print(df)



#Leitura do json
#df = conn.sql(QUERIES["leitura"])

#conn.sql("SELECT 42 AS x").show()

#cria um json com base nos dados de todos3

#df = conn.sql(QUERIES["gravacao"])

#df = conn.sql(QUERIES["descricao"])


# descrição da tabela 

#df = conn.sql(QUERIES["tabela"])
'''

# criação de uma tabela pelo json
df = conn.sql("""


""")
# leitura de um json
df = conn.sql("""
    SELECT *
    FROM read_json('test.json',
               format = 'auto');
"""
)

df = conn.execute("""
    SELECT * 
    FROM 'test.json', format = 'array';
"""
).df()


'''

