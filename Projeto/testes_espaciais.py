import duckdb

con = duckdb.connect(":memory:")


con.sql("INSTALL spatial")
con.sql("LOAD spatial")

con.execute("CREATE OR REPLACE TABLE areaDesconhecida as SELECT * FROM read_parquet('/home/vitor.oliveira/Downloads/estudo/git-demo/reatividadedeestgioduckdb/production_mimic/ano=2025/mes=01/dia=01/*.parquet')")

con.execute("CREATE TABLE IF NOT EXISTS estacao as (SELECT * FROM read_parquet('../reatividadedeestgioduckdb/estacao.parquet'))")

con.sql("SELECT estacao.nome FROM estacao").show()

con.sql("""SELECT estacao.id, estacao.nome, areaDesconhecida.the_elipsegeom
        FROM estacao JOIN areaDesconhecida ON ST_Contains(areaDesconhecida.the_elipsegeom, ST_Point(estacao.longitude, estacao.latitude))""").show()

con.sql("CREATE TABLE valores (area GEOMETRY('EPSG:4618'))")

con.sql("INSERT INTO valores (SELECT ST_Point(latitude, longitude) FROM estacao WHERE id = 20134412)")

con.sql("SELECT ST_Transform(area, 'EPSG:4618', 'EPSG:4326') FROM valores").show()

con.sql("SELECT area FROM valores").show()

con.sql("SELECT * FROM estacao WHERE id = 20134412").show()

# con.sql("SELECT ST_CRS(area) FROM valores").show()


# con.sql("SELECT nome, ST_MakePoint(latitude, longitude)::GEOMETRY('EPSG:4618') FROM estacao").show()



