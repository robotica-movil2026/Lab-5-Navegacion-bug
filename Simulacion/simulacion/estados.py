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
    
    def transiciones(self, objetivo, condicion):
        if condicion:
            self.estado = objetivo
        return self.estado
            
    def lazo_motores(self, error, kp, potencia):
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
    
    def states(self, potencia, kp, umbral, error, tiempo_fin):
        if self.estado == self.ESTADO_SEGUIR_LINEA:
            if self.color<umbral:
                self.izq = potencia + kp
                self.der = potencia - kp
            else:
                self.der = potencia + kp
                self.izq = potencia - kp
            self.transiciones(self.ESTADO_FINALIZAR, self.color > 200)
            self.transiciones(self.RETROCESO, self.tactil == 1)

        elif self.estado == self.ESTADO_RODEO:
            self.lazo_motores(error, kp, potencia)
            #print(self.ultrasonido)
            self.transiciones(self.ESTADO_FINALIZAR, self.color > 200)
            self.transiciones(self.GIRO_SEGUIDOR, self.color > umbral)
            self.transiciones(self.ESTADO_GIRO_DER, self.ultrasonido > 20)

        elif self.estado == self.ESTADO_GIRO_IZQ:
            self.izq = -potencia
            self.der = potencia
            #print(self.angulo)
            self.transiciones(self.ESTADO_RODEO, self.angulo <= -90)
            
        elif self.estado == self.ESTADO_GIRO_DER:
            self.izq = potencia
            self.der = -potencia
            #print(self.angulo)
            self.transiciones(self.GIRO_SEGUIDOR, self.color > umbral)
            self.transiciones(self.ESTADO_AVANCE_CIEGO, self.angulo >90)
            
        elif self.estado == self.ESTADO_AVANCE_CIEGO:
            self.izq = potencia
            self.der = potencia
            self.transiciones(self.GIRO_SEGUIDOR, self.color > umbral)
            self.transiciones(self.ESTADO_RODEO, self.ultrasonido <= 50)

        elif self.estado == self.RETROCESO:
            self.izq = - potencia
            self.der = - potencia
            #print(time.time() - self.tiempo_inicial)
            self.transiciones(self.ESTADO_GIRO_IZQ, tiempo_fin < (time.time() - self.tiempo_inicial))
            
        elif self.estado == self.GIRO_SEGUIDOR:
            self.izq = -potencia
            self.der = +potencia
            self.transiciones(self.ESTADO_FINALIZAR, self.color > 200)
            self.transiciones(self.ESTADO_SEGUIR_LINEA, self.angulo <= -45)

        elif self.estado == self.ESTADO_FINALIZAR:
            return self.ESTADO_FINALIZAR
            