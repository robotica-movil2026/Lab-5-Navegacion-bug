#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor, TouchSensor, GyroSensor
from pybricks.parameters import Port
from pybricks.tools import wait, StopWatch

from Estados import Robot

bot = Robot()

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
umbral=10

lista_estados=["ESTADO_SEGUIR_LINEA",
    "ESTADO_RODEO",
    "ESTADO_GIRO_IZQ",
    "ESTADO_GIRO_DER",
    "ESTADO_AVANCE_CIEGO",
    "ESTADO_FINALIZAR",
    "RETROCESO" ]

while True:
    bot.color = color_sensor.reflection()
    print(bot.ultrasonido)
    print(lista_estados[bot.estado])
    bot.tactil = tactil_sensor.pressed()
    bot.ultrasonido = ultrasonido_sensor.distance()
    bot.angulo = giroscopio.angle()

    if bot.estado == Robot.ESTADO_SEGUIR_LINEA:
        error = ref_color - bot.color
        bot.seguir_linea(10, error, potencia,umbral)
    elif bot.estado == Robot.ESTADO_RODEO:
        error = ref_distancia - bot.ultrasonido
        bot.rodeo(0.5, error, potencia, umbral)
    elif bot.estado == Robot.ESTADO_GIRO_IZQ:
        bot.giro_izq(potencia, 90)
    elif bot.estado == Robot.ESTADO_GIRO_DER:
        bot.giro_der(potencia, 90)
    elif bot.estado == Robot.ESTADO_AVANCE_CIEGO:
        bot.avance_ciego(potencia, 0.5)
    elif bot.estado == Robot.ESTADO_FINALIZAR:
        break
    elif bot.estado == Robot.RETROCESO:
        bot.retroceso_ciego(potencia, 1 )

    # Ejecutar motores
    motor_izq.run(bot.izq)
    motor_der.run(bot.der)
