-- name: estacao
SELECT estacao.id as estacao_id, estacao.nome, estacao.latitude, estacao.longitude, estacao.altitude, orgao.nome as nome_orgao, tipo_estacao.descricao as tipo_estacao, tipo_coleta.descricao as tipo_coleta, estacao.classificacao, estacao.inicio_operacao, estacao.fim_operacao
FROM estacao LEFT JOIN orgao on orgao.id = estacao.orgao_id
LEFT JOIN tipo_estacao on estacao.tipo_estacao_id = tipo_estacao.id 
LEFT JOIN tipo_coleta on estacao.tipo_coleta_id = tipo_coleta.id  
WHERE estacao.id = ?;

-- name: estacao_dados
SELECT data_0.data_hora, sensor.descricao as tipo_sensor, operacao.funcao as operacao_sensor, data_0.valor, unidade_medida.sigla as unidadade_de_medida, qualidade.descricao as nivel_qualidade
FROM data_0 LEFT JOIN sensor on data_0.sensor_id = sensor.id 
LEFT JOIN qualidade ON data_0.qualidade_id = qualidade.id
LEFT JOIN operacao ON sensor.classificacao_id = operacao.id
LEFT JOIN unidade_medida ON sensor.unidade_medida_id = unidade_medida.id
WHERE estacao_id = ?;

-- name: estacao_dados_filtro
DELETE FROM dados WHERE dados.estacao_id != ?; 

-- name: sensor
SELECT sensor.id as sensor_id, sensor.descricao, sensor.nome_curto, unidade_medida.sigla as unidade_medida, unidade_medida.descricao as descricao_da_medida, operacao.funcao as operacao 
FROM sensor LEFT JOIN unidade_medida on sensor.unidade_medida_id = unidade_medida.id
LEFT JOIN operacao on sensor.classificacao_id = operacao.id
WHERE sensor.descricao = ? OR sensor.nome_curto = ?;

-- name: sensor_dados
SELECT data_0.data_hora, estacao.nome as estacao_nome, orgao.nome as nome_orgao, tipo_estacao.descricao as tipo_estacao, tipo_coleta.descricao as tipo_coleta, data_0.valor, qualidade.descricao as nivel_qualidade
FROM data_0 LEFT JOIN estacao on data_0.estacao_id = estacao.id
LEFT JOIN qualidade on data_0.qualidade_id = qualidade.id
LEFT JOIN sensor on data_0.sensor_id = sensor.id
LEFT JOIN orgao on  orgao.id = estacao.orgao_id
LEFT JOIN tipo_estacao on estacao.tipo_estacao_id = tipo_estacao.id
LEFT JOIN tipo_coleta on estacao.tipo_coleta_id = tipo_coleta.id  
WHERE sensor.nome_curto = ? ORDER BY estacao_nome;

-- name: dados
SELECT dados.data_hora, estacao.id as estacao_id, estacao.nome as estacao_nome, sensor.id as sensor_id, sensor.descricao as sensor_descricao,
 dados.valor, unidade_medida.sigla as unidade_de_medida, qualidade.descricao as qualidade
FROM dados LEFT JOIN estacao on dados.estacao_id = estacao.id
LEFT JOIN sensor on dados.sensor_id = sensor.id
LEFT JOIN unidade_medida on sensor.unidade_medida_id = unidade_medida.id
LEFT JOIN qualidade on dados.qualidade_id = qualidade.id
ORDER BY data_hora LIMIT 100;

-- name: dados_filtrados
CREATE OR REPLACE TABLE dadosFiltro as SELECT dados.data_hora, estacao.id as estacao_id, estacao.nome, estacao.latitude, estacao.longitude, estacao.altitude, orgao.nome as nome_orgao, tipo_estacao.descricao as tipo_estacao, tipo_coleta.descricao as tipo_coleta, dados.valor, qualidade.descricao as nivel_qualidade,estacao.classificacao, estacao.inicio_operacao, estacao.fim_operacao, sensor.id as sensor_id, sensor.descricao, sensor.nome_curto, unidade_medida.sigla as unidade_medida, unidade_medida.descricao as descricao_da_medida, operacao.funcao as operacao 
FROM dados LEFT JOIN estacao on dados.estacao_id = estacao.id
LEFT JOIN orgao on orgao.id = estacao.orgao_id
LEFT JOIN tipo_estacao on estacao.tipo_estacao_id = tipo_estacao.id 
LEFT JOIN tipo_coleta on estacao.tipo_coleta_id = tipo_coleta.id  
LEFT JOIN sensor on dados.sensor_id = sensor.id
LEFT JOIN unidade_medida on sensor.unidade_medida_id = unidade_medida.id
LEFT JOIN operacao on sensor.classificacao_id = operacao.id
LEFT JOIN qualidade on dados.qualidade_id = qualidade.id;


-- name: sensor_dados_filtro
DELETE FROM dados USING sensor 
WHERE dados.sensor_id = sensor.id AND sensor.nome_curto != ?;  

-- name: hora_dados_filtro
DELETE FROM dados 
WHERE data_hora::TIMETZ < ?::TIMETZ OR data_hora::TIMETZ > ?::TIMETZ;

-- name: hora
SELECT DISTINCT data_hora FROM dados WHERE data_hora::TIMETZ = ? LIMIT 1;

-- name: delete_sensor
ALTER TABLE dados DROP COLUMN sensor_id;

-- name: raios
COPY (SELECT areaDesconhecida.time_tick as Data_hora, areaDesconhecida.lon, areaDesconhecida.lat, areaDesconhecida.chi_square_value, areaDesconhecida.the_centrogeom::GEOMETRY('EPSG:4618'), max_rate_of_rise,
         CASE
            WHEN chi_square_value <=3 THEN 'Altamente Confiável'
            WHEN chi_square_value >3 AND chi_square_value <=6 THEN 'Mediano'
            ELSE 'Pouco Confiável'
            END AS Precisao_coleta,
         CASE 
            WHEN abs(max_rate_of_rise) <= 10 THEN 'Leve'
            WHEN abs(max_rate_of_rise) > 10 AND abs(max_rate_of_rise) < 25 THEN 'Média'
            ELSE 'Alta'
            END AS Intensidade_do_Raio,
         CASE
            WHEN peak_current <= 0 THEN 'Raio Comum'
            WHEN peak_current > 0 THEN 'Raio Nuvem-a-Nuvem'
            END AS Status_Raio
         FROM estacao LEFT JOIN areaDesconhecida ON ST_Contains(ST_Buffer(ST_Point(estacao.longitude, estacao.latitude), 0.025),areaDesconhecida.the_centrogeom) WHERE estacao.id IN (SELECT unnest($1))) to 'geometria_raios.geojson' (FORMAT GDAL, DRIVER GeoJSON );

-- name: raios_com_data
COPY (SELECT areaDesconhecida.time_tick as Data_hora, areaDesconhecida.lon, areaDesconhecida.lat, areaDesconhecida.chi_square_value, areaDesconhecida.the_centrogeom::GEOMETRY('EPSG:4618'), max_rate_of_rise,
         CASE
            WHEN chi_square_value <=3 THEN 'Altamente Confiável'
            WHEN chi_square_value >3 AND chi_square_value <=6 THEN 'Mediano'
            ELSE 'Pouco Confiável'
            END AS Precisao_coleta,
         CASE 
            WHEN abs(max_rate_of_rise) <= 10 THEN 'Leve'
            WHEN abs(max_rate_of_rise) > 10 AND abs(max_rate_of_rise) < 25 THEN 'Média'
            ELSE 'Alta'
            END AS Intensidade_do_Raio,
         CASE
            WHEN peak_current <= 0 THEN 'Raio Comum'
            WHEN peak_current > 0 THEN 'Raio Nuvem-a-Nuvem'
            END AS Status_Raio
         FROM estacao LEFT JOIN areaDesconhecida ON ST_Contains(ST_Buffer(ST_Point(estacao.longitude, estacao.latitude), 0.025),areaDesconhecida.the_centrogeom) WHERE estacao.id IN (SELECT unnest($1)) AND areaDesconhecida.time_tick >= $2 AND areaDesconhecida.time_tick <= $3) to 'geometria_raios.geojson' (FORMAT GDAL, DRIVER GeoJSON );

-- name: pontos_estacoes
COPY (SELECT DISTINCT estacao.id as estacao_id, estacao.nome, estacao.longitude as lon, estacao.latitude as lat, ST_Point(estacao.longitude, estacao.latitude)::GEOMETRY('EPSG:4618'), estacao.altitude, orgao.nome as nome_orgao, tipo_estacao.descricao as tipo_estacao, tipo_coleta.descricao as tipo_coleta, estacao.classificacao, estacao.inicio_operacao, estacao.fim_operacao
FROM estacao LEFT JOIN orgao on orgao.id = estacao.orgao_id
LEFT JOIN tipo_estacao on estacao.tipo_estacao_id = tipo_estacao.id 
LEFT JOIN tipo_coleta on estacao.tipo_coleta_id = tipo_coleta.id
LEFT JOIN areaDesconhecida ON ST_Contains(ST_Buffer(ST_Point(estacao.longitude, estacao.latitude), 0.025),areaDesconhecida.the_centrogeom) WHERE estacao.id IN (SELECT unnest($1))) to 'geometria_estacoes.geojson' (FORMAT GDAL, DRIVER GeoJSON );

-- name: area_raios
COPY (
WITH estacoes_buffer AS (
    SELECT  estacao.id, estacao.nome, ST_Buffer(ST_Point(estacao.longitude, estacao.latitude), 0.025)::GEOMETRY('EPSG:4618') as geometria
    FROM estacao 
    WHERE estacao.id IN (SELECT unnest($1))
),
raios_por_estacao AS (
    SELECT e.id, e.nome, e.geometria, count(a.the_elipsegeom) as numero_de_raios, avg(a.max_rate_of_rise) as media_intensidade, max(a.max_rate_of_rise) as raio_mais_intenso,
            CASE
               WHEN avg(chi_square_value) <=3 THEN 'Altamente Confiável'
               WHEN avg(chi_square_value) >3 AND avg(chi_square_value) <=6 THEN 'Mediano'
               ELSE 'Pouco Confiável'
               END AS media_precisao
    FROM estacoes_buffer e LEFT JOIN areaDesconhecida a ON ST_Contains(e.geometria, a.the_centrogeom)
    GROUP BY e.id, e.nome, e.geometria
)
SELECT  nome, geometria, numero_de_raios, media_intensidade, raio_mais_intenso, media_precisao
FROM raios_por_estacao
) to 'geometria_area_raios.geojson' (FORMAT GDAL, DRIVER GeoJSON );

-- name: area_raios_com_data
COPY (
WITH estacoes_buffer AS (
    SELECT  estacao.id, estacao.nome, ST_Buffer(ST_Point(estacao.longitude, estacao.latitude), 0.025)::GEOMETRY('EPSG:4618') as geometria
    FROM estacao 
    WHERE estacao.id IN (SELECT unnest($1))
),
raios_por_estacao AS (
    SELECT e.id, e.nome, e.geometria, count(a.the_elipsegeom) as numero_de_raios, avg(a.max_rate_of_rise) as media_intensidade, max(a.max_rate_of_rise) as raio_mais_intenso,
            CASE
               WHEN avg(chi_square_value) <=3 THEN 'Altamente Confiável'
               WHEN avg(chi_square_value) >3 AND avg(chi_square_value) <=6 THEN 'Mediano'
               ELSE 'Pouco Confiável'
               END AS media_precisao
    FROM estacoes_buffer e LEFT JOIN areaDesconhecida a ON ST_Contains(e.geometria, a.the_centrogeom) AND a.time_tick >= $2 AND a.time_tick <= $3
    GROUP BY e.id, e.nome, e.geometria
)
SELECT  nome, geometria, numero_de_raios, media_intensidade, raio_mais_intenso, media_precisao
FROM raios_por_estacao
) to 'geometria_area_raios.geojson' (FORMAT GDAL, DRIVER GeoJSON )