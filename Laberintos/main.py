#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor, TouchSensor, GyroSensor
from pybricks.parameters import Port


from Estados import bug_2
#import time
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

potencia = 100
kp = 0.1
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
    bot.tactil = tactil_sensor.pressed()
    bot.ultrasonido = ultrasonido_sensor.distance()
    bot.angulo = giroscopio.angle()
    enc = motor_izq.angle()

    if enc is not None:
        enc = math.degrees(enc)

        if enc_prev is None:
            enc_prev = enc

        delta = enc - enc_prev

        if delta > 180:
            delta -= 360
        if delta < -180:
            delta += 360

        encoder_acumulado += abs(delta)
        enc_prev = enc
    
    bot.encoder = encoder_acumulado
    
    #STATES

    estado_anterior = bot.estado
    error = bot.anguloobjetivo - bot.angulo
    bot.states(potencia,error,kp)

    # CAMBIO DE ESTADO
    if estado_anterior != bot.estado:

        print(lista_estados[bot.estado])

        #bot.tiempo_inicial = time.time()

        encoder_acumulado = 0
        bot.encoder = 0
        motor_izq.reset_angle(0)
        motor_der.reset_angle(0)

    #TERMINAR

    if bot.estado == bot.ESTADO_FINALIZAR:
        break


    # Ejecutar motores
    motor_izq.run(bot.izq)
    motor_der.run(bot.der)