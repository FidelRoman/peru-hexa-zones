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
# def procesar_ciudad(ciudad, center_lon, center_lat, radius=0.5, n_rows=20, n_cols=25):
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
    output_path = f"data/{ciudad.lower()}_hexagonos_final.csv"
    df_final.to_csv(output_path, index=False)
    print(f"✓ CSV final guardado en: {output_path}")

# ---------------------------------------
# Lista de ciudades y coordenadas
# ---------------------------------------
ciudades = [
    # # {"ciudad": "Arequipa", "center_lon": -71.59823629, "center_lat": -16.4715831},
    # {"ciudad": "Ayacucho", "center_lon": -74.2568446, "center_lat": -13.2222462},
    # {"ciudad": "Cajamarca", "center_lon": -78.545282, "center_lat": -7.21106},
    # {"ciudad": "Cañete", "center_lon": -76.4143361, "center_lat": -13.1051316},
    # {"ciudad": "Centro", "center_lon": -77.08749557, "center_lat": -12.1561274},
    # # {"ciudad": "Chiclayo", "center_lon": -79.918642, "center_lat": -6.831968},
    # {"ciudad": "Chimbote", "center_lon": -78.624955, "center_lat": -9.174626756},
    # {"ciudad": "Chincha alta", "center_lon": -76.19793039, "center_lat": -13.46808},
    # {"ciudad": "Cusco", "center_lon": -72.01284427, "center_lat": -13.56606903},
    # {"ciudad": "Huacho", "center_lon": -77.6508463, "center_lat": -11.149141},
    # # {"ciudad": "Huancayo", "center_lon": -75.2778686, "center_lat": -12.113199},
    # {"ciudad": "Huanuco", "center_lon": -76.2785276, "center_lat": -9.9680716},
    # {"ciudad": "Huaral", "center_lon": -77.2553637, "center_lat": -11.5271079},
    # {"ciudad": "Huaraz", "center_lon": -77.5618383, "center_lat": -9.5584525},
    # # {"ciudad": "Ica", "center_lon": -75.781778, "center_lat": -14.12552},
    # {"ciudad": "Ilo", "center_lon": -71.37158011, "center_lat": -17.6775188},
    # {"ciudad": "Iquitos", "center_lon": -73.3177722, "center_lat": -3.808329},
    # {"ciudad": "Juliaca", "center_lon": -70.2058917, "center_lat": -15.5970155},
    # # {"ciudad": "Lima", "center_lon": -77.1864123, "center_lat": -12.856899},
    {"ciudad": "Moquegua", "center_lon": -70.9816072, "center_lat": -17.2321443},
    # {"ciudad": "Piura", "center_lon": -80.70302763, "center_lat": -5.254906},
    {"ciudad": "Pucallpa", "center_lon": -74.6196149, "center_lat": -8.4333163},
    {"ciudad": "Sullana", "center_lon": -80.77094037, "center_lat": -4.951375834},
    {"ciudad": "Tacna", "center_lon": -70.308191, "center_lat": -18.08283478},
    {"ciudad": "Talara", "center_lon": -81.305947, "center_lat": -4.617656},
    # {"ciudad": "Trujillo", "center_lon": -79.08967037, "center_lat": -8.16871}
]


# Iterar sobre las ciudades
for info in ciudades:
    procesar_ciudad(**info)



# Ejecutar en bash : 
# head -n 1 data/*.csv | head -n 1 > hexagonos_peru_completo.csv && tail -n +2 -q data/*.csv >> hexagonos_peru_completo.csv
