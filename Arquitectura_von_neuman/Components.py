# Components.py - Versión Harvard

# Memoria de Datos
class MemoriaDatos:
    def __init__(self, idx=0):
        self.direcciones = ['00000100', '00000101', '01100111', '01110000', '00000101', '00001011', '00000000', '00000000']
        self.contenido = [0]*8  # Inicializa datos
        # Inicialización según el set de instrucciones
        if idx == 0:
            # Suma MEM[0] + MEM[1] (ahora MEM[0]=11, MEM[1]=5)
            self.store(0, 11)
            self.store(1, 5)
        elif idx == 1:
            # 5 + 11
            self.store(0, 5)
            self.store(1, 5)
        elif idx == 2:
            # (1 + 1)^5
            self.store(0, 1)
            self.store(1, 1)
        elif idx == 3:
            # OR
            self.store(0, 0b01001011)
            self.store(1, 0b01010101)
        elif idx == 4:
            # AND
            self.store(0, 0b01001011)
            self.store(1, 0b01010101)
        elif idx == 5:
            # 255 + 1
            self.store(0, 255)
            self.store(1, 1)
        elif idx == 6:
            # ((2 ^ 2) + 2) ^ 2 = 36
            self.store(0, 2)
            self.store(1, 2)
        elif idx == 7:
            # (8 - 3) ^ 3 = 125
            self.store(0, 8)
            self.store(1, 3)
        elif idx == 8:
            # Multiplicación MEM[0] * MEM[1] = 3 * 4 = 12
            self.store(0, 3)
            self.store(1, 4)
        elif idx == 9:
            # Potenciación MEM[0] ^ MEM[1] = 2 ^ 3 = 8
            self.store(0, 2)
            self.store(1, 3)

    def leer(self, direccion):
        if 0 <= direccion < len(self.contenido):
            return self.contenido[direccion]
        else:
            # Silenciosamente retorna 0 si la dirección es inválida
            return 0

    def store(self, direccion, valor):
        self.contenido[direccion] = valor

# Memoria de Instrucciones
class MemoriaInstrucciones:
    def __init__(self, idx=0):
        self.operaciones = [
            # Sumar MEM[0] + MEM[1] y guardar en la última casilla
            ['01100000', '00000001', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000'],
            # 5 + 11 (original)
            ['00000100', '00000101', '01100111', '01110000', '00000101', '00001011', '00000000', '00000000'],
            # ...resto de operaciones...
            ['00000101', '00000101', '00110110', '01100111', '01110000', '00000001', '00000101', '00000000'],
            ['00000100', '01010101', '01100111', '01110000', '01001011', '01010101', '00000000', '00000000'],
            ['00000100', '01000101', '01100111', '01110000', '01001011', '01010101', '00000000', '00000000'],
            ['00000100', '00000101', '01100111', '01110000', '11111111', '00000001', '00000000', '00000000'],
            ['00000110', '00110110', '00000110', '00110110', '01100111', '01110000', '00000010', '00000000'],
            ['00000101', '00010110', '00110110', '01100111', '01110000', '00001000', '00000011', '00000000'],
            # Multiplicación MEM[0] * MEM[1]
                ['01100000', '00100001', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000'],
            # Potenciación MEM[0] ^ MEM[1]
            ['01100000', '00110001', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000']
        ]
        self.contenido = self.operaciones[idx]

    def leer(self, direccion):
        return self.contenido[direccion]

# Unidad de Control
class UnidadControl:
    def decode(self):
        index = int(self.registroInstrucciones[0: 4], 2)
        self.operacion = self.decodificador[index]
        direccion = int(self.registroInstrucciones[4:], 2)
        return self.operacion, direccion
    def fetch(self, memoriaInstrucciones):
        self.registroInstrucciones = memoriaInstrucciones.leer(self.contadorPrograma)
        self.contadorPrograma += 1
    def __init__(self):
        self.contadorPrograma = 0
        self.registroInstrucciones = None
        self.decodificador = ["+", "-", "*", "^", "&", "|", "M", "..."]
        self.operacion = ""
class ALU:
    def __init__(self):
        self.acumulador = 0
        self.registroEntrada = 0

    def ejecutar(self, operacion, valor):
        if operacion == "+":
            self.acumulador += valor
        elif operacion == "-":
            self.acumulador -= valor
        elif operacion == "*":
            self.acumulador *= valor
        elif operacion == "^":
            self.acumulador **= valor
        elif operacion == "&":
            self.acumulador = self.acumulador & valor
        elif operacion == "|":
            self.acumulador = self.acumulador | valor
        return self.acumulador

# CPU
class CPU:
    def __init__(self):
        self.control = UnidadControl()
        self.alu = ALU()

    def ejecutar(self, operacion, direccion, memoriaDatos):
        if operacion == "M":  # LOAD/STORE
            self.alu.acumulador = memoriaDatos.leer(direccion)
        elif operacion in ["+", "-", "*", "^", "&", "|"]:
            valor = memoriaDatos.leer(direccion)
            self.alu.ejecutar(operacion, valor)
        elif operacion == "...":  # HALT
            return False
        return True
