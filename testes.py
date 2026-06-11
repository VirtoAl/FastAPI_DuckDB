teste: dict = {"ada": 2, "sdasd": 5}

print(teste.keys())

"""
@app.get("/filtroSensor")
async def filtroSensor(filtroSensor: Annotated[str, Query()]):
    

    sensor = con.execute(QUERIES["sensor"], [filtroSensor]).df()
    
    if(sensor.empty):
        return "Nenhum sensor com o nome curto fornecido"
        
    resultado = con.execute(QUERIES["sensorDados"], [filtroSensor]).df()

    resultado.replace({np.nan: None}, inplace=True)
    
    # resultado.replace({np.nan: None}, inplace=True)  # Substitui NaN por None

    sensor = sensor.to_dict('records')
    resultado = resultado.to_dict('records')

    return {"Sensor:": sensor, "Dados obtidos": resultado}





# cur_time = time.time()
# print(f"Tempo antes: {time.time() - cur_time}")


# print(f"Tempo para criar tabela: {(time.time() - cur_time)} segundos")

# meu_timestamp = datetime.now().timestamp()

# df = con.execute("SELECT data_hora FROM data_0 WHERE data_hora = '2026-06-05 T12:11:00-03:00' LIMIT 10").df()
# print(df)

-- name: sensor
SELECT sensor.id, sensor.descricao, sensor.nome_curto, unidade_medida.sigla as unidade_medida, unidade_medida.descricao as descricao_da_medida, operacao.funcao as operacao 
FROM sensor LEFT JOIN unidade_medida on sensor.unidade_medida_id = unidade_medida.id
LEFT JOIN operacao on sensor.classificacao_id = operacao.id
WHERE sensor.nome_curto = ?;

try:
    number = int(input("Enter a number: "))
except ValueError:
    print("That was not a valid number!")

val




class Person:
    def __init__(self, name: str):
        self.name = name


def get_person_name(one_person: Person):
    return one_person.name


def get_full_name(first_name: str, last_name: str):
    full_name = first_name.title + " " + last_name.title()
    return full_name

#async def hamburbur(burbur: int):
burbur = await 
    



print (get_person_name(Person("Vitor")))
hambur = await hamburbur(2)


import os

nome = os.getenv("MY_NAME", "mundo")
print(f"Ola {nome}")
"""

# from datetime import date

# dia = date.today()

# @classmethod(cls)
# @staticmethod
# @


# print(f"dia: {dia}")
