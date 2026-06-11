-- name: estacao
SELECT estacao.id, estacao.nome, estacao.latitude, estacao.longitude, estacao.altitude, orgao.nome as nome_orgao, tipo_estacao.descricao as tipo_estacao, tipo_coleta.descricao as tipo_coleta, estacao.classificacao, estacao.inicio_operacao, estacao.fim_operacao
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
DELETE FROM dados USING estacao 
WHERE dados.estacao_id = estacao.id AND estacao.id != ?; 

-- name: sensor
SELECT sensor.id, sensor.descricao, sensor.nome_curto, unidade_medida.sigla as unidade_medida, unidade_medida.descricao as descricao_da_medida, operacao.funcao as operacao 
FROM sensor LEFT JOIN unidade_medida on sensor.unidade_medida_id = unidade_medida.id
LEFT JOIN operacao on sensor.classificacao_id = operacao.id
WHERE nome_curto = ?;

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
SELECT dados.data_hora, estacao.id as estacao_id, estacao.nome as estacao_nome, sensor.id as sensor_id, sensor.descricao as sensor_descricao, dados.valor, unidade_medida.sigla as unidade_de_medida, qualidade.descricao as qualidade
FROM dados LEFT JOIN estacao on dados.estacao_id = estacao.id
LEFT JOIN sensor on dados.sensor_id = sensor.id
LEFT JOIN unidade_medida on sensor.unidade_medida_id = unidade_medida.id
LEFT JOIN qualidade on dados.qualidade_id = qualidade.id;

-- name: sensor_dados_filtro
DELETE FROM dados USING sensor 
WHERE dados.sensor_id = sensor.id AND sensor.nome_curto != ?;  
