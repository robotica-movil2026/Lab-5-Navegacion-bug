#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor, TouchSensor, GyroSensor
from pybricks.parameters import Port


from Estados import bug_2
import time
import math
#import numpy as np

bot = bug_2()

ev3 = EV3Brick()

# Initialize a motor at port B.
motor_izq = Motor(Port.B)
motor_der = Motor(Port.C)
motor_izq.reset_angle(0)
motor_der.reset_angle(0)

tactil_sensor = TouchSensor(Port.S2)
color_sensor = ColorSensor(Port.S4)
giroscopio = GyroSensor(Port.S1)
ultrasonido_sensor = UltrasonicSensor(Port.S3)

# Write your program here

# Play a sound.
ev3.speaker.beep()
# Play another beep sound.
ev3.speaker.beep(frequency=1000, duration=500)

potencia = 120
#ref_color = 10
#ref_distancia = 150
umbral=17
seguir = 20
kp = 0.5
enc_prev = None
encoder_acumulado = 0

lista_estados = [
    "ESTADO_SEGUIR_LINEA",
    "ESTADO_RODEO",
    "ESTADO_GIRO_IZQ",
    "ESTADO_GIRO_DER",
    "ESTADO_AVANCE_CIEGO",
    "ESTADO_FINALIZAR",
    "RETROCESO",
    "GIRO_SEGUIDOR",
    "AVANCE_ESQUINA",
    "GIRO_BUSCA_PARED",
    "GIRO_SEGUIDOR_1",
    "AVANCE_LINEA_1",
    "GIRO_SEGUIDOR_2",
    "AVANCE_LINEA_2"
]

giroscopio.reset_angle(0)
while True:
    bot.color = color_sensor.reflection()
    #print(bot.color)
    if bot.color is None:
        bot.color = 100
        
    bot.tactil = tactil_sensor.pressed()
    bot.ultrasonido = ultrasonido_sensor.distance()
    #print(bot.ultrasonido)
    bot.angulo = giroscopio.angle()
    #print(bot.angulo)
    enc = motor_izq.angle()

    if enc is not None:
        #enc = math.degrees(enc)

        if enc_prev is None:
            enc_prev = enc

        delta = enc - enc_prev

        if delta > 180:
            delta -= 360
        if delta < -180:
            delta += 360

        encoder_acumulado += abs(delta)
        enc_prev = enc
    #print(enc)
    bot.encoder = encoder_acumulado
    
    #ULTRASONIDO Y STATES

    error = 0
    if bot.estado == bot.ESTADO_RODEO:
            error = bot.ultrasonido-60
            #error = max(min(error, 8),-8)
    estado_anterior = bot.estado

    bot.states(potencia, seguir, kp, umbral, error, 1.2)

    # RESETS AL CAMBIAR DE ESTADO
    print(lista_estados[bot.estado])
    if estado_anterior != bot.estado:

        bot.tiempo_inicial = time.time()
        encoder_acumulado = 0
        bot.encoder = 0

        if bot.estado in [
            bot.ESTADO_GIRO_IZQ,
            bot.ESTADO_GIRO_DER,
            bot.GIRO_BUSCA_PARED,
            bot.ESTADO_RODEO,
            bot.GIRO_SEGUIDOR_1,
            bot.GIRO_SEGUIDOR_2,
        ]:
            motor_izq.reset_angle(0)
            motor_der.reset_angle(0)
            #giroscopio.reset_angle(0)

    #TERMINAR

    if bot.estado == bot.ESTADO_FINALIZAR:
        break

    # Ejecutar motores
    motor_izq.run(bot.izq)
    motor_der.run(bot.der)

