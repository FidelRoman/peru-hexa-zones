import math
import pandas as pd
from shapely.geometry import Polygon, Point
from shapely import wkt
import time
from get_coverages import get_coverage, get_coverage_updated

# ---------------------------------------
# Función para crear un hexágono
# ---------------------------------------
def create_hexagon(center_lat, center_lon, radius):
    points = []
    for i in range(6):
        angle = math.radians(i * 60)
        lat = center_lat + (radius * math.sin(angle)) / 111.32
        lon = center_lon + (radius * math.cos(angle)) / (111.32 * math.cos(math.radians(center_lat)))
        points.append((lon, lat))
    points.append(points[0])
    return Polygon(points)

# ---------------------------------------
# Cargar distritos del Perú
# ---------------------------------------
df_districts = pd.read_csv("assets/peru_districts_shape.csv")

district_polygons = []
for i, wkt_str in enumerate(df_districts["geo_shape"]):
    try:
        poly = wkt.loads(wkt_str)
        if poly.geom_type == "Polygon":
            district_polygons.append((poly, df_districts.iloc[i]))
        elif poly.geom_type == "MultiPolygon":
            for sub_poly in poly.geoms:
                district_polygons.append((sub_poly, df_districts.iloc[i]))
    except Exception:
        continue

# ---------------------------------------
# Función principal por ciudad
# ---------------------------------------
def procesar_ciudad(ciudad, center_lon, center_lat, radius=0.5, n_rows=20, n_cols=25):
    print(f"Procesando ciudad: {ciudad}...")
    hex_records = []
    zone_id = 1

    # Generar todos los hexágonos
    for row in range(n_rows):
        for col in range(n_cols):
            offset_x = col * 3/2 * radius
            offset_y = row * math.sqrt(3) * radius + (col % 2) * (math.sqrt(3)/2 * radius)

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

    # Filtrar solo hexágonos dentro de Perú y asignar departamento/provincia/distrito
    output_records = []
    for _, row in df_hex.iterrows():
        centroide = Point(row["centroid_lon"], row["centroid_lat"])
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

    # Obtener cobertura Rappi
    coverages, cities, zones = [], [], []
    for _, row in df_final.iterrows():
        has_cov, city, zone = get_coverage(row["centroid_lat"], row["centroid_lon"])
        coverages.append(has_cov)
        cities.append(city)
        zones.append(zone)
        time.sleep(0.3)

    df_final["has_coverage"] = coverages
    df_final["city"] = cities
    df_final["zone_rappi"] = zones

    coverage_messages = []
    for _, row in df_final.iterrows():
        msg = get_coverage_updated(row["centroid_lat"], row["centroid_lon"])
        coverage_messages.append(msg)
        time.sleep(0.3)

    df_final["coverage_messages"] = coverage_messages
    df_final["timestamp"] = pd.Timestamp.now()

    # Guardar **solo** el CSV final
    output_path = f"{ciudad.lower()}_hexagonos_final.csv"
    df_final.to_csv(output_path, index=False)
    print(f"✓ CSV final guardado en: {output_path}")

# ---------------------------------------
# Lista de ciudades y coordenadas
# ---------------------------------------
ciudades = [
    {"ciudad": "Arequipa",  "center_lon": -71.59923629, "center_lat": -16.4645831},
    # {"ciudad": "Chiclayo",  "center_lon": -79.906642,    "center_lat": -6.819968},
    # {"ciudad": "Huancayo",  "center_lon": -75.2658686,   "center_lat": -12.099199},
    # {"ciudad": "Trujillo",  "center_lon": -79.07767037,  "center_lat": -8.15671},
    # {"ciudad": "Ica",       "center_lon": -75.769778,    "center_lat": -14.11352},
    # {"ciudad": "Piura",     "center_lon": -80.69102763,  "center_lat": -5.242906}
    
]

# Iterar sobre las ciudades
for info in ciudades:
    procesar_ciudad(**info)
