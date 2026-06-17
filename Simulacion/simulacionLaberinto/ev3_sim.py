#EV3
import sys
import os
import time
import math
import numpy as np
import sim
import simConst
from estados import Robot, bug_2

print('[OK] Modulos cargados')

print('Conectando a CoppeliaSim...')
sim.simxFinish(-1)  # Cerrar conexiones previas

clientID = sim.simxStart('127.0.0.1',19997,True,True,5000,5)

if clientID != -1:
    print(f'[OK] Conectado. clientID={clientID}')
else:
    print('[ERROR] No se pudo conectar. Verifica que CoppeliaSim esta abierto.')
    print('         Tambien verifica que el puerto legacy (19997) esta habilitado.')

def get_handle(clientID, name):
    """Obtiene handle de un objeto por nombre."""
    err, handle = sim.simxGetObjectHandle(
        clientID, name, simConst.simx_opmode_blocking
    )
    if err != simConst.simx_return_ok:
        print(f'  WARN: No se encontro {name} (err={err})')
        return -1
    return handle

# Objetos del robot
body = get_handle(clientID, 'ev3_body')
motor_izq = get_handle(clientID, 'ev3_leftMotor')
motor_der = get_handle(clientID, 'ev3_rightMotor')
ultrasonido_sensor = get_handle(clientID, 'ev3_us')
tactil_sensor = get_handle(clientID, 'ev3_tactil')
color_sensor = get_handle(clientID, 'ev3_colorSensor')

def set_motor_speed(left, right):
    """Velocidad de ruedas en rad/s."""
    sim.simxSetJointTargetVelocity(clientID, motor_izq, left, simConst.simx_opmode_oneshot)
    sim.simxSetJointTargetVelocity(clientID, motor_der, right, simConst.simx_opmode_oneshot)

def read_ultrasonic(sensor):
    """Distancia del sensor ultrasonico en cm. 255 si no detecta."""
    err, state, point, handle, normal = sim.simxReadProximitySensor(
        clientID, sensor, simConst.simx_opmode_streaming
    )
    if err == simConst.simx_return_ok and state:
        dist = math.sqrt(point[0]**2 + point[1]**2 + point[2]**2)
        return round(dist * 100, 1)
    return 255

def read_encoder(motor):
    err, pos = sim.simxGetJointPosition(
        clientID,
        motor,
        simConst.simx_opmode_buffer
    )

    if err == simConst.simx_return_ok:
        return pos

    return None

def tactil(sensor):
    if read_ultrasonic(sensor)<3:
        return 1
    else:
        return 0


def read_color_reflection():
    """
    Reflexion del sensor de color (0=negro, 100=blanco).
    Analiza la region central de la imagen del vision sensor.
    """
    err, res, img = sim.simxGetVisionSensorImage(
        clientID, color_sensor, 0, simConst.simx_opmode_streaming
    )
    if err != simConst.simx_return_ok or res[0] == 0:
        return None
    
    # Convertir imagen 1D a array (RGB, [resX, resY])
    img_array = np.array(img, dtype=np.int32).reshape(res[1], res[0], 3)
    
    # Region central (~20%)
    cx, cy = res[0], res[1]
    m = min(res[0], res[1])
    # Escala de grises ponderada
    gray = (0.299 * img_array[:,:,0].astype(np.float32) +
            0.587 * img_array[:,:,1].astype(np.float32) +
            0.114 * img_array[:,:,2].astype(np.float32))
    
    return round(float(np.mean(gray)) / 255.0 * 100.0, 2)+100


def read_gyro(giro_0):
    """Angulo de orientacion en grados (yaw)."""
    err, euler = sim.simxGetObjectOrientation(
        clientID, body, -1, simConst.simx_opmode_streaming
    )
    if err == simConst.simx_return_ok:
        angle = math.degrees(euler[2])-giro_0
        return -round(((angle + 180) % 360) - 180, 1)
    return 0.0

def reset_gyro():
    err, euler = sim.simxGetObjectOrientation(
        clientID, body, -1, simConst.simx_opmode_blocking
    )
    if err == simConst.simx_return_ok:
        return math.degrees(euler[2])
    return 0.0

bot = bug_2()

giro_0 = reset_gyro()
kp = 0.005
potencia = 0.7

sim.simxGetJointPosition(clientID,motor_izq, simConst.simx_opmode_streaming)
sim.simxGetJointPosition(clientID,motor_der, simConst.simx_opmode_streaming)
enc_prev = None
encoder_acumulado = 0

lista_estados = [
    "AVANCE",
    "GIRO_DER",
    "GIRO_IZQ",
    "ENTRAR_PASILLO",
    "RETROCESO"
]

while True:
    bot.ultrasonido = read_ultrasonic(
        ultrasonido_sensor
    )

    bot.tactil = tactil(
        tactil_sensor
    )

    bot.angulo = read_gyro(
        giro_0
    )
    #print(f"Angulo: {bot.angulo}")
    # ENCODER ACUMULADO

    enc = read_encoder(motor_izq)
    if enc is not None:
        if enc != 255:

            enc = math.degrees(enc)

            if enc_prev is None:
                enc_prev = enc

            delta = enc - enc_prev

            if delta > 180:
                delta -= 360
            elif delta < -180:
                delta += 360

            encoder_acumulado += abs(delta)
            enc_prev = enc

    bot.encoder = encoder_acumulado

    #STATES

    estado_anterior = bot.estado
    error = 0 - bot.angulo
    bot.states(potencia,error,kp)

    # CAMBIO DE ESTADO
    if estado_anterior != bot.estado:

        print(lista_estados[bot.estado])

        bot.tiempo_inicial = time.time()

        encoder_acumulado = 0
        bot.encoder = 0

        if bot.estado in [
            bot.GIRO_DER,
            bot.GIRO_IZQ,
            bot.AVANCE
            #bot.RETROCESO
        ]:

            giro_0 = reset_gyro()
    #MOTORES

    set_motor_speed(bot.izq,bot.der)