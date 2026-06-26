import duckdb
import geopandas as gpd
import webbrowser
import os

con = duckdb.connect("raiosFunde.db")

con.sql("INSTALL spatial")
con.sql("LOAD spatial")

arquivo =  "mapa_interativo.html"

con.sql("COPY teste to 'teste.geojson' (FORMAT GDAL, DRIVER GeoJSON)")

gdf = gpd.read_file("teste.geojson")
m = gdf.explore()


m.save(arquivo)

webbrowser.open('file://' + os.path.realpath(arquivo))