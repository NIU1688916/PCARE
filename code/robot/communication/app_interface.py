import json
from flask import Flask, request, jsonify
from pyngrok import ngrok
from arduino_connection import ArduinoNano
import subprocess
import os
app = Flask(__name__)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'config.json')

def leer_datos_planta(path=CONFIG_PATH):
    """
    Lee los datos de configuración de la planta desde un archivo JSON.
    :param path: Ruta del archivo JSON.
    :return: Diccionario con los datos de configuración o un mensaje de error.
    """
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"El archivo {path} no existe.")
        with open(path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"error": "El archivo de configuración contiene un formato JSON inválido."}
    except Exception as e:
        return {"error": f"Error al leer los datos de la planta: {str(e)}"}

    
def obtener_intensidad_wifi():
    """
    Obtiene la intensidad de la señal WiFi usando el comando `iwconfig`.
    :return: Intensidad de la señal WiFi como cadena, o None si ocurre un error.
    """
    try:
        result = subprocess.check_output(['iwconfig'], stderr=subprocess.STDOUT, universal_newlines=True)
        for line in result.split('\n'):
            if 'Signal level' in line:
                # Extraer el nivel de señal
                parts = line.split('Signal level=')
                if len(parts) > 1:
                    return parts[1].split(' ')[0]  # Devuelve el valor de la señal
        return "No se pudo obtener la intensidad de la señal"
    except Exception as e:
        return f"Error al obtener la intensidad de la señal: {str(e)}"


@app.route('/datos_planta', methods=['POST'])
def enviar_datos_planta():
    """
    Guarda los datos de configuración de la planta en un archivo JSON.
    :return: Respuesta JSON indicando éxito o error.
    """
    try:
        datos = request.get_json()
        if not datos:
            raise ValueError("No se recibieron datos en la solicitud.")
        
        # Validar que los datos contengan las claves necesarias
        required_keys = ["plant_name", "target_humidity", "target_luminosity"]
        for key in required_keys:
            if key not in datos:
                raise ValueError(f"Falta la clave requerida: {key}")
        
        with open(CONFIG_PATH, 'w') as f:
            json.dump(datos, f, indent=4)
        return jsonify({'message': 'Datos recibidos y guardados correctamente'}), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': f"Error al guardar los datos de la planta: {str(e)}"}), 500

@app.route('/datos_sensor', methods=['GET'])
def obtener_datos_sensor():
    try:
        arduino = ArduinoNano(port='/dev/ttyUSB0') 
        humedad = arduino.read_sensor("SENSOR:HUMEDAD")
        luminocidad = arduino.read_sensor("SENSOR:LUZ")
        intensidad_wifi = obtener_intensidad_wifi()
        
        return jsonify({
            'humedad': humedad,
            'luminocidad': luminocidad,
            'intensidad_wifi': intensidad_wifi
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    

@app.route('/mapa', methods=['GET'])
def obtener_mapa():
        """
        Retorna el mapa generado por OpenSLAM.
        :return: Archivo del mapa en formato adecuado o un mensaje de error.
        """
        try:
            # Ruta del archivo del mapa generado por OpenSLAM
            mapa_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'maps', 'mapa.pgm') 
            # Leer el archivo del mapa
            if not os.path.exists(mapa_path):
                raise FileNotFoundError(f"El archivo del mapa no existe en la ruta: {mapa_path}")
            with open(mapa_path, 'rb') as mapa_file:
                mapa_data = mapa_file.read()
            # Retornar el archivo como respuesta
            return (mapa_data, 200, {'Content-Type': 'image/x-portable-graymap'})
        except Exception as e:
            return jsonify({'error': f"No se pudo obtener el mapa: {str(e)}"}), 500

if __name__ == '__main__':
    # Inicia el túnel NGROK
    public_url = ngrok.connect(5000)
    print(f"NGROK URL: {public_url}")
    
    # Inicia el servidor Flask
    app.run(port=5000)