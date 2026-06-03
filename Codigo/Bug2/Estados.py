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

    def __init__(self):
        self.izq = 0
        self.der = 0
        self.angulo = 0
        self.color = 0
        self.tactil = False
        self.ultrasonido = 0
        self.estado = self.ESTADO_SEGUIR_LINEA
        self.tiempo_inicial = 0
        self.angulo_inicial = 0
        self.meta = 0
    
    def lazo_motores(self, error, kp, potencia):
        self.izq = potencia + error * kp
        self.der = potencia - error * kp

    def print_atributos(self):
        #print(f"Izquierda: {self.izq}, Derecha: {self.der}, Angulo: {self.angulo}, Color: {self.color}, Tactil: {self.tactil}, Ultrasonido: {self.ultrasonido}, Tiempo: {self.tiempo_inicial}, Estado: {self.estado}")
        print(self.estado) 
        return 0

    def seguir_linea(self, kp, error, potencia, umbral): #el kp es la variable de suma
        if self.color<umbral:
            self.izq = potencia + kp
            self.der = potencia - kp
        
        else:
            self.der = potencia + kp
            self.izq = potencia - kp
            
        #self.lazo_motores(error, kp, potencia)

        if self.meta != 0:
            self.estado = self.ESTADO_FINALIZAR
            return self.estado
        if self.tactil == 1:
            self.angulo_inicial = self.angulo
            self.estado = self.RETROCESO
            #self.estado = self.ESTADO_GIRO_IZQ
            self.tiempo_inicial = time.time()
            self.retroceso_ciego(60, 4)
            return self.estado
        else:
            self.estado = self.ESTADO_SEGUIR_LINEA
            return self.estado

    def rodeo(self, kp, error, potencia, umbral):
        self.lazo_motores(error, kp, potencia)
        if (self.ultrasonido <= 200):
            self.estado = self.ESTADO_RODEO
            return self.estado
        if self.ultrasonido > 600:
            self.angulo_inicial = self.angulo
            self.estado = self.ESTADO_GIRO_DER
            return self.estado
        if self.color < umbral:
            self.estado = self.ESTADO_SEGUIR_LINEA
            return self.estado

    def diferencia_angular(self, angulo_objetivo, angulo_actual):
        """Calcula la diferencia más corta entre dos ángulos, evitando discontinuidades."""
        return (angulo_objetivo - angulo_actual + 180) % 360 - 180

    def giro_izq(self, potencia, angulo_fin):
        # Asumiendo que girar a la izquierda aumenta el ángulo
        target_angle = self.angulo_inicial + angulo_fin
        error = self.diferencia_angular(target_angle, self.angulo)
        
        # Si el error es positivo y mayor al umbral, seguimos girando
        if error > 2:
            self.izq = -potencia
            self.der = potencia
            self.estado = self.ESTADO_GIRO_IZQ
            return self.estado
        else:
            # Detenemos motores al terminar el giro
            self.izq = 0
            self.der = 0
            self.estado = self.ESTADO_RODEO
            return self.estado
        
    def giro_der(self, potencia, angulo_fin):
        # Asumiendo que girar a la derecha disminuye el ángulo
        target_angle = self.angulo_inicial - angulo_fin
        error = self.diferencia_angular(target_angle, self.angulo)
        
        # Si el error es negativo y menor al umbral negativo, seguimos girando
        if error < -2:
            self.izq = potencia
            self.der = -potencia
            self.estado = self.ESTADO_GIRO_DER
            return self.estado
        else:
            # Detenemos motores y preparamos el siguiente estado
            self.izq = 0
            self.der = 0
            self.tiempo_inicial = time.time()
            self.estado = self.ESTADO_AVANCE_CIEGO
            return self.estado
    
    def avance_ciego(self, potencia, tiempo_fin):
        self.izq = potencia
        self.der = potencia
        tiempo = time.time() - self.tiempo_inicial
        if tiempo > tiempo_fin:
            self.estado = self.ESTADO_RODEO
            return self.estado
        else:
            self.estado = self.ESTADO_AVANCE_CIEGO
            return self.estado
    
    def retroceso_ciego(self, potencia, tiempo_fin):
        if tiempo_fin > (time.time() - self.tiempo_inicial):
            self.izq = - potencia
            self.der = - potencia
            self.estado = self.RETROCESO
            return self.estado
        else:
            self.estado = self.ESTADO_GIRO_IZQ
            return self.estado

        

    def finalizar(self):
        self.izq = 0
        self.der = 0
        self.estado = self.ESTADO_FINALIZAR
        return self.estado
'''
# --- Bloque de Simulación Local ---
if __name__ == "__main__":
    bot = Robot()
    
    color_ref = 50
    ultrasonido_ref = 10

    while True:
        variable = input("Ingrese la variable a cambiar: Angulo(A), Color(C), Tactil(T), Ultrasonido(U), Estado(E): ")
        if variable == "A":
            bot.angulo = int(input("Ingrese el angulo: "))
        elif variable == "C":
            bot.color = int(input("Ingrese el color: "))
        elif variable == "T":
            bot.tactil = int(input("Ingrese el tactil: "))
        elif variable == "U":
            bot.ultrasonido = int(input("Ingrese el ultrasonido: "))
        elif variable == "E":
            bot.estado = int(input("Ingrese el estado: "))

        if bot.estado == Robot.ESTADO_SEGUIR_LINEA:
            error = color_ref - bot.color
            bot.seguir_linea(1, error, 30)
        elif bot.estado == Robot.ESTADO_RODEO:
            error = bot.ultrasonido - ultrasonido_ref
            bot.rodeo(1, error, 30)
        elif bot.estado == Robot.ESTADO_GIRO_IZQ:
            bot.giro_izq(30, 90)
        elif bot.estado == Robot.ESTADO_GIRO_DER:
            bot.giro_der(30, 90)
        elif bot.estado == Robot.ESTADO_AVANCE_CIEGO:
            bot.avance_ciego(30, 5)
        elif bot.estado == Robot.ESTADO_FINALIZAR:
            bot.finalizar()
            break
        bot.print_atributos()'''