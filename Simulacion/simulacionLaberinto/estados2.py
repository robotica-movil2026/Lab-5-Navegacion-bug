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
        if error < self.anguloobjetivo:
            self.izq = potencia + error * kp
            self.der = potencia - error * kp
            #print(f"Error: {error}, {self.izq>self.der}")
        else:
            self.izq = potencia + error * kp
            self.der = potencia - error * kp
            #print(f"Error: {error}, {self.izq>self.der}")

    def print_atributos(self):
        #print(f"Izquierda: {self.izq}, Derecha: {self.der}, Angulo: {self.angulo}, Color: {self.color}, Tactil: {self.tactil}, Ultrasonido: {self.ultrasonido}, Tiempo: {self.tiempo_inicial}, Estado: {self.estado}")
        print(self.estado) 
        return 0

class bug_2(Robot):

    AVANCE = 0
    GIRO_DER = 1
    GIRO_IZQ = 2
    ENTRAR_PASILLO = 3
    RETROCESO = 4 

    def __init__(self):
        super().__init__()

        self.estado = self.AVANCE

        self.encoder = 0

        self.PARED_CERCANA = 10
        self.FACTOR_SEGURIDAD = 2.5

        self.contador_hueco = 0
        self.MUESTRAS_HUECO = 5000

    def states(self, potencia, error, kp):

        # AVANCE NORMAL

        if self.estado == self.AVANCE:
            self.lazo_motores(error, kp, potencia)

            if self.ultrasonido > (self.PARED_CERCANA * self.FACTOR_SEGURIDAD) and self.tiempo_inicial > 25:
                print(self.ultrasonido)
                self.contador_hueco += 1
            else:
                self.contador_hueco = 0

            if self.contador_hueco >= self.MUESTRAS_HUECO:
                self.contador_hueco = 0
                self.estado = self.GIRO_DER

            # Choque frontal
            self.transiciones(self.RETROCESO,self.tactil == 1)


        # GIRO DERECHA
        elif self.estado == self.GIRO_DER:
            self.izq = potencia
            self.der = -potencia

            if self.angulo >= self.anguloobjetivo+90:
                self.estado = self.ENTRAR_PASILLO
                self.anguloobjetivo = self.anguloobjetivo + 90

        # RETROCESO

        elif self.estado == self.RETROCESO:
            self.lazo_motores(error, kp, -1*potencia)

            if self.encoder >= 80:
                self.estado = self.GIRO_IZQ
            
        # ENTRAR AL NUEVO PASILLO
        elif self.estado == self.ENTRAR_PASILLO:
            self.izq = potencia
            self.der = potencia

            if self.ultrasonido <= self.PARED_CERCANA * self.FACTOR_SEGURIDAD:
               self.estado=self.AVANCE

        # GIRO IZQUIERDA
        elif self.estado == self.GIRO_IZQ:
            self.izq = -potencia
            self.der = potencia

            if self.angulo <= self.anguloobjetivo-90:
                self.estado = self.AVANCE
                self.anguloobjetivo = self.anguloobjetivo - 90
