
#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor, TouchSensor, InfraredSensor
from pybricks.parameters import Port

import time
from estados import Robot, bug_2

ev3 = EV3Brick()

POTENCIA = 100
UMBRAL_LINEA = 110          # valor de color que distingue linea negra del suelo
KP_SEGUIDOR = 0.4
KI_SEGUIDOR = 0.001           # ganancia integral para el controlador de pared
TIEMPO_RETROCESO = 0.8       # segundos de retroceso antes de girar
DISTANCIA_PARED = 12           # distancia objetivo (cm) para rodeo de obstaculo

motor_izq = Motor(Port.B)
motor_der = Motor(Port.C)
us_sensor = UltrasonicSensor(Port.S4)
infra_sensor = InfraredSensor(Port.S1)
tactil_sensor = TouchSensor(Port.S2)
color_sensor = ColorSensor(Port.S3)


# ---------------------------------------------------------------------------
# Funciones de bajo nivel (sensores y actuadores)
# ---------------------------------------------------------------------------
def set_motor_speed(left, right):
    """Establece velocidad de las ruedas en rad/s."""
    motor_izq.run(left)
    motor_der.run(right)
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

# ---------------------------------------------------------------------------
# Bucle principal
# ---------------------------------------------------------------------------
def main():

    bot = bug_2()
    print('[INFO] Iniciando Bug2...')

    try:
        while True:
            # --- Leer sensores ---
            color_anterior=bot.color
            bot.color = color_sensor.reflection()
            bot.tactil = 1 if tactil_sensor.pressed() else 0
            bot.ultrasonido = us_sensor.distance() / 10.0
            bot.infra = infra_sensor.distance() / 10.0
            bot.ang_izq=motor_izq.angle()
            bot.ang_der=motor_der.angle()

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
                    motor_izq.reset()
                    motor_der.reset()

            if bot.estado == Robot.ESTADO_FINALIZAR:
                print('[INFO] Meta alcanzada. Finalizando.')
                set_motor_speed(0, 0)
                

            # --- Actuar motores (se niega por polaridad del modelo simulado) ---
            set_motor_speed(bot.der, bot.izq)

    except Exception as e:
        print(f'[ERROR] {e}')



while True:
    a=us_sensor.distance()
    b=infra_sensor.distance()
    c=1.756*a - 4.00
    print('distancia ultrasonido: ','distancia infrarrojo: ', infra_sensor.distance(), 'linalizacion:',c)

#if __name__ == '__main__':
#    main()
