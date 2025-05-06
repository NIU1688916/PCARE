from estado import robot_estado

def recibir_datos_app():
    return {"tipo_planta": "Cactus", "modo_operacion": "automatico"}

def adaptar_funcionamiento_robot(datos):
    robot_estado.planta = Planta("Cactus", 20, 200, 5)
    robot_estado.modo_automatico = datos["modo_operacion"] == "automatico"