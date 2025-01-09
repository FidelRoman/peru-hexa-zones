import math
import csv
import folium
from shapely.geometry import Polygon

# Función para generar los vértices de un hexágono dado el centro y el radio
def create_hexagon(center_lat, center_lon, radius):
    points = []
    for i in range(6):
        angle = math.radians(i * 60)  # Cada vértice está a 60 grados del anterior
        lat = center_lat + (radius * math.sin(angle)) / 111.32  # Convertir el radio a grados en latitud
        lon = center_lon + (radius * math.cos(angle)) / (111.32 * math.cos(math.radians(center_lat)))  # Convertir el radio a grados en longitud
        points.append((lat, lon))
    points.append(points[0])  # Cerrar el polígono (el primer punto debe repetirse al final)
    return Polygon(points)

# Generar una rejilla hexagonal y asignar nombres únicos
def generate_hexagonal_grid(center_lat, center_lon, radius, rows, cols):
    hexagons = []
    zone_id = 1
    for row in range(rows):
        for col in range(cols):
            offset_x = col * 3/2 * radius  # Desplazamiento en X
            offset_y = row * math.sqrt(3) * radius + (col % 2) * math.sqrt(3)/2 * radius  # Desplazamiento en Y
            hex_center_lat = center_lat + offset_y / 111.32  # Convertir desplazamiento a grados en latitud
            hex_center_lon = center_lon + offset_x / (111.32 * math.cos(math.radians(center_lat)))  # Convertir desplazamiento a grados en longitud
            hexagon = create_hexagon(hex_center_lat, hex_center_lon, radius)
            hex_name = f"zona_{zone_id:03d}"  # Generar el nombre único
            # Convertir el polígono en formato WKT POLYGON((...))
            hex_wkt = f"POLYGON(({', '.join([f'{lon} {lat}' for lat, lon in hexagon.exterior.coords])}))"
            hexagons.append({"name": hex_name, "geometry": hex_wkt, "polygon": hexagon})
            zone_id += 1
    return hexagons

# Coordenadas del centro de Lima
center_lat = -12.25  # Más hacia abajo
center_lon = -77.17  # Más hacia la izquierda

# Radio del hexágono (ajustado para mayor visibilidad)
radius = 1  # Radio de ~2 km

# Generar una rejilla de hexágonos de 15 filas x 15 columnas
hexagons = generate_hexagonal_grid(center_lat, center_lon, radius, 20, 25)

# Guardar el resultado como un archivo CSV con las zonas y sus geometrías WKT
with open("hexagonal_zones_wkt.csv", "w", newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    # Escribir el encabezado
    csvwriter.writerow(["zone_name", "geometry"])
    # Escribir las filas
    for hexagon in hexagons:
        csvwriter.writerow([hexagon["name"], hexagon["geometry"]])

print("Archivo CSV generado con éxito: 'hexagonal_zones_wkt.csv'")

# Crear un mapa centrado en Lima usando Folium
m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

# Añadir los hexágonos al mapa con Folium
for hexagon in hexagons:
    folium.Polygon(
        locations=[(lat, lon) for lat, lon in hexagon['polygon'].exterior.coords],
        color="blue",
        weight=2,
        fill=True,
        fill_opacity=0.4,
        tooltip=hexagon["name"]  # Añadir tooltip con el nombre de la zona
    ).add_to(m)

# Guardar el mapa como archivo HTML
m.save("hexagonal_grid_lima.html")

print("Archivo HTML del mapa generado con éxito: 'hexagonal_grid_lima.html'")