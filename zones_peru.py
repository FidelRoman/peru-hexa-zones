import math
import pandas as pd
from shapely.geometry import Polygon, Point
from shapely import wkt
import folium
import geopandas as gpd
from shapely import wkt
import pandas as pd
import time
from get_coverages  import get_coverage, get_coverage_updated


center_lat = -16.42  
center_lon = -71.56 
radius = 1            
n_rows = 20
n_cols = 25
ciudad = "AREQUIPA"




def create_hexagon(center_lat, center_lon, radius):
    points = []
    for i in range(6):
        angle = math.radians(i * 60)
        lat = center_lat + (radius * math.sin(angle)) / 111.32
        lon = center_lon + (radius * math.cos(angle)) / (111.32 * math.cos(math.radians(center_lat)))
        points.append((lon, lat))
    
    points.append(points[0])
    return Polygon(points)


df_districts = pd.read_csv("peru_districts_shape.csv") 

district_polygons = []
for i, wkt_str in enumerate(df_districts["geo_shape"]):
    try:
        poly = wkt.loads(wkt_str)
        # Si es un Polígono simple
        if poly.geom_type == 'Polygon':
            district_polygons.append((poly, df_districts.iloc[i]))
        # Si es un MultiPolígono, se separa en sus polígonos hijos
        elif poly.geom_type == 'MultiPolygon':
            for sub_poly in poly.geoms:
                district_polygons.append((sub_poly, df_districts.iloc[i]))
    except Exception as e:
        # Opcional: imprimir el error para debug
        # print(f"Error al procesar fila {i}: {e}")
        continue



hex_records = []
zone_id = 1

for row in range(n_rows):
    for col in range(n_cols):
        # Cálculo de offsets para acomodar los hexágonos “en colmena”
        offset_x = col * 3/2 * radius
        offset_y = row * math.sqrt(3) * radius + (col % 2) * (math.sqrt(3)/2 * radius)
        
        # Convertir el offset en grados
        hex_center_lat = center_lat + offset_y / 111.32
        hex_center_lon = center_lon + offset_x / (111.32 * math.cos(math.radians(center_lat)))
        
        hexagon = create_hexagon(hex_center_lat, hex_center_lon, radius)
        
        hex_records.append({
            "hexagono_id": f"zona_{zone_id:06d}",
            "hexagono_shape": hexagon.wkt,
            "centroid_lat": hex_center_lat,
            "centroid_lon": hex_center_lon
        })
        zone_id += 1

df_hex = pd.DataFrame(hex_records)
df_hex.to_csv("hexagonos_generados.csv", index=False)

# ------------------------------------------------
# Asignar un distrito a cada hexágono
# ------------------------------------------------
df_hex_loaded = pd.read_csv("hexagonos_generados.csv")

output_records = []
for _, row in df_hex_loaded.iterrows():
    # Creamos el punto del centroide (x=lon, y=lat)
    centroide = Point(row["centroid_lon"], row["centroid_lat"])
    
    # Se busca el primer distrito cuyo polígono contenga ese punto
    for poly, dist_row in district_polygons:
        if poly.contains(centroide):
            output_records.append({
                "hexagono_id": row["hexagono_id"],
                "hexagono_shape": row["hexagono_shape"],
                "centroid_lat": row["centroid_lat"],
                "centroid_lon": row["centroid_lon"],
                "nombdep": dist_row["nombdep"],
                "nombprov": dist_row["nombprov"],
                "nombdist": dist_row["nombdist"]
            })
            break

df_final = pd.DataFrame(output_records)
df_final.to_csv("hexagonos_peru.csv", index=False)

print("Proceso finalizado. Revisa el archivo 'hexagonos_peru.csv'.")


df_final["geometry"] = df_final["hexagono_shape"].apply(wkt.loads)

gdf_final = gpd.GeoDataFrame(df_final, geometry="geometry", crs="EPSG:4326")

# center_lat = -12.25
# center_lon = -77.17
# m = folium.Map(location=[center_lat, center_lon], zoom_start=10)

# for _, row in gdf_final.iterrows():
#     folium.GeoJson(
#         row["geometry"],
#         name=row["hexagono_id"],
#         tooltip=f"{row['hexagono_id']} - {row['nombdist']}"
#     ).add_to(m)

# m.save("hexagonos_peru_final_map.html")
# print("Mapa guardado como hexagonos_peru_final_map.html")



# Listas para almacenar resultados
coverages = []
cities = []
zones = []
# Recorrer cada fila del DataFrame y obtener cobertura

peru_zones = pd.read_csv("hexagonos_peru.csv")
peru_zones = peru_zones[peru_zones["nombprov"] == ciudad]


# Recorrer cada fila del DataFrame y obtener cobertura
for index, row in peru_zones.iterrows():
    has_coverage, city, zone = get_coverage(row["centroid_lat"], row["centroid_lon"])
    coverages.append(has_coverage)
    cities.append(city)
    zones.append(zone)
    time.sleep(0.3)

# Agregar resultados al DataFrame
peru_zones["has_coverage"] = coverages
peru_zones["city"] = cities
peru_zones["zone_rappi"] = zones 

peru_zones.to_csv("hexagonos_peru_rappi.csv", index=False, encoding="utf-8")

coverage_messages = []
for index, row in peru_zones.iterrows():
    coverage_message = get_coverage_updated(row["centroid_lat"], row["centroid_lon"])
    coverage_messages.append(coverage_message)
    time.sleep(0.3)

# Agregar resultados al DataFrame
peru_zones["coverage_messages"] = coverage_messages
peru_zones["timestamp"] = pd.Timestamp.now()

peru_zones.to_csv("hexagonos_peru_rappi_final.csv", index=False, encoding="utf-8")