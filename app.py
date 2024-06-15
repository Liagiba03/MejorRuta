from flask import Flask, render_template, request, jsonify
import math
import random

app = Flask(__name__)

# Coordenadas de las ciudades
coord = {
    'Aguascalientes': [21.87641043660486, -102.26438663286967],
    'BajaCalifornia': [32.5027, -117.00371],
    'BajaCaliforniaSur': [24.14437, -110.3005],
    'Campeche': [19.8301, -90.53491],
    'Chiapas': [16.75, -93.1167],
    'Chihuahua': [28.6353, -106.0889],
    'CDMX': [19.432713075976878, -99.13318344772986],
    'Coahuila': [25.4260, -101.0053],
    'Colima': [19.2452, -103.725],
    'Durango': [24.0277, -104.6532],
    'Guanajuato': [21.0190, -101.2574],
    'Guerrero': [17.5506, -99.5024],
    'Hidalgo': [20.1011, -98.7624],
    'Jalisco': [20.6767, -103.3475],
    'Mexico': [19.285, -99.5496],
    'Michoacan': [19.701400113725654, -101.20829680213464],
    'Morelos': [18.6813, -99.1013],
    'Nayarit': [21.5085, -104.895],
    'NuevoLeon': [25.6714, -100.309],
    'Oaxaca': [17.0732, -96.7266],
    'Puebla': [19.0414, -98.2063],
    'Queretaro': [20.5972, -100.387],
    'QuintanaRoo': [21.1631, -86.8023],
    'SanLuisPotosi': [22.1565, -100.9855],
    'Sinaloa': [24.8091, -107.394],
    'Sonora': [29.0729, -110.9559],
    'Tabasco': [17.9892, -92.9475],
    'Tamaulipas': [25.4348, -99.134],
    'Tlaxcala': [19.3181, -98.2375],
    'Veracruz': [19.1738, -96.1342],
    'Yucatan': [20.967, -89.6237],
    'Zacatecas': [22.7709, -102.5833]
}

def distancia(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)

def evalua_ruta(ruta, coord):
    total = 0
    for i in range(0, len(ruta) - 1):
        ciudad1 = ruta[i]
        ciudad2 = ruta[i + 1]
        total += distancia(coord[ciudad1], coord[ciudad2])
    return total

def simulated_annealing(ruta, coord):
    T = 20
    T_MIN = 0
    V_enfriamiento = 100

    while T > T_MIN:
        dist_actual = evalua_ruta(ruta, coord)
        for _ in range(1, V_enfriamiento):
            i = random.randint(1, len(ruta) - 2)  # Evitar intercambiar origen y destino
            j = random.randint(1, len(ruta) - 2)
            ruta_tmp = ruta[:]
            ruta_tmp[i], ruta_tmp[j] = ruta_tmp[j], ruta_tmp[i]
            dist_tmp = evalua_ruta(ruta_tmp, coord)
            delta = dist_tmp - dist_actual
            if delta < 0 or random.random() < math.exp(-delta / T):
                ruta = ruta_tmp[:]
                dist_actual = dist_tmp
        T -= 0.005
    return ruta

@app.route('/')
def index():
    return render_template('index.html', ciudades=coord.keys())

@app.route('/get_routes', methods=['POST'])
def get_routes():
    data = request.get_json()
    origen = data['start']
    destino = data['end']
    umbral_lat = 0.00001
    umbral_lon = 0.00001

    if origen not in coord or destino not in coord:
        return jsonify({'error': 'Inicio o fin inválidos.'}), 400

    nodos_intermedios = encontrar_nodos_intermedios(coord, origen, destino, umbral_lat, umbral_lon)
    
    ruta_inicial = [origen] + nodos_intermedios + [destino]
    ruta_optima = simulated_annealing(ruta_inicial, coord)
    
    # Reordenar la ruta para que coincida en el mapa y en la salida mostrada en pantalla
    ruta_optima_str = " -> ".join(ruta_optima)
    coordenadas_ruta = [coord[ciudad] for ciudad in ruta_optima]

    return jsonify({
        'camino': ruta_optima_str,
        'coordenadas_ruta': coordenadas_ruta,
        'nodos_intermedios_encontrados': ruta_optima_str
    })

def encontrar_nodos_intermedios(coord, origen, destino, umbral_lat, umbral_lon):
    nodos_intermedios = []
    lat_origen, lon_origen = coord[origen]
    lat_destino, lon_destino = coord[destino]

    for ciudad, (lat, lon) in coord.items():
        if ciudad != origen and ciudad != destino:
            if (min(lat_origen, lat_destino) - umbral_lat <= lat <= max(lat_origen, lat_destino) + umbral_lat and
                min(lon_origen, lon_destino) - umbral_lon <= lon <= max(lon_origen, lon_destino) + umbral_lon):
                nodos_intermedios.append(ciudad)
    
    return nodos_intermedios

if __name__ == '__main__':
    app.run(debug=True)
