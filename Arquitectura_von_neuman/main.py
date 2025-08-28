import pygame
import sys
import Components

# Función para ejecutar un paso Harvard
def ejecutar_paso(cpu, memoriaDatos, memoriaInstrucciones, estado_alu):
    resultado = None
    if cpu.control.contadorPrograma < len(memoriaInstrucciones.contenido):
        # Fetch
        cpu.control.fetch(memoriaInstrucciones)
        operacion, direccion = cpu.control.decode()

        # Validar dirección antes de operar
        if direccion < 0 or direccion >= len(memoriaDatos.contenido):
            print(f"Dirección fuera de rango ignorada: {direccion}")
            estado_alu['resultado'] = None
            return True, estado_alu

        # Execute
        if operacion == "M":  # LOAD
            cpu.alu.acumulador = memoriaDatos.leer(direccion)
            resultado = cpu.alu.acumulador
        elif operacion in ["+", "-", "*", "^", "&", "|"]:
            valor = memoriaDatos.leer(direccion)
            cpu.alu.registroEntrada = valor
            # Para operaciones lógicas, inicializa el acumulador si está en cero
            if cpu.alu.acumulador == 0 and operacion in ["&", "|"]:
                cpu.alu.acumulador = valor
                resultado = cpu.alu.acumulador
            else:
                resultado = cpu.alu.ejecutar(operacion, valor)
            memoriaDatos.contenido[-1] = resultado
        elif operacion == "...":  # HALT
            return False, estado_alu
        # Marcar animación si el acumulador cambió
        if estado_alu['prev_acumulador'] != cpu.alu.acumulador:
            estado_alu['anim_timer'] = 15  # frames para animación
        estado_alu['prev_acumulador'] = cpu.alu.acumulador
        estado_alu['resultado'] = resultado
    return True, estado_alu

# Colores
FONDO = (245, 247, 250)
NEGRO = (40, 40, 40)
AZUL = (80, 140, 200)
VERDE = (100, 200, 150)
ROJO = (240, 110, 110)
GRIS = (230, 230, 230)
HOVER = (180, 180, 180)

# Inicializar pantalla
ANCHO, ALTO = 1000, 720
pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Arquitectura Harvard")
fuente = pygame.font.SysFont("consolas", 14)
fuente2 = pygame.font.SysFont("Segoe UI", 20, bold=True)

def draw_card(surface, color, rect, radius=12):
    sombra = (rect[0]+4, rect[1]+4, rect[2], rect[3])
    pygame.draw.rect(surface, (200, 200, 200), sombra, border_radius=radius)
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def dibujar_architectura(cpu, memoriaDatos, memoriaInstrucciones, estado_alu):
    pantalla.fill(FONDO)

    # Posiciones base
    centro_x, centro_y = ANCHO // 2, ALTO // 2
    tam_control = 220
    tam_mem = 260  # Aumenta el tamaño de las memorias
    tam_alu = 160
    sep_x = 320    # Aumenta la separación horizontal
    sep_y = 250   # Subir aún más la ALU

    # Unidad de Control (centro)
    draw_card(pantalla, VERDE, (centro_x-tam_control//2, centro_y-tam_control//2, tam_control, tam_control))
    pantalla.blit(fuente2.render("Unidad de Control", True, NEGRO), (centro_x-80, centro_y-15))
    pantalla.blit(fuente.render("C. Programa: " + str(cpu.control.contadorPrograma).rjust(2,"0"), True, NEGRO), (centro_x-80, centro_y+30))
    pantalla.blit(fuente.render("R. Instr.: " + str(cpu.control.registroInstrucciones), True, NEGRO), (centro_x-80, centro_y+55))
    pantalla.blit(fuente.render("Operación: " + str(cpu.control.operacion), True, NEGRO), (centro_x-80, centro_y+80))

    # Memoria de instrucciones (izquierda, más grande y más separada)
    draw_card(pantalla, AZUL, (centro_x-sep_x-tam_mem//2, centro_y-tam_mem//2, tam_mem, tam_mem))
    pantalla.blit(fuente2.render("Memoria instrucciones", True, NEGRO), (centro_x-sep_x-tam_mem//2+10, centro_y-tam_mem//2+10))
    pantalla.blit(fuente.render("Dirección", True, NEGRO), (centro_x-sep_x-tam_mem//2+20, centro_y-tam_mem//2+40))
    pantalla.blit(fuente.render("Contenido", True, NEGRO), (centro_x-sep_x-tam_mem//2+100, centro_y-tam_mem//2+40))
    for i in range(len(memoriaInstrucciones.contenido)):
        dir_bin = format(i, '03b')
        y_pos = centro_y-tam_mem//2+70+i*24
        color = (255, 0, 0) if i == cpu.control.contadorPrograma else NEGRO
        pantalla.blit(fuente.render(dir_bin, True, color), (centro_x-sep_x-tam_mem//2+20, y_pos))
        pantalla.blit(fuente.render(str(memoriaInstrucciones.contenido[i]), True, color), (centro_x-sep_x-tam_mem//2+100, y_pos))

    # Memoria de datos (derecha, más grande y más separada)
    draw_card(pantalla, AZUL, (centro_x+sep_x-tam_mem//2, centro_y-tam_mem//2, tam_mem, tam_mem))
    pantalla.blit(fuente2.render("Memoria datos", True, NEGRO), (centro_x+sep_x-tam_mem//2+10, centro_y-tam_mem//2+10))
    pantalla.blit(fuente.render("Dirección", True, NEGRO), (centro_x+sep_x-tam_mem//2+20, centro_y-tam_mem//2+40))
    pantalla.blit(fuente.render("Contenido", True, NEGRO), (centro_x+sep_x-tam_mem//2+100, centro_y-tam_mem//2+40))
    for i in range(len(memoriaDatos.contenido)):
        pantalla.blit(fuente.render(str(memoriaDatos.direcciones[i]), True, NEGRO), (centro_x+sep_x-tam_mem//2+20, centro_y-tam_mem//2+70+i*24))
        pantalla.blit(fuente.render(str(memoriaDatos.contenido[i]), True, NEGRO), (centro_x+sep_x-tam_mem//2+100, centro_y-tam_mem//2+70+i*24))

    # ALU (arriba de la unidad de control)
    color_alu = ROJO
    if estado_alu['anim_timer'] > 0:
        color_alu = (180, 255, 180)
        estado_alu['anim_timer'] -= 1
    draw_card(pantalla, color_alu, (centro_x-tam_alu//2, centro_y-sep_y-tam_alu//2, tam_alu, tam_alu))
    pantalla.blit(fuente2.render("ALU", True, NEGRO), (centro_x-30, centro_y-sep_y-tam_alu//2+10))
    pantalla.blit(fuente.render("Entrada: " + str(cpu.alu.registroEntrada), True, NEGRO), (centro_x-tam_alu//2+10, centro_y-sep_y-tam_alu//2+40))
    pantalla.blit(fuente.render("Acumulador: " + str(cpu.alu.acumulador), True, NEGRO), (centro_x-tam_alu//2+10, centro_y-sep_y-tam_alu//2+70))
    pantalla.blit(fuente.render("Resultado: " + str(estado_alu['resultado']), True, NEGRO), (centro_x-tam_alu//2+10, centro_y-sep_y-tam_alu//2+100))

    # BUSES DE DATOS (líneas entre componentes)
    bus_color = (255, 255, 0)
    bus_width = 10
    # Memoria instrucciones <-> Unidad de control
    pygame.draw.line(pantalla, bus_color,
        (centro_x-sep_x+tam_mem//2, centro_y),
        (centro_x-tam_control//2, centro_y), bus_width)
    # Memoria datos <-> Unidad de control
    pygame.draw.line(pantalla, bus_color,
        (centro_x+sep_x-tam_mem//2, centro_y),
        (centro_x+tam_control//2, centro_y), bus_width)
    # ALU <-> Unidad de control
    pygame.draw.line(pantalla, bus_color,
        (centro_x, centro_y-sep_y+tam_alu//2),
        (centro_x, centro_y-tam_control//2), bus_width)

    # Botones horizontales en la parte inferior
    mouse = pygame.mouse.get_pos()
    color_avanzar = HOVER if (centro_x-130 <= mouse[0] <= centro_x-10 and ALTO-80 <= mouse[1] <= ALTO-30) else GRIS
    draw_card(pantalla, color_avanzar, (centro_x-130, ALTO-80, 120, 50))
    pantalla.blit(fuente2.render("Avanzar", True, NEGRO), (centro_x-120, ALTO-65))
    color_reiniciar = HOVER if (centro_x+10 <= mouse[0] <= centro_x+130 and ALTO-80 <= mouse[1] <= ALTO-30) else GRIS
    draw_card(pantalla, color_reiniciar, (centro_x+10, ALTO-80, 120, 50))
    pantalla.blit(fuente2.render("Reiniciar", True, NEGRO), (centro_x+20, ALTO-65))

    pygame.display.flip()

# Inicialización

idx_operacion = 1 # Potenciación MEM[0] ^ MEM[1]
cpu = Components.CPU()
memoriaDatos = Components.MemoriaDatos(idx_operacion)
memoriaInstrucciones = Components.MemoriaInstrucciones(idx_operacion)
estado = "pausa"
historial = []
# Estado para animación y resultado ALU
estado_alu = {'prev_acumulador': cpu.alu.acumulador, 'anim_timer': 0, 'resultado': None}
# Variables globales para posiciones
centro_x = ANCHO // 2
centro_y = ALTO // 2

# Bucle principal
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.MOUSEBUTTONDOWN:
            x, y = evento.pos
            # Botones horizontales
            if centro_x-130 <= x <= centro_x-10 and ALTO-80 <= y <= ALTO-30:
                estado = "avanzar"
            elif centro_x+10 <= x <= centro_x+130 and ALTO-80 <= y <= ALTO-30:
                # Reiniciar
                cpu = Components.CPU()
                memoriaDatos = Components.MemoriaDatos(idx_operacion)
                memoriaInstrucciones = Components.MemoriaInstrucciones(idx_operacion)
                historial = []

    # Avanzar paso a paso
    if estado == "avanzar":
        # Guardar estado
        historial.append((cpu, memoriaDatos))
        continuar, estado_alu = ejecutar_paso(cpu, memoriaDatos, memoriaInstrucciones, estado_alu)
        if continuar == False:
            print("Programa terminado.")
            estado = "pausa"
        else:
            estado = "pausa"

    dibujar_architectura(cpu, memoriaDatos, memoriaInstrucciones, estado_alu)

