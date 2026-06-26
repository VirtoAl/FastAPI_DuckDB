import duckdb
import time

con = duckdb.connect("raiosFunde.db")

con.sql("INSTALL spatial")
con.sql("LOAD spatial;")

tempo = time.time()
print(f"tempo inicial: {(time.time() - tempo)}")

con.execute(
    "CREATE TABLE IF NOT EXISTS sensor as SELECT * FROM read_parquet('../reatividadedeestgioduckdb/production_mimic/ano=2025/mes=01/*/*.parquet')"
)

con.execute("CREATE TABLE IF NOT EXISTS areaDesconhecida as SELECT * FROM read_parquet('../reatividadedeestgioduckdb/production_mimic/ano=2025/mes=01/dia=01/8a7ba7ef-8ae2-4c7e-8461-c6ee690c6d80.parquet')")

con.sql("SELECT the_elipsegeom FROM areaDesconhecida LIMIT 1").show()

con.sql("CREATE TABLE IF NOT EXISTS teste (nome VARCHAR, geometrica GEOMETRY)")




# con.sql("""
# INSERT INTO teste VALUES
#         ('point', ST_GeomFromText('POINT(-51.10089 -0.00221)')),
#         ('MeuDeus', ST_GeomFromText('POLYGON ((-66.05852077067522 -30.61091771039725, -66.03437934600498 -30.620640087835646, -65.98042708020328 -30.617021256429926, -65.90489860572833 -30.600580173748604, -65.81932396809137 -30.5737914624696, -65.7367547340507 -30.540725359908834, -65.66976305984345 -30.506432730258197, -65.62852666584094 -30.47616612536997, -65.6192918770639 -30.45456148224445, -65.6434412503465 -30.444915979658553, -65.69729673469901 -30.448681444859833, -65.77268039001775 -30.465253024167968, -65.85814700468735 -30.492079651244904, -65.94070829124449 -30.52506887823762, -66.0077967481819 -30.559214874125303, -66.0491779602118 -30.589350983102268, -66.05852077067522 -30.61091771039725))'))
# """)

con.sql("""
INSERT INTO teste (nome, geometrica)
    SELECT 'nomePadrao',the_elipsegeom FROM areaDesconhecida USING SAMPLE 5
""")

con.sql("SELECT * FROM teste").show()


# df = con.execute("SELECT DISTINCT h3_index FROM sensor").df()
# print(df)


# con.sql("SELECT * FROM sensor").show()



print(f"tempo final: {(time.time() - tempo)}")



# con.table("sensor").show()

# Converter para uma lista
# [item[0] for item in con.sql(QUERRY[]).fetchall()]