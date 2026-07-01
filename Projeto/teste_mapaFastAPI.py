from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import geopandas as gpd
import duckdb

con = duckdb.connect(":memory:")

con.sql("INSTALL spatial")
con.sql("LOAD spatial")

con.execute(
    "CREATE OR REPLACE TABLE areaDesconhecida as SELECT * FROM read_parquet('/home/vitor.oliveira/Downloads/estudo/git-demo/reatividadedeestgioduckdb/production_mimic/ano=2025/mes=01/dia=01/*.parquet')"
)
con.execute(
    "CREATE TABLE IF NOT EXISTS estacao as (SELECT * FROM read_parquet('../reatividadedeestgioduckdb/estacao.parquet'))"
)

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def exibir_mapa():
    # 1. Cria o mapa interativo centrado em Curitiba
    arrow_table_areas = con.sql("""SELECT areaDesconhecida.time_tick, areaDesconhecida.lon, areaDesconhecida.lat, ST_AsWKB(areaDesconhecida.the_elipsegeom) as geometry
        FROM estacao LEFT JOIN areaDesconhecida ON ST_Contains(areaDesconhecida.the_elipsegeom, ST_Point(estacao.longitude, estacao.latitude))""").fetch_arrow_table()
    arrow_table_pontos = con.sql("""SELECT estacao.id, estacao.nome, ST_AsWKB(ST_Point(estacao.longitude,estacao.latitude)) as geometry
        FROM estacao LEFT JOIN areaDesconhecida ON ST_Contains(areaDesconhecida.the_elipsegeom, ST_Point(estacao.longitude, estacao.latitude))""").fetch_arrow_table()

    gdf_areas = gpd.GeoDataFrame(arrow_table_areas.to_pandas(), geometry=gpd.GeoSeries.from_wkb(arrow_table_areas["geometry"]), crs="EPSG:4618")
    gdf_pontos = gpd.GeoDataFrame(arrow_table_pontos.to_pandas(), geometry=gpd.GeoSeries.from_wkb(arrow_table_pontos["geometry"]), crs="EPSG:4618")
    
    m = gdf_areas.explore(popup=True, cmap="Set1", tooltip=['time_tick', 'lon', 'lat'], style_kwds=dict(color="green"), name="Areas de incidência de raio")
    gdf_pontos.explore(m=m, color="red", marker_kwds=dict(radius=2, fill=True), name="Estações")

    
    # 3. Extrai o HTML gerado pelo Folium e retorna diretamente para o navegador
    html_do_mapa = m._repr_html_()
    return HTMLResponse(content=html_do_mapa)

