#Estados
import time 

class Robot:
    # Constantes de Estado
    ESTADO_SEGUIR_LINEA = 0
    ESTADO_RODEO = 1
    ESTADO_GIRO_IZQ = 2
    ESTADO_GIRO_DER = 3
    ESTADO_AVANCE_CIEGO = 4
    ESTADO_FINALIZAR = 5
    RETROCESO = 6
    GIRO_SEGUIDOR=7
    AVANCE_ESQUINA = 8
    GIRO_BUSCA_PARED = 9
    GIRO_SEGUIDOR_1 = 10
    AVANCE_LINEA_1 = 11
    GIRO_SEGUIDOR_2 = 12
    AVANCE_LINEA_2 = 13
    
    def __init__(self):
        self.izq = 0
        self.der = 0
        self.angulo = 0
        self.color = 0
        self.tactil = False
        self.ultrasonido = 0
        self.estado = self.ESTADO_SEGUIR_LINEA
        self.tiempo_inicial = 0
        self.meta = 0
        self.encoder = 0
        self.anguloobjetivo = 0
        self.encoder_inicio = 0
        self.contador_sin_pared = 0
        self.contador_linea = 0
    
    def transiciones(self, objetivo, condicion):
        if condicion:
            self.estado = objetivo
        return self.estado
            
    def lazo_motores(self, error, kp, potencia):
        if self.angulo > self.anguloobjetivo:
            self.izq = potencia + error * kp
            self.der = potencia - error * kp
        else:
            self.izq = potencia - error * kp
            self.der = potencia + error * kp

    def print_atributos(self):
        #print(f"Izquierda: {self.izq}, Derecha: {self.der}, Angulo: {self.angulo}, Color: {self.color}, Tactil: {self.tactil}, Ultrasonido: {self.ultrasonido}, Tiempo: {self.tiempo_inicial}, Estado: {self.estado}")
        print(self.estado) 
        return 0


class bug_2(Robot):
    def __init__(self):
        super().__init__()

        self.angulo_inicial = 0
        self.encoder = 0
        self.encoder_inicio = 0
        self.contador_linea = 0
        self.contador_sin_pared = 0

    def states(self, potencia, KP, kp, umbral, error, tiempo_fin):

        if self.estado == self.ESTADO_SEGUIR_LINEA:

            if self.color < umbral:
                self.izq = potencia + KP
                self.der = potencia - KP
            else:
                self.der = potencia + KP
                self.izq = potencia - KP

            self.transiciones(self.ESTADO_FINALIZAR,self.color == 100.68)
            self.transiciones(self.RETROCESO,self.tactil == 1)



        elif self.estado == self.ESTADO_RODEO:

            self.lazo_motores(error, kp, potencia)

            self.transiciones(self.ESTADO_FINALIZAR,self.color > 200)

            if self.color > umbral:
                self.estado = self.AVANCE_LINEA_1

            if self.ultrasonido > 30:
                self.estado = self.AVANCE_ESQUINA

            self.transiciones(self.ESTADO_FINALIZAR,self.color == 100.68)
            self.transiciones(self.RETROCESO,self.tactil == 1)

        elif self.AVANCE_ESQUINA == self.estado:

            self.izq = potencia
            self.der = potencia

            if self.encoder > 90:
                self.estado = self.GIRO_BUSCA_PARED

            self.transiciones(self.ESTADO_FINALIZAR,self.color == 100.68)
            self.transiciones(self.RETROCESO,self.tactil == 1)



        elif self.estado == self.GIRO_BUSCA_PARED:
            self.izq = potencia
            self.der = -potencia

            if self.angulo >= self.anguloobjetivo+90:
                self.estado = self.ESTADO_AVANCE_CIEGO
                self.anguloobjetivo += 90



        elif self.estado == self.ESTADO_GIRO_IZQ:
            self.izq = -potencia
            self.der = potencia

            if self.angulo <= self.anguloobjetivo-90:
                self.estado = self.ESTADO_RODEO
                self.anguloobjetivo = self.anguloobjetivo-90


        elif self.estado == self.ESTADO_AVANCE_CIEGO:
            self.izq = potencia
            self.der = potencia

            if self.ultrasonido <= 25:
                self.estado = self.ESTADO_RODEO



        elif self.estado == self.RETROCESO:

            self.izq = -potencia
            self.der = -potencia

            if tiempo_fin < (
                time.time() - self.tiempo_inicial
            ):
                self.estado = self.ESTADO_GIRO_IZQ


        # RECUPERACION DE LINEA

        elif self.estado == self.GIRO_SEGUIDOR_1:
            self.izq = -0.4 * potencia
            self.der = +0.4 * potencia

            if self.color > umbral:
                self.estado = self.AVANCE_LINEA_2


        elif self.estado == self.AVANCE_LINEA_1:
            self.izq = potencia
            self.der = potencia

            if self.encoder > 120:
                self.estado = self.GIRO_SEGUIDOR_1


        elif self.estado == self.GIRO_SEGUIDOR_2:
            self.izq = -0.4 * potencia
            self.der = +0.4 * potencia

            if self.color > umbral:
                self.estado = self.ESTADO_SEGUIR_LINEA
                self.anguloobjetivo = 0


        elif self.estado == self.AVANCE_LINEA_2:
            self.izq = potencia
            self.der = potencia

            if self.encoder > 120:
                self.estado = self.GIRO_SEGUIDOR_2


        #TERMINAR

        elif self.estado == self.ESTADO_FINALIZAR:
            self.izq = 0
            self.der = 0
            return self.ESTADO_FINALIZAR