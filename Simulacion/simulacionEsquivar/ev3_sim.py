
"""
Controlador Bug2 para robot EV3 en CoppeliaSim.
Implementa navegacion seguidor de linea con rodeo de obstaculos.
"""
import sys
import time
import math
import signal
import numpy as np
import sim
import simConst
from estados import Robot, bug_2

# ---------------------------------------------------------------------------
# Configuracion
# ---------------------------------------------------------------------------
SIM_HOST = '127.0.0.1'
SIM_PORT = 19999
SIM_TIMEOUT = 5000
SIM_RETRIES = 5

POTENCIA = 1.0
UMBRAL_LINEA = 110          # valor de color que distingue linea negra del suelo
KP_SEGUIDOR = 0.4
KI_SEGUIDOR = 0.001           # ganancia integral para el controlador de pared
TIEMPO_RETROCESO = 0.8       # segundos de retroceso antes de girar
DISTANCIA_PARED = 12           # distancia objetivo (cm) para rodeo de obstaculo

# ---------------------------------------------------------------------------
# Conexion y handles
# ---------------------------------------------------------------------------
print('[OK] Modulos cargados')
print('Conectando a CoppeliaSim...')

sim.simxFinish(-1)
clientID = sim.simxStart(SIM_HOST, SIM_PORT, True, True, SIM_TIMEOUT, SIM_RETRIES)

if clientID == -1:
    print('[ERROR] No se pudo conectar. Verifica que CoppeliaSim esta abierto.')
    print('         Tambien verifica que el puerto legacy (19997) esta habilitado.')
    sys.exit(1)

print(f'[OK] Conectado. clientID={clientID}')


def obtener_handle(nombre):
    """Obtiene handle de un objeto en la escena por su nombre."""
    err, handle = sim.simxGetObjectHandle(
        clientID, nombre, simConst.simx_opmode_blocking
    )
    if err != simConst.simx_return_ok:
        raise RuntimeError(f'No se encontro "{nombre}" (err={err})')
    return handle


body = obtener_handle('ev3_body')
motor_izq = obtener_handle('ev3_leftMotor')
motor_der = obtener_handle('ev3_rightMotor')
us_sensor = obtener_handle('ev3_us')
infra_sensor = obtener_handle('ev3_infra')
tactil_sensor = obtener_handle('ev3_tactil')
color_sensor = obtener_handle('ev3_colorSensor')


# ---------------------------------------------------------------------------
# Funciones de bajo nivel (sensores y actuadores)
# ---------------------------------------------------------------------------
def set_motor_speed(left, right):
    """Establece velocidad de las ruedas en rad/s."""
    sim.simxSetJointTargetVelocity(clientID, motor_izq, left, simConst.simx_opmode_oneshot)
    sim.simxSetJointTargetVelocity(clientID, motor_der, right, simConst.simx_opmode_oneshot)


def leer_proximidad(sensor):
    """Lee sensor de proximidad. Retorna distancia en cm o 255 si no detecta."""
    err, state, point, _, _ = sim.simxReadProximitySensor(
        clientID, sensor, simConst.simx_opmode_streaming
    )
    if err == simConst.simx_return_ok and state:
        dist = math.sqrt(point[0] ** 2 + point[1] ** 2 + point[2] ** 2)
        return round(dist * 100, 1)
    return 255


def leer_tactil():
    """Retorna True si el sensor tactil esta presionado (distancia < 3 cm)."""
    return leer_proximidad(tactil_sensor) < 3


def leer_color():
    """
    Reflexion del sensor de color (0=negro ~100=blanco, >110=fuera de linea).
    Analiza la region central de la imagen del vision sensor.
    Retorna None si el sensor no esta disponible.
    """
    err, res, img = sim.simxGetVisionSensorImage(
        clientID, color_sensor, 0, simConst.simx_opmode_streaming
    )
    if err != simConst.simx_return_ok or res[0] == 0:
        return None

    img_array = np.array(img, dtype=np.int32).reshape(res[1], res[0], 3)
    gray = (img_array[:, :, 1].astype(np.float32)# +
            #0.587 * img_array[:, :, 1].astype(np.float32) +
            #0.114 * img_array[:, :, 2].astype(np.float32)
            )
    return round(float(np.mean(gray)) / 255.0 * 100.0, 2) + 100


def leer_giro(giro_referencia):
    """Angulo relativo de orientacion (yaw) en grados respecto a giro_referencia."""
    err, euler = sim.simxGetObjectOrientation(
        clientID, body, -1, simConst.simx_opmode_streaming
    )
    if err == simConst.simx_return_ok:
        angle = math.degrees(euler[2]) - giro_referencia
        return -round(((angle + 180) % 360) - 180, 1)
    return 0.0


def resetear_giro():
    """Lee el angulo absoluto (yaw) para usarlo como nuevo cero."""
    err, euler = sim.simxGetObjectOrientation(
        clientID, body, -1, simConst.simx_opmode_blocking
    )
    if err == simConst.simx_return_ok:
        return math.degrees(euler[2])
    return 0.0


def limpiar_y_salir(signum=None, frame=None):
    """Detiene motores y cierra conexion con CoppeliaSim."""
    print('\n[INFO] Finalizando...')
    try:
        set_motor_speed(0, 0)
    except Exception:
        pass
    sim.simxFinish(clientID)
    sys.exit(0)


# ---------------------------------------------------------------------------
# Mapa de estados a nombres legibles
# ---------------------------------------------------------------------------
NOMBRES_ESTADO = {
    Robot.ESTADO_SEGUIR_LINEA: "SEGUIR_LINEA",
    Robot.ESTADO_RODEO: "RODEO",
    Robot.ESTADO_GIRO_IZQ: "GIRO_IZQ",
    Robot.ESTADO_GIRO_DER: "GIRO_DER",
    Robot.ESTADO_AVANCE_CIEGO: "AVANCE_CIEGO",
    Robot.ESTADO_FINALIZAR: "FINALIZAR",
    Robot.RETROCESO: "RETROCESO",
    Robot.GIRO_SEGUIDOR: "GIRO_SEGUIDOR",
    Robot.AVANCE_2: "AVANCE_2",
}
color_anterior=0

#while True:
#    print(leer_color())
#    set_motor_speed(0.2, -0.2)

# ---------------------------------------------------------------------------
# Bucle principal
# ---------------------------------------------------------------------------
def main():
    signal.signal(signal.SIGINT, limpiar_y_salir)

    bot = bug_2()
    giro_0 = resetear_giro()
    print('[INFO] Iniciando Bug2...')

    try:
        while True:
            # --- Leer sensores ---
            color_anterior=bot.color
            bot.color = leer_color()
            if bot.color is None:
                bot.color = 100

            bot.tactil = 1 if leer_tactil() else 0
            bot.ultrasonido = leer_proximidad(us_sensor)
            bot.angulo = leer_giro(giro_0)
            bot.infra = leer_proximidad(infra_sensor)

            # --- Ejecutar maquina de estados ---
            estado_anterior = bot.estado
            error_pared = bot.infra - bot.ultrasonido if bot.estado == Robot.ESTADO_RODEO else 0
            ki = 0
            if bot.estado==Robot.ESTADO_SEGUIR_LINEA:
                kp=1
                #if color_anterior!=bot.color:
                #    print(bot.color)
            if bot.estado == Robot.ESTADO_RODEO:
                kp=KP_SEGUIDOR
                ki=KI_SEGUIDOR
                print(round(error_pared,2), round(bot.izq,2), round(bot.der,2))
            bot.states(POTENCIA, kp, ki, UMBRAL_LINEA, error_pared, TIEMPO_RETROCESO, 0.3)

            # --- Transicion entre estados ---
            if estado_anterior != bot.estado:
                bot.tiempo_inicial = time.time()
                print(f'[ESTADO] -> {NOMBRES_ESTADO[bot.estado]}')
                if bot.estado in (Robot.ESTADO_GIRO_IZQ, Robot.ESTADO_GIRO_DER, Robot.GIRO_SEGUIDOR):
                    giro_0 = resetear_giro()

            if bot.estado == Robot.ESTADO_FINALIZAR:
                print('[INFO] Meta alcanzada. Finalizando.')
                set_motor_speed(0, 0)
                

            # --- Actuar motores (se niega por polaridad del modelo simulado) ---
            set_motor_speed(bot.der, bot.izq)

    except Exception as e:
        print(f'[ERROR] {e}')
    finally:
        limpiar_y_salir()


if __name__ == '__main__':
    main()
