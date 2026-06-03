-- name: leitura2
SELECT *
FROM read_json(weather,
     format = 'auto');
-- name: gravacao
COPY (
    SELECT * FROM todos3      
    ) TO 'todos7.json';
-- name: descricao
DESCRIBE todos8;

-- name: tabela
CREATE TABLE IF NOT EXISTS testeJson AS
SELECT * FROM 'test.json';

-- name: leitura
SELECT * FROM test;

-- name: teste
CREATE TABLE IF NOT EXISTS weather(
    city    VARCHAR,
    temp_lo INTEGER, -- minimum temperature on a day
    temp_hi INTEGER, -- maximum temperature on a day
    prcp    FLOAT,
    date    DATE
);

-- name: teste2
CREATE TABLE IF NOT EXISTS test(
    titulo VARCHAR,
    conteudo VARCHAR,
    publicado boolean,
    nota INTEGER
);

-- name: teste_l
SELECT *
FROM weather;

-- name: cidades
CREATE TABLE cities (
    name VARCHAR,  
    lat  DECIMAL,
    lon  DECIMAL
);

-- name: inserir
INSERT INTO weather(city, temp_lo, temp_hi, prcp) 
VALUES('Curitiiiba', -2, 18, 1.5);

-- name: inserir2
INSERT INTO test(titulo, conteudo, publicado, nota)
VALUES('Teste', 'Conteúdo de teste', true, 5);

-- name: retorno
SELECT city, (temp_lo + temp_hi)/2 AS temp_avg, prcp, date FROM weather;

-- name: maximo
SELECT MAX(temp_hi)
FROM weather;

-- name: atualiza
UPDATE weather
SET temp_hi = temp_hi + 5;

-- name: deletar
DELETE FROM weather
where temp_hi = 18;

-- name: inserir_tabela
INSERT INTO test (titulo, conteudo, publicado, nota) VALUES(?, ?, ?, ?);

-- name: backup
CREATE TABLE test AS SELECT * FROM 'backup.parquet';

-- name: descrever
DESCRIBE SELECT * FROM read_csv("Sales_Product_Combined.csv");

-- name: testes
SELECT stats_min,stats_max FROM parquet_metadata('backup.parquet');