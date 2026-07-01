import duckdb
import time
import leafmap
import webbrowser
import os
import geopandas as gpd
from lonboard import Map, SolidPolygonLayer
from IPython.display import display

con = duckdb.connect("raiosFunde.db")

con.sql("INSTALL spatial")
con.sql("LOAD spatial")

tempo = time.time()
print(f"tempo inicial: {(time.time() - tempo)}")

arquivoBlob = "mapaBlob.html"
arquivoDftoGeo = "mapaDf.html"
arquivotoGeojson = "mapaGeoJson.html"
arquivoParquet = "mapaParquet.html"

con.execute(
    "CREATE OR REPLACE TABLE areaDesconhecida as SELECT * FROM read_parquet('/home/vitor.oliveira/Downloads/estudo/git-demo/reatividadedeestgioduckdb/production_mimic/ano=2025/mes=01/*/*.parquet')"
)
con.execute(
    "CREATE TABLE IF NOT EXISTS estacao as (SELECT * FROM read_parquet('../reatividadedeestgioduckdb/estacao.parquet'))"
)


con.sql("SELECT count(*) FROM areaDesconhecida").show()

con.sql("SELECT DISTINCT ST_CRS(the_elipsegeom) FROM areaDesconhecida").show()

# df = con.sql("SELECT the_elipsegeom FROM areaDesconhecida LIMIT 1").df()


# ----------------------------------------------------------------------------------------------------------------------

# # Método lendo diretamente o arquivo .parquet, velocidade média, porém se limita a apenas um arquivo

# caminho_url = '/home/vitor.oliveira/Downloads/estudo/git-demo/reatividadedeestgioduckdb/production_mimic/ano=2025/mes=01/dia=01/0bc743a0-5fce-45c0-afb2-b2476d9f287c.parquet'


# # gdf = leafmap.parquet_to_gdf(caminho_url, geometry = 'the_elipsegeom', columns=["time_tick", "lat", "lon"])
# gdf = leafmap.read_parquet(caminho_url, return_type='gdf', src_crs='EPSG:4618', dst_crs="EPSG:4618", geometry="the_elipsegeom")

# con.sql(f"DESCRIBE FROM '{caminho_url}'").show()

# print(type(gdf))

# camada = SolidPolygonLayer.from_geopandas(
#     gdf,
#     get_fill_color=[255,0,0],
# )

# m = Map(camada)

# m.to_html(arquivoParquet)


# # # gdf.explore()  -- Se estiver rodando pela web o algoritmo

# # m = gdf.explore()

# # m.save(arquivoParquet)


# webbrowser.open(os.path.abspath(arquivoParquet))

# print(f"tempo final: {(time.time() - tempo)}")

# ----------------------------------------------------------------------------------------------------------------------

# # # Solução mais pobrinha, a que mais demora, e tem limite de aproximadamente, 500000 strings

# df = con.sql("SELECT ST_AsText(the_elipsegeom) as the_elipsegeom FROM areaDesconhecida LIMIT 20000").df()

# gdf_df = leafmap.df_to_gdf(df, geometry='the_elipsegeom', src_crs="EPSG:4326") #converte dataframe para geometry
# # gdf.explore()  -- Se estiver rodando pela web o algoritmo

# m = leafmap.Map()

# m.add_gdf(gdf_df, layer_name="surbway",)
# m.to_html(arquivoDftoGeo)

# webbrowser.open(os.path.abspath(arquivoDftoGeo))

# print(f"tempo final: {(time.time() - tempo)}")
# # ----------------------------------------------------------------------------------------------------------------------

# Método mais rápido utilizando blob como elemento de parâmetro

arrow_table_areas = con.sql("""SELECT areaDesconhecida.time_tick, areaDesconhecida.lon, areaDesconhecida.lat, ST_AsWKB(areaDesconhecida.the_elipsegeom) as geometry
        FROM estacao LEFT JOIN areaDesconhecida ON ST_Contains(areaDesconhecida.the_elipsegeom, ST_Point(estacao.longitude, estacao.latitude))""").fetch_arrow_table()
arrow_table_pontos = con.sql("""SELECT estacao.id, estacao.nome, ST_AsWKB(ST_Point(estacao.longitude,estacao.latitude)) as geometry
        FROM estacao LEFT JOIN areaDesconhecida ON ST_Contains(areaDesconhecida.the_elipsegeom, ST_Point(estacao.longitude, estacao.latitude))""").fetch_arrow_table()

# con.sql("""SELECT areaDesconhecida.time_tick, areaDesconhecida.lon, areaDesconhecida.lat, areaDesconhecida.the_elipsegeom as geometry
#         FROM estacao LEFT JOIN areaDesconhecida ON ST_Contains(areaDesconhecida.the_elipsegeom, ST_Point(estacao.longitude, estacao.latitude))""").show()
# con.sql("""SELECT estacao.id, estacao.nome, ST_Point(estacao.longitude,estacao.latitude) as geometry
#         FROM estacao LEFT JOIN areaDesconhecida ON ST_Contains(areaDesconhecida.the_elipsegeom, ST_Point(estacao.longitude, estacao.latitude))""").show()


gdf_areas = gpd.GeoDataFrame(arrow_table_areas.to_pandas(), geometry=gpd.GeoSeries.from_wkb(arrow_table_areas["geometry"]), crs="EPSG:4618")
gdf_pontos = gpd.GeoDataFrame(arrow_table_pontos.to_pandas(), geometry=gpd.GeoSeries.from_wkb(arrow_table_pontos["geometry"]), crs="EPSG:4618")
# gdf.explore()  -- Se estiver rodando pela web o algoritmo
# gdf_areas = gdf_wkb.explode(ignore_index=True)


print(gdf_areas.columns)
print(gdf_pontos.columns)

m = gdf_areas.explore(popup=True, cmap="Set1", tooltip=['time_tick', 'lon', 'lat'], style_kwds=dict(color="green"), name="Areas de incidência de raio")
gdf_pontos.explore(m=m, color="red", marker_kwds=dict(radius=2, fill=True), name="Estações")


# m = leafmap.Map()

# # m.add_gdf(gdf_wkb, layer_name="surbway")

# # m.to_html(arquivoBlob)
m.save(arquivoBlob)


webbrowser.open(f"file://{os.path.abspath(arquivoBlob)}")

print(f"tempo final: {(time.time() - tempo)}")

# ----------------------------------------------------------------------------------------------------------------------

# # Método utilizando arquivo gerado geojson para alimentar o GEOdataFrame, eficiência média

# # con.sql("COPY (SELECT time_tick, lat, lon, ST_Collect([the_centrogeom,the_elipsegeom]) as geometry FROM areaDesconhecida LIMIT 1000) to 'geometria_raios.geojson' (FORMAT GDAL, DRIVER GeoJSON)")

# con.sql("COPY (SELECT nome, ST_Point(longitude, latitude)::GEOMETRY('EPSG:4618') FROM estacao) to 'geometria_raios.geojson' (FORMAT GDAL, DRIVER GeoJSON )")

# # con.sql("SELECT nome, ST_Point(latitude, longitude)::GEOMETRY('EPSG:4618') FROM estacao").show()


# gdf = gpd.read_file("geometria_raios.geojson")

# # m = leafmap.Map()
# # m.add_vector(
# #     gdf,
# #     radius=2000,
# #     radius_units="meters"
# #     get_fill_color='blue'
# # )
# m = gdf.explore(cmap="Set1")
# # m = leafmap.view_vector(gdf, get_radius=2000, get_fill_color='blue')


# # m.to_html(arquivotoGeojson)
# m.save(arquivotoGeojson)

# webbrowser.open(os.path.realpath(arquivotoGeojson))
# print(f"tempo final: {(time.time() - tempo)}")

# ----------------------------------------------------------------------------------------------------------------------


# # print(gdf)

# print(f"CRS atual {gdf.crs}")


# # con.sql("CREATE TABLE IF NOT EXISTS teste (nome VARCHAR, geometrica GEOMETRY)")


# con.sql("""
# INSERT INTO teste VALUES
#         ('point', ST_GeomFromText('POINT(-51.10089 -0.00221)')),
#         ('MeuDeus', ST_GeomFromText('POLYGON ((-66.05852077067522 -30.61091771039725, -66.03437934600498 -30.620640087835646, -65.98042708020328 -30.617021256429926, -65.90489860572833 -30.600580173748604, -65.81932396809137 -30.5737914624696, -65.7367547340507 -30.540725359908834, -65.66976305984345 -30.506432730258197, -65.62852666584094 -30.47616612536997, -65.6192918770639 -30.45456148224445, -65.6434412503465 -30.444915979658553, -65.69729673469901 -30.448681444859833, -65.77268039001775 -30.465253024167968, -65.85814700468735 -30.492079651244904, -65.94070829124449 -30.52506887823762, -66.0077967481819 -30.559214874125303, -66.0491779602118 -30.589350983102268, -66.05852077067522 -30.61091771039725))'))
# """)

# con.sql("""
# INSERT INTO teste (nome, geometrica)
#     SELECT 'nomePadrao',the_elipsegeom FROM areaDesconhecida USING SAMPLE 5
# """)

# con.sql("SELECT * FROM teste").show()


# df = con.execute("SELECT DISTINCT h3_index FROM sensor").df()
# print(df)


# con.sql("SELECT * FROM sensor").show()


# con.table("sensor").show()

# Converter para uma lista
# [item[0] for item in con.sql(QUERRY[]).fetchall()]
