import numpy as np
import time


class Robot:
    """
    Robot EV3 con comportamientos definidos por estados.

    Estados:
        0 ESTADO_SEGUIR_LINEA: sigue la linea negra en el suelo.
        1 ESTADO_RODEO:        rodea un obstaculo manteniendo distancia lateral.
        2 ESTADO_GIRO_IZQ:     gira 90 grados a la izquierda.
        3 ESTADO_GIRO_DER:     gira 90 grados a la derecha.
        4 ESTADO_AVANCE_CIEGO: avanza recto sin sensar la linea.
        5 ESTADO_FINALIZAR:    meta alcanzada, detener.
        6 RETROCESO:           retrocede para evitar colision.
        7 GIRO_SEGUIDOR:       gira buscando reencontrar la linea negra.
    """
    ESTADO_SEGUIR_LINEA = 0
    ESTADO_RODEO = 1
    ESTADO_GIRO_IZQ = 2
    ESTADO_GIRO_DER = 3
    ESTADO_AVANCE_CIEGO = 4
    ESTADO_FINALIZAR = 5
    RETROCESO = 6
    GIRO_SEGUIDOR = 7

    def __init__(self):
        self.izq = 0.0
        self.der = 0.0
        self.angulo = 0.0
        self.color = 0.0
        self.tactil = False
        self.ultrasonido = 0.0
        self.estado = self.ESTADO_SEGUIR_LINEA
        self.tiempo_inicial = 0.0

    def transiciones(self, objetivo, condicion):
        """Transita al estado objetivo si la condicion se cumple."""
        if condicion:
            self.estado = objetivo
        return self.estado

    def lazo_motores(self, error, kp, potencia, max_dif):
        """
        Control proporcional de motores para mantener distancia lateral.
        Ajusta velocidades segun error respecto a distancia objetivo.
        """
        self.izq = potencia - error * kp
        self.der = potencia + error * kp
        if np.abs(self.izq - self.der) > max_dif:
            self.izq = potencia - max_dif*np.sign(error)
            self.der = potencia + max_dif*np.sign(error)
            


class bug_2(Robot):
    """
    Implementacion del algoritmo Bug2.
    Combina seguidor de linea con rodeo de obstaculos usando wall-following.
    """

    def states(self, potencia, kp, umbral, error_pared, tiempo_fin, max_dif):
        """
        Ejecuta la logica correspondiente al estado actual.

        Args:
            potencia: velocidad base de los motores.
            kp: ganancia proporcional del controlador de pared.
            umbral: valor de color que distingue linea negra del suelo (110).
            error_pared: error de distancia para el estado RODEO.
            tiempo_fin: duracion del retroceso en segundos.
        """
        if self.estado == self.ESTADO_SEGUIR_LINEA:
            # Correccion proporcional para mantener la linea bajo el sensor
            if self.color < umbral:
                self.izq = potencia + kp
                self.der = potencia - kp
            else:
                self.der = potencia + kp
                self.izq = potencia - kp
            self.transiciones(self.ESTADO_FINALIZAR, self.color > 200)
            self.transiciones(self.RETROCESO, self.tactil == 1)

        elif self.estado == self.ESTADO_RODEO:
            # Wall-following: mantener distancia lateral al obstaculo
            self.lazo_motores(error_pared, kp, potencia, max_dif)
            self.transiciones(self.ESTADO_FINALIZAR, self.color > 200)
            self.transiciones(self.GIRO_SEGUIDOR, self.color > umbral)
            self.transiciones(self.ESTADO_GIRO_DER, self.ultrasonido > 20)

        elif self.estado == self.ESTADO_GIRO_IZQ:
            self.izq = -potencia
            self.der = potencia
            self.transiciones(self.ESTADO_RODEO, self.angulo <= -90)

        elif self.estado == self.ESTADO_GIRO_DER:
            self.izq = potencia
            self.der = -potencia
            self.transiciones(self.GIRO_SEGUIDOR, self.color > umbral)
            self.transiciones(self.ESTADO_AVANCE_CIEGO, self.angulo > 90)

        elif self.estado == self.ESTADO_AVANCE_CIEGO:
            self.izq = potencia
            self.der = potencia
            self.transiciones(self.GIRO_SEGUIDOR, self.color > umbral)
            self.transiciones(self.ESTADO_RODEO, self.ultrasonido <= 50)

        elif self.estado == self.RETROCESO:
            self.izq = -potencia
            self.der = -potencia
            self.transiciones(
                self.ESTADO_GIRO_IZQ,
                tiempo_fin < (time.time() - self.tiempo_inicial),
            )

        elif self.estado == self.GIRO_SEGUIDOR:
            self.izq = -potencia
            self.der = potencia
            self.transiciones(self.ESTADO_FINALIZAR, self.color > 200)
            self.transiciones(self.ESTADO_SEGUIR_LINEA, self.angulo <= -70)

        elif self.estado == self.ESTADO_FINALIZAR:
            return self.ESTADO_FINALIZAR
