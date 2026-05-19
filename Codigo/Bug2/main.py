#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor, TouchSensor, GyroSensor
from pybricks.parameters import Port
from pybricks.tools import wait, StopWatch
from pybricks.parameters import Axis
from Estados import Robot

bot = Robot()

ev3 = EV3Brick()

# Initialize a motor at port B.
motor_izq = Motor(Port.B)
motor_der = Motor(Port.C)

tactil_sensor = TouchSensor(Port.S1)
color_sensor = ColorSensor(Port.S2)
giroscopio = GyroSensor(Port.S3)
ultrasonido_sensor = UltrasonicSensor(Port.S4)

# Write your program here

# Play a sound.
ev3.speaker.beep()
# Play another beep sound.
ev3.speaker.beep(frequency=1000, duration=500)

potencia = 60
ref_color = 60
ref_distancia = 45

while True:
    bot.color = color_sensor.reflection()
    bot.tactil = tactil_sensor.pressed()
    bot.ultrasonido = ultrasonido_sensor.distance()
    bot.angulo = giroscopio.angle()

    if bot.estado == Robot.ESTADO_SEGUIR_LINEA:
        error = ref_color - bot.color
        bot.seguir_linea(1, error, potencia)
    elif bot.estado == Robot.ESTADO_RODEO:
        error = ref_distancia - bot.ultrasonido
        bot.rodeo(1, error, potencia)
    elif bot.estado == Robot.ESTADO_GIRO_IZQ:
        bot.giro_izq(potencia, 90)
    elif bot.estado == Robot.ESTADO_GIRO_DER:
        bot.giro_der(potencia, 90)
    elif bot.estado == Robot.ESTADO_AVANCE_CIEGO:
        bot.avance_ciego(potencia, 5)
    elif bot.estado == Robot.ESTADO_FINALIZAR:
        break

    # Ejecutar motores
    motor_izq.run(bot.izq)
    motor_der.run(bot.der)
