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
    AVANCE_2 = 8

    def __init__(self):
        self.izq = 0.0
        self.der = 0.0
        self.angulo = 0.0
        self.color = 0.0
        self.tactil = False
        self.ultrasonido = 0.0
        self.estado = self.ESTADO_SEGUIR_LINEA
        self.tiempo_inicial = 0.0
        self.infra = 0.0
        self.error_integral = 0.0
        self.ang_izq=0.0
        self.ang_der=0.0

    def transiciones(self, objetivo, condicion):
        """Transita al estado objetivo si la condicion se cumple."""
        if condicion:
            self.estado = objetivo
        return self.estado

    def lazo_motores(self, error, kp, ki, potencia, max_dif):
        """
        Control proporcional-integral de motores para mantener distancia lateral.
        Ajusta velocidades segun error respecto a distancia objetivo.
        """
        if self.ultrasonido<20:
            self.error_integral += error
            control = error * kp + self.error_integral * ki
            self.izq = potencia - control
            self.der = potencia + control
        else:
            self.izq = potencia
            self.der = potencia
            self.error_integral = 0.0
            
        if np.abs(self.izq - self.der) > max_dif:
            control_sign = np.sign(error * kp + self.error_integral * ki)
            if control_sign == 0: control_sign = np.sign(error)
            self.izq = potencia - max_dif*control_sign
            self.der = potencia + max_dif*control_sign
            


class bug_2(Robot):
    def __init__(self):
        super().__init__()
        self.Angulo_seguimiento = 120
        self.Umbral_final=70
        self.Angulo_rotacion=90
        self.distancia_objetivo=20
        self.distancia_recuperacion=50

    """
    Implementacion del algoritmo Bug2.
    Combina seguidor de linea con rodeo de obstaculos usando wall-following.
    """

    def states(self, potencia, kp, ki, umbral, error_pared, tiempo_fin, max_dif):
        """
        Ejecuta la logica correspondiente al estado actual.

        Args:
            potencia: velocidad base de los motores.
            kp: ganancia proporcional del controlador de pared.
            ki: ganancia integral del controlador de pared.
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
            self.transiciones(self.ESTADO_FINALIZAR, self.color < self.Umbral_final)
            self.transiciones(self.RETROCESO, self.tactil == 1)

        elif self.estado == self.ESTADO_RODEO:
            # Wall-following: mantener distancia lateral al obstaculo
            self.lazo_motores(error_pared, kp, ki, potencia, max_dif)
            self.transiciones(self.ESTADO_FINALIZAR, self.color < self.Umbral_final)
            self.transiciones(self.GIRO_SEGUIDOR, self.color > umbral)
            self.transiciones(self.AVANCE_2, self.infra > self.distancia_objetivo)

        elif self.estado == self.ESTADO_GIRO_IZQ:
            self.izq = -potencia
            self.der = potencia
            self.transiciones(self.ESTADO_RODEO, self.ang_izq <=-self.Angulo_rotacion
                                            and self.ang_der >= self.Angulo_rotacion)

        elif self.estado == self.ESTADO_GIRO_DER:
            self.izq = potencia
            self.der = -potencia
            self.transiciones(self.GIRO_SEGUIDOR, self.color > umbral)
            self.transiciones(self.ESTADO_AVANCE_CIEGO, self.ang_der <= -self.Angulo_rotacion
                                                and self.ang_izq >= self.Angulo_rotacion)

        elif self.estado == self.ESTADO_AVANCE_CIEGO:
            self.izq = potencia
            self.der = potencia
            self.transiciones(self.GIRO_SEGUIDOR, self.color > umbral)
            self.transiciones(self.ESTADO_RODEO, self.infra <= self.distancia_recuperacion)

        elif self.estado == self.RETROCESO:
            self.izq = -potencia
            self.der = -potencia
            self.transiciones(
                self.ESTADO_GIRO_IZQ,
                tiempo_fin < (time.time() - self.tiempo_inicial),
            )

        elif self.estado == self.AVANCE_2:
            self.izq = potencia
            self.der = potencia
            self.transiciones(self.ESTADO_GIRO_DER, tiempo_fin < (time.time() - self.tiempo_inicial))
        
        elif self.estado == self.GIRO_SEGUIDOR:
            self.izq = -potencia
            self.der = potencia
            self.transiciones(self.ESTADO_FINALIZAR, self.color < self.Umbral_final)
            self.transiciones(self.ESTADO_SEGUIR_LINEA, self.ang_izq <=-self.Angulo_seguimiento
                                            and self.ang_der >= self.Angulo_seguimiento)

        elif self.estado == self.ESTADO_FINALIZAR:
            self.izq = 0
            self.der = 0



class laberinto(Robot):
    def __init__(self):
        super().__init__()
        self.Angulo_seguimiento = 120
        self.Umbral_final=70
        self.Angulo_rotacion=90
        self.distancia_objetivo=20
        self.distancia_recuperacion=50

    """
    Implementacion del algoritmo Bug2.
    Combina seguidor de linea con rodeo de obstaculos usando wall-following.
    """

    def states(self, potencia, kp, ki, umbral, error_pared, tiempo_fin, max_dif):
        """
        Ejecuta la logica correspondiente al estado actual.

        Args:
            potencia: velocidad base de los motores.
            kp: ganancia proporcional del controlador de pared.
            ki: ganancia integral del controlador de pared.
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
            self.transiciones(self.ESTADO_FINALIZAR, self.color < self.Umbral_final)
            self.transiciones(self.RETROCESO, self.tactil == 1)

        elif self.estado == self.ESTADO_RODEO:
            # Wall-following: mantener distancia lateral al obstaculo
            self.lazo_motores(error_pared, kp, ki, potencia, max_dif)
            self.transiciones(self.ESTADO_FINALIZAR, self.color < self.Umbral_final)
            self.transiciones(self.RETROCESO, self.tactil == 1)
            self.transiciones(self.GIRO_SEGUIDOR, self.color > umbral)
            self.transiciones(self.AVANCE_2, self.infra > self.distancia_objetivo and self.infra !=255 and self.ultrasonido!=255)

        elif self.estado == self.ESTADO_GIRO_IZQ:
            self.izq = -potencia
            self.der = potencia
            self.transiciones(self.ESTADO_RODEO, self.ang_izq <= -self.Angulo_rotacion
                                            and self.ang_der >= self.Angulo_rotacion)

        elif self.estado == self.ESTADO_GIRO_DER:
            self.izq = potencia
            self.der = -potencia
            self.transiciones(self.GIRO_SEGUIDOR, self.color > umbral)
            self.transiciones(self.ESTADO_AVANCE_CIEGO, self.ang_der <= -self.Angulo_rotacion
                                                and self.ang_izq >= self.Angulo_rotacion)

        elif self.estado == self.ESTADO_AVANCE_CIEGO:
            self.izq = potencia
            self.der = potencia
            self.transiciones(self.GIRO_SEGUIDOR, self.color > umbral)
            self.transiciones(self.ESTADO_RODEO, self.infra <= self.distancia_recuperacion)

        elif self.estado == self.RETROCESO:
            self.izq = -potencia
            self.der = -potencia
            self.transiciones(
                self.ESTADO_GIRO_IZQ,
                tiempo_fin < (time.time() - self.tiempo_inicial),
            )

        elif self.estado == self.AVANCE_2:
            self.izq = potencia
            self.der = potencia
            self.transiciones(self.ESTADO_GIRO_DER, tiempo_fin < (time.time() - self.tiempo_inicial))
        
        elif self.estado == self.GIRO_SEGUIDOR:
            self.izq = -potencia
            self.der = potencia
            self.transiciones(self.ESTADO_FINALIZAR, self.color < self.Umbral_final)
            self.transiciones(self.ESTADO_SEGUIR_LINEA, self.ang_izq <= -self.Angulo_seguimiento
                                            and self.ang_der >= self.Angulo_seguimiento)

        elif self.estado == self.ESTADO_FINALIZAR:
            self.izq = 0
            self.der = 0
#-1.5,+1.35,0.045