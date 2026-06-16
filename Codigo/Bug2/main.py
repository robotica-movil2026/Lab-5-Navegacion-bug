#!/usr/bin/env pybricks-micropython
from Codigo.Bug2.Estados import Robot
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor, TouchSensor, GyroSensor
from pybricks.parameters import Port
from pybricks.tools import wait, StopWatch

from Estados import bug_2

bot = bug_2()

ev3 = EV3Brick()

# Initialize a motor at port B.
motor_izq = Motor(Port.B)
motor_der = Motor(Port.C)

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
ref_color = 10
ref_distancia = 150
umbral=15

lista_estados=["ESTADO_SEGUIR_LINEA",
    "ESTADO_RODEO",
    "ESTADO_GIRO_IZQ",
    "ESTADO_GIRO_DER",
    "ESTADO_AVANCE_CIEGO",
    "ESTADO_FINALIZAR",
    "RETROCESO",
    "GIRO_SEGUIDOR"]

while True:
    bot.color = color_sensor.reflection()
    #print(bot.ultrasonido)
    #print(lista_estados[bot.estado])
    bot.tactil = tactil_sensor.pressed()
    bot.ultrasonido = ultrasonido_sensor.distance()
    bot.angulo = giroscopio.angle()
    estado_anterior = bot.estado
    bot.states(potencia, 0.1, umbral, 10, 1)

    if estado_anterior != bot.estado:
        print(lista_estados[bot.estado])
        if bot.estado in [2,3,7]:
            giroscopio.reset_angle(0)
    
    if bot.estado == 5:
        break
    # Ejecutar motores
    motor_izq.run(bot.izq)
    motor_der.run(bot.der)

'''
while True:
    bot.color = color_sensor.reflection()
    bot.tactil = tactil_sensor.pressed()
    bot.ultrasonido = ultrasonido_sensor.distance()
    bot.angulo = giroscopio.angle()
    print(bot.ultrasonido)
    print(bot.tactil)
    if bot.tactil:
        giroscopio.reset_angle(0)
    wait(1000)
'''

#107 -150
#500