import math
import csv
import folium
from shapely.geometry import Polygon
from shapely import wkt
import pandas as pd
import geopandas as gpd

# Función para generar los vértices de un hexágono dado el centro y el radio
def create_hexagon(center_lat, center_lon, radius):
    points = []
    for i in range(6):
        angle = math.radians(i * 60)
        lat = center_lat + (radius * math.sin(angle)) / 111.32
        lon = center_lon + (radius * math.cos(angle)) / (111.32 * math.cos(math.radians(center_lat)))
        points.append((lat, lon))
    points.append(points[0])
    return Polygon(points)

# Generar una rejilla hexagonal
def generate_hexagonal_grid(center_lat, center_lon, radius, rows, cols):
    hexagons = []
    zone_id = 1
    for row in range(rows):
        for col in range(cols):
            offset_x = col * 3/2 * radius
            offset_y = row * math.sqrt(3) * radius + (col % 2) * math.sqrt(3)/2 * radius
            hex_center_lat = center_lat + offset_y / 111.32
            hex_center_lon = center_lon + offset_x / (111.32 * math.cos(math.radians(center_lat)))
            hexagon = create_hexagon(hex_center_lat, hex_center_lon, radius)
            hex_name = f"zona_{zone_id:03d}"
            hexagons.append({"name": hex_name, "polygon": hexagon, "intersections": []})
            zone_id += 1
    return hexagons

# Función para corregir el orden de las coordenadas
def swap_coordinates(geometry):
    if geometry.geom_type == 'Polygon':
        new_coords = [tuple(reversed(coord)) for coord in geometry.exterior.coords]
        return Polygon(new_coords)
    return geometry

# Leer los datos de distritos y convertir geo_shape a geometría
df_districts = pd.read_csv("peru_districts_shape.csv")
df_districts["geometry"] = df_districts["geo_shape"].apply(wkt.loads)
df_districts["geometry"] = df_districts["geometry"].apply(swap_coordinates)

# Convertir a GeoDataFrame
districts_gdf = gpd.GeoDataFrame(df_districts, geometry="geometry", crs="EPSG:4326")

# Coordenadas del centro de Lima
center_lat = -12.25
center_lon = -77.17
radius = 1
n_rows = 20
n_cols = 25

# Generar hexágonos
hexagons = generate_hexagonal_grid(center_lat, center_lon, radius, n_rows, n_cols)

# Asignar datos a cada hexágono basado en intersecciones
for h in hexagons:
    poly = h["polygon"]
    intersecting_rows = []
    
    # Iterar sobre cada fila del GeoDataFrame para verificar intersección
    for idx, row in districts_gdf.iterrows():
        if poly.intersects(row.geometry):
            intersecting_rows.append({
                "ccdd": row["ccdd"],
                "nombdep": row["nombdep"],
                "ccpp": row["ccpp"],
                "nombprov": row["nombprov"],
                "ccdi": row["ccdi"],
                "nombdist": row["nombdist"],
                "capital": row["capital"],
                "ubigeo": row["ubigeo"],
                "idprov": row["idprov"],
                "codigo": row["codigo"],
                "cnt_ccpp": row["cnt_ccpp"],
                "descripcio": row["descripcio"],
                "poblacion": row["poblacion"],
                "fecha": row["fecha"],
                "dat_pob": row["dat_pob"],
                "pobreza": row["pobreza"],
                "internet_access": row["internet_access"],
                "edad": row["edad"],
                "tam": row["tam"],
                "rmapshaperid": row["rmapshaperid"]
            })
    
    # Agregar las filas intersectadas al hexágono
    h["intersections"] = intersecting_rows

# Guardar los resultados en un archivo CSV
with open("hexagonal_zones_with_data.csv", "w", newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    
    # Escribir el encabezado
    header = [
        "zone_name", "geometry", "ccdd", "nombdep", "ccpp", "nombprov", "ccdi", 
        "nombdist", "capital", "ubigeo", "idprov", "codigo", "cnt_ccpp", 
        "descripcio", "poblacion", "fecha", "dat_pob", "pobreza", 
        "internet_access", "edad", "tam", "rmapshaperid"
    ]
    csvwriter.writerow(header)
    
    # Escribir cada hexágono con las filas intersectadas
    for hexagon in hexagons:
        for data in hexagon["intersections"]:
            csvwriter.writerow([
                hexagon["name"], hexagon["polygon"].wkt, 
                data["ccdd"], data["nombdep"], data["ccpp"], data["nombprov"], 
                data["ccdi"], data["nombdist"], data["capital"], data["ubigeo"], 
                data["idprov"], data["codigo"], data["cnt_ccpp"], data["descripcio"], 
                data["poblacion"], data["fecha"], data["dat_pob"], data["pobreza"], 
                data["internet_access"], data["edad"], data["tam"], data["rmapshaperid"]
            ])

print("Archivo CSV generado con éxito: 'hexagonal_zones_with_data.csv'")

# Crear el mapa interactivo
m = folium.Map(location=[center_lat, center_lon], zoom_start=12)


for hexagon in hexagons:
    folium.Polygon(
        locations=[(lat, lon) for lat, lon in hexagon["polygon"].exterior.coords],
        color="blue",
        weight=2,
        fill=True,
        fill_opacity=0.4,
        tooltip=f"{hexagon['name']} - {len(hexagon['intersections'])} intersecciones"
    ).add_to(m)

m.save("index.html")
print("Archivo HTML del mapa generado con éxito: 'index.html'")