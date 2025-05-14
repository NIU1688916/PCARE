import json
from flask import Flask, request, jsonify
from pyngrok import ngrok
import os
import threading
from ..estado import Planta

class RobotServer:
    def __init__(self, estado):
        """
        Inicializa el servidor Flask y el estado del robot.
        :param estado: Instancia del estado del robot.
        """
        self.app = Flask(__name__)
        self.estado = estado
        self._setup_routes()

    def _setup_routes(self):
        """
        Configura las rutas del servidor Flask.
        """
        @self.app.route('/datos_planta', methods=['POST'])
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
                # Extraer valores de los datos recibidos
                nombre = datos.get("nombre")
                humedad_opt = datos.get("humedad_opt")
                luz_opt = datos.get("luz_opt")

                planta = Planta(nombre, humedad_opt, luz_opt)
                planta = Planta(nombre, humedad_opt, luz_opt)
                self.estado.set_planta(planta)
                return jsonify({'message': 'Datos recibidos y guardados correctamente'}), 200
            except ValueError as ve:
                return jsonify({'error': str(ve)}), 400
            except Exception as e:
                return jsonify({'error': f"Error al guardar los datos de la planta: {str(e)}"}), 500

        @self.app.route('/datos_sensor', methods=['GET'])
        def obtener_datos_sensor():
            """
            Obtiene las lecturas de los sensores del robot.
            :return: Respuesta JSON con las lecturas o un mensaje de error.
            """
            try:
                humedad, luminocidad, intensidad_wifi = self.estado.celda_actual.lecturas.tomar_lecturas()
                return jsonify({
                    'humedad': humedad,
                    'luminocidad': luminocidad,
                    'intensidad_wifi': intensidad_wifi
                }), 200
            except Exception as e:
                jsonify({'error': str(e)}), 500

        @self.app.route('/mapa_wifi', methods=['GET'])
        def obtener_mapa_wifi():
            """
            Genera y retorna el mapa de intensidad WiFi.
            :return: Archivo del mapa de intensidad WiFi o un mensaje de error.
            """
            try:
                # Generar el mapa de intensidad WiFi
                mapa_wifi_path = self.estado.generar_mapa_wifi() 

                # Verificar si el archivo existe
                if not os.path.exists(mapa_wifi_path):
                    raise FileNotFoundError(f"El archivo del mapa de intensidad WiFi no existe en la ruta: {mapa_wifi_path}")
                
                # Leer el archivo del mapa de intensidad WiFi
                with open(mapa_wifi_path, 'rb') as mapa_wifi_file:
                    mapa_wifi_data = mapa_wifi_file.read()
                
                # Retornar el archivo como respuesta
                return (mapa_wifi_data, 200, {'Content-Type': 'image/png'})
            except Exception as e:
                return jsonify({'error': f"No se pudo obtener el mapa de intensidad WiFi: {str(e)}"}), 500
            

        @self.app.route('/mapa_actual', methods=['GET'])
        def obtener_mapa_actual():
            """
            Obtiene el mapa actual del estado del robot.
            :return: Archivo del mapa actual o un mensaje de error.
            """
            try:
                # Generar el mapa actual
                #TODO: Implementar la lógica para generar el mapa actual del SLAM como lo ve el robot
                return (mapa_actual_data, 200, {'Content-Type': 'image/png'})
            except Exception as e:
                return jsonify({'error': f"No se pudo obtener el mapa actual: {str(e)}"}), 500

    def run(self):
        """
        Inicia el servidor Flask con ngrok.
        """
        public_url = ngrok.connect(5000)
        print(f"NGROK URL: {public_url}")
        self.app.run(port=5000)
        
    def run_in_thread(self):
        """
        Ejecuta el servidor Flask en un hilo separado.
        """
        server_thread = threading.Thread(target=self.run, daemon=True)
        server_thread.start()