import pygame
import sys
import os
import random
import math

# ==========================================
# CONFIGURACIÓN Y CONSTANTES
# ==========================================
ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600
FPS = 60

ESCALA = 4  
TAM_TILE_ORIGINAL = 16
TAM_TILE = TAM_TILE_ORIGINAL * ESCALA

ANCHO_MAPA = 2000
ALTO_MAPA = 2000

VOLUMEN_MUSICA = 0.35
VELOCIDAD_JUGADOR = 5
VELOCIDAD_ANIMACION = 0.15
VELOCIDAD_ANIMACION_VACA = 0.05
ESCALA_CASA = 2.5
DURACION_TRANSICION_DIA = 1.0
ESCALA_VACA = 4
ESCALA_ICONO_CARRITO = 5
ESCALA_SEMILLA_MENU = 5
TAM_ICONO_VENTA = 28

META_MONEDAS_VICTORIA = 500  # Condición de victoria
DIA_LIMITE_DERROTA = 10      # Condición de derrota
VOLUMEN_MUSICA = 0.35 

PRECIO_COMPRA_SEMILLA_1 = 15
PRECIO_COMPRA_SEMILLA_2 = 22
PRECIO_VENTA_SEMILLA_1 = 9
PRECIO_VENTA_SEMILLA_2 = 13
PRECIO_VENTA_PLANTA_1 = 24
PRECIO_VENTA_PLANTA_2 = 31

# ==========================================
# UTILIDADES DE SISTEMA Y SPRITES
# ==========================================
def asset_path(*rutas):
    """Obtiene la ruta absoluta de los recursos en la carpeta Assets."""
    dir_actual = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir_actual, "Assets", *rutas)

def extraer_sprite_exacto(hoja, col, fila, ancho_tiles, alto_tiles, escala):
    """Recorta y escala un área específica de la hoja de sprites."""
    x, y = (col - 1) * 16, (fila - 1) * 16
    ancho_px, alto_px = ancho_tiles * 16, alto_tiles * 16
    imagen = pygame.Surface((ancho_px, alto_px), pygame.SRCALPHA)
    imagen.blit(hoja, (0, 0), pygame.Rect(x, y, ancho_px, alto_px))
    return pygame.transform.scale(imagen, (int(ancho_px * escala), int(alto_px * escala)))

def dibujar_texto_con_borde(superficie, fuente, texto, pos, color_texto, color_borde):
    """Dibuja texto con un borde simple (sombra) para mejorar la legibilidad."""
    x, y = pos
    texto_base = fuente.render(texto, True, color_texto)
    for dx in (-2, -1, 0, 1, 2):
        for dy in (-2, -1, 0, 1, 2):
            if dx == 0 and dy == 0: continue
            superficie.blit(fuente.render(texto, True, color_borde), (x + dx, y + dy))
    superficie.blit(texto_base, (x, y))

def construir_layout_tienda(panel_rect):
    """Genera los rectángulos de colisión (hitboxes) para la UI de la tienda."""
    return {
        "tab_compra": pygame.Rect(panel_rect.x + 30, panel_rect.y + 58, 120, 44),
        "tab_venta": pygame.Rect(panel_rect.x + 170, panel_rect.y + 58, 120, 44),
        "cerrar": pygame.Rect(panel_rect.right - 54, panel_rect.y + 14, 32, 32),
        "accion1": pygame.Rect(panel_rect.right - 140, panel_rect.y + 130, 104, 38),
        "accion2": pygame.Rect(panel_rect.right - 140, panel_rect.y + 236, 104, 38),
        "venta_s1": pygame.Rect(panel_rect.right - 140, panel_rect.y + 118, 104, 38),
        "venta_p1": pygame.Rect(panel_rect.right - 140, panel_rect.y + 160, 104, 38),
        "venta_s2": pygame.Rect(panel_rect.right - 140, panel_rect.y + 224, 104, 38),
        "venta_p2": pygame.Rect(panel_rect.right - 140, panel_rect.y + 266, 104, 38),
        "fila1_y": panel_rect.y + 122,
        "fila2_y": panel_rect.y + 228,
    }

def draw_tienda(superficie, panel_img, boton_img, fuente_titulo, fuente_texto, layout, modo_tienda, 
                estado_juego, semillas, cosechas, i_s1, i_s2, i_p1, i_p2, iv_s1, iv_s2, iv_p1, iv_p2):
    """Renderiza la interfaz interactiva de la tienda de la vaca."""
    mpos = pygame.mouse.get_pos()
    overlay = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    superficie.blit(overlay, (0, 0))

    panel_rect = panel_img.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2))
    superficie.blit(panel_img, panel_rect)

    def draw_btn(rect, text, is_active=True):
        """Función interna para dibujar botones con efecto hover e inactivos."""
        superficie.blit(pygame.transform.scale(boton_img, (rect.width, rect.height)), rect)
        color_texto, color_sombra = (30, 20, 15), (255, 255, 255)
        if not is_active:
            s = pygame.Surface(rect.size, pygame.SRCALPHA)
            s.fill((0, 0, 0, 120))
            superficie.blit(s, rect)
            color_texto, color_sombra = (150, 150, 150), (50, 50, 50)
        elif rect.collidepoint(mpos):
            s = pygame.Surface(rect.size, pygame.SRCALPHA)
            s.fill((255, 255, 255, 60))
            superficie.blit(s, rect)
            color_texto = (10, 10, 10)
        dibujar_texto_con_borde(superficie, fuente_texto, text, (rect.x + 8, rect.y + 10), color_texto, color_sombra)

    c_on, c_off = (244, 219, 171), (184, 154, 118)
    pygame.draw.rect(superficie, c_on if modo_tienda == "compra" else c_off, layout["tab_compra"], border_radius=8)
    pygame.draw.rect(superficie, c_on if modo_tienda == "venta" else c_off, layout["tab_venta"], border_radius=8)
    pygame.draw.rect(superficie, (150, 70, 60) if layout["cerrar"].collidepoint(mpos) else (120, 56, 48), layout["cerrar"], border_radius=6)

    dibujar_texto_con_borde(superficie, fuente_titulo, "Tienda de Vaca", (panel_rect.x + 24, panel_rect.y + 14), (34, 25, 20), (255, 255, 255))
    dibujar_texto_con_borde(superficie, fuente_texto, f"Monedas: {estado_juego.monedas}", (panel_rect.right - 210, panel_rect.y + 20), (255, 220, 100), (40, 20, 10))
    dibujar_texto_con_borde(superficie, fuente_texto, "Comprar", (layout["tab_compra"].x + 18, layout["tab_compra"].y + 11), (30, 20, 15), (255, 255, 255))
    dibujar_texto_con_borde(superficie, fuente_texto, "Vender", (layout["tab_venta"].x + 26, layout["tab_venta"].y + 11), (30, 20, 15), (255, 255, 255))
    dibujar_texto_con_borde(superficie, fuente_texto, "X", (layout["cerrar"].x + 9, layout["cerrar"].y + 5), (255, 240, 240), (20, 10, 10))

    superficie.blit(i_s1, (panel_rect.x + 32, layout["fila1_y"]))
    superficie.blit(i_s2, (panel_rect.x + 32, layout["fila2_y"]))

    dibujar_texto_con_borde(superficie, fuente_texto, f"Elote  S:{semillas['semilla1']} P:{cosechas['planta1']}", (panel_rect.x + 100, layout["fila1_y"] + 8), (34, 25, 20), (255, 255, 255))
    dibujar_texto_con_borde(superficie, fuente_texto, f"Jitomate  S:{semillas['semilla2']} P:{cosechas['planta2']}", (panel_rect.x + 100, layout["fila2_y"] + 8), (34, 25, 20), (255, 255, 255))

    if modo_tienda == "compra":
        draw_btn(layout["accion1"], f"Comprar {PRECIO_COMPRA_SEMILLA_1}", estado_juego.monedas >= PRECIO_COMPRA_SEMILLA_1)
        draw_btn(layout["accion2"], f"Comprar {PRECIO_COMPRA_SEMILLA_2}", estado_juego.monedas >= PRECIO_COMPRA_SEMILLA_2)
    else:
        superficie.blit(iv_s1, (layout["venta_s1"].x - 34, layout["venta_s1"].y + 5))
        superficie.blit(iv_p1, (layout["venta_p1"].x - 34, layout["venta_p1"].y + 5))
        draw_btn(layout["venta_s1"], f"Sobre {PRECIO_VENTA_SEMILLA_1}", semillas['semilla1'] > 0)
        draw_btn(layout["venta_p1"], f"Planta {PRECIO_VENTA_PLANTA_1}", cosechas['planta1'] > 0)

        superficie.blit(iv_s2, (layout["venta_s2"].x - 34, layout["venta_s2"].y + 5))
        superficie.blit(iv_p2, (layout["venta_p2"].x - 34, layout["venta_p2"].y + 5))
        draw_btn(layout["venta_s2"], f"Sobre {PRECIO_VENTA_SEMILLA_2}", semillas['semilla2'] > 0)
        draw_btn(layout["venta_p2"], f"Planta {PRECIO_VENTA_PLANTA_2}", cosechas['planta2'] > 0)


# ==========================================
# CLASES DE LÓGICA (OOP, Encapsulamiento y Herencia)
# ==========================================
class EstadoJuego:
    """Clase principal que maneja el estado general y encapsula datos vitales (OOP Encapsulamiento)."""
    def __init__(self):
        self.__monedas = 120  # Atributo privado
        self.dia_actual = 1

    @property
    def monedas(self):
        """Getter para obtener la cantidad de monedas."""
        return self.__monedas

    @monedas.setter
    def monedas(self, valor):
        """Setter que previene que las monedas bajen de cero."""
        self.__monedas = max(0, valor)

class EntidadVisible:
    """Clase Base (Superclase) para todos los objetos dibujables en pantalla (OOP Herencia)."""
    def __init__(self, x, y, imagen):
        self.image = imagen
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, superficie, cam_x, cam_y):
        """Método heredable para renderizar la entidad basada en la cámara."""
        superficie.blit(self.image, (self.rect.x - cam_x, self.rect.y - cam_y))

class Obstaculo(EntidadVisible):
    """Subclase de EntidadVisible que representa objetos estáticos con colisión."""
    def __init__(self, x, y, imagen):
        super().__init__(x, y, imagen)
        self.hitbox = pygame.Rect(self.rect.x, self.rect.bottom - TAM_TILE, self.rect.width, TAM_TILE)

class Vaca(EntidadVisible):
    """Subclase de EntidadVisible que representa al NPC interactivo."""
    def __init__(self, x, y, hoja, icono_carrito=None):
        frames = [
            extraer_sprite_exacto(hoja, 1, 1, 2, 2, ESCALA_VACA),
            extraer_sprite_exacto(hoja, 3, 1, 2, 2, ESCALA_VACA),
            extraer_sprite_exacto(hoja, 5, 1, 2, 2, ESCALA_VACA),
        ]
        super().__init__(x, y, frames[0])
        self.frames = frames
        self.timer = 0.0

        hb_w, hb_h = int(self.rect.width * 0.82), int(self.rect.height * 0.75)
        self.hitbox = pygame.Rect(0, 0, hb_w, hb_h)
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.bottom = self.rect.bottom - int(self.rect.height * 0.06)

        self.icono_carrito = icono_carrito
        self.t_flotacion = 0.0

    def update(self, dt):
        """Actualiza la animación y la posición del indicador flotante."""
        self.timer += VELOCIDAD_ANIMACION_VACA
        self.image = self.frames[int(self.timer) % len(self.frames)]
        self.t_flotacion += dt * 5.0

    def draw(self, superficie, cam_x, cam_y):
        """Dibuja a la vaca y su icono flotante de tienda."""
        super().draw(superficie, cam_x, cam_y)
        if self.icono_carrito is not None:
            desfase_y = int(math.sin(self.t_flotacion) * 3)
            icono_x = self.rect.centerx - (self.icono_carrito.get_width() // 2)
            superficie.blit(self.icono_carrito, (icono_x - cam_x, self.rect.y - self.icono_carrito.get_height() - 1 + desfase_y - cam_y))

class Jugador(EntidadVisible):
    """Subclase de EntidadVisible para el personaje controlable."""
    def __init__(self, x, y, hoja):
        self.direccion = 'abajo'
        self.animaciones = {
            'abajo': [extraer_sprite_exacto(hoja, (i*3)+1, 1, 3, 3, ESCALA) for i in range(4)],
            'arriba': [extraer_sprite_exacto(hoja, (i*3)+1, 4, 3, 3, ESCALA) for i in range(4)],
            'izquierda': [extraer_sprite_exacto(hoja, (i*3)+1, 7, 3, 3, ESCALA) for i in range(4)],
            'derecha': [extraer_sprite_exacto(hoja, (i*3)+1, 10, 3, 3, ESCALA) for i in range(4)],
        }
        super().__init__(x, y, self.animaciones['abajo'][0])
        self.timer = 0
       
        self.hitbox = pygame.Rect(0, 0, TAM_TILE, TAM_TILE // 2)
        self.hitbox.center = self.rect.center
        self.fx, self.fy = float(self.hitbox.x), float(self.hitbox.y)

    def update(self, muros):
        """Procesa el input, mueve la hitbox de forma fluida y maneja colisiones."""
        teclas = pygame.key.get_pressed()
        vx, vy = 0, 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: vx = -VELOCIDAD_JUGADOR; self.direccion = 'izquierda'
        elif teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: vx = VELOCIDAD_JUGADOR; self.direccion = 'derecha'
        if teclas[pygame.K_UP] or teclas[pygame.K_w]: vy = -VELOCIDAD_JUGADOR; self.direccion = 'arriba'
        elif teclas[pygame.K_DOWN] or teclas[pygame.K_s]: vy = VELOCIDAD_JUGADOR; self.direccion = 'abajo'

        if vx != 0 and vy != 0: vx, vy = vx * 0.707, vy * 0.707

        if vx != 0 or vy != 0:
            self.timer += VELOCIDAD_ANIMACION
            self.image = self.animaciones[self.direccion][int(self.timer % 4)]
        else:
            self.image = self.animaciones[self.direccion][0]

        self.fx += vx
        self.hitbox.x = round(self.fx)
        for muro in muros:
            if self.hitbox.colliderect(muro):
                if vx > 0: self.hitbox.right = muro.left
                elif vx < 0: self.hitbox.left = muro.right
                self.fx = float(self.hitbox.x)

        self.fy += vy
        self.hitbox.y = round(self.fy)
        for muro in muros:
            if self.hitbox.colliderect(muro):
                if vy > 0: self.hitbox.bottom = muro.top
                elif vy < 0: self.hitbox.top = muro.bottom
                self.fy = float(self.hitbox.y)

        self.rect.center = self.hitbox.center

class Camara:
    """Calcula el offset para mantener al jugador en el centro de la pantalla."""
    def __init__(self, ancho, alto):
        self.x, self.y = 0, 0
        self.ancho, self.alto = ancho, alto

    def actualizar(self, objetivo_rect):
        self.x = max(0, min(objetivo_rect.centerx - self.ancho // 2, ANCHO_MAPA - self.ancho))
        self.y = max(0, min(objetivo_rect.centery - self.alto // 2, ALTO_MAPA - self.alto))

class Granja:
    """Gestiona el terreno, arado, riego y crecimiento de cultivos."""
    def __init__(self, tile_pasto, sprites_arados):
        self.tile = tile_pasto
        self.sprites_arados = sprites_arados
        self.tile_w = tile_pasto.get_width()
        self.tile_h = tile_pasto.get_height()
        self.terreno_arado = {}
        self.cultivos = {}
        self.terreno_regado = set()

    def get_tile_info(self, mouse_pos, cam_x, cam_y):
        """Convierte una coordenada de pantalla a coordenada del grid de la granja."""
        col = int((mouse_pos[0] + cam_x) // self.tile_w)
        fila = int((mouse_pos[1] + cam_y) // self.tile_h)
        return pygame.Rect(col * self.tile_w, fila * self.tile_h, self.tile_w, self.tile_h), col, fila

    def es_arable(self, mouse_pos, cam_x, cam_y, jugador_rect, objetos):
        tile_rect, col, fila = self.get_tile_info(mouse_pos, cam_x, cam_y)
        if (col, fila) in self.terreno_arado: return False
        if not tile_rect.colliderect(jugador_rect.inflate(self.tile_w * 1.5, self.tile_h * 1.5)): return False
        return not any(tile_rect.colliderect(obj.rect) for obj in objetos)

    def intentar_arar(self, mouse_pos, cam_x, cam_y, jugador_rect, objetos):
        if self.es_arable(mouse_pos, cam_x, cam_y, jugador_rect, objetos):
            _, col, fila = self.get_tile_info(mouse_pos, cam_x, cam_y)
            self.terreno_arado[(col, fila)] = random.choice(self.sprites_arados)

    def es_plantable(self, mouse_pos, cam_x, cam_y, jugador_rect, inventario, slot_semilla):
        tile_rect, col, fila = self.get_tile_info(mouse_pos, cam_x, cam_y)
        if (col, fila) not in self.terreno_arado or (col, fila) in self.cultivos: return False
        if inventario.cantidades.get(slot_semilla, 0) <= 0: return False
        return tile_rect.colliderect(jugador_rect.inflate(self.tile_w * 1.5, self.tile_h * 1.5))

    def intentar_plantar(self, mouse_pos, cam_x, cam_y, jugador_rect, fases_sprite, tipo, sprite_item, inventario, slot_semilla):
        if self.es_plantable(mouse_pos, cam_x, cam_y, jugador_rect, inventario, slot_semilla):
            _, col, fila = self.get_tile_info(mouse_pos, cam_x, cam_y)
            self.cultivos[(col, fila)] = {"fases": fases_sprite, "etapa": 0, "tipo": tipo, "item": sprite_item}
            inventario.gastar_semilla(slot_semilla)

    def regar_area_recursiva(self, col, fila, visitados=None):
        """
        [MÉTODO RECURSIVO]
        Se llama a sí mismo para regar toda la tierra arada adyacente conectada.
        """
        if visitados is None:
            visitados = set()

        if (col, fila) in visitados or (col, fila) in self.terreno_regado or (col, fila) not in self.terreno_arado:
            return
            
        visitados.add((col, fila))
        self.terreno_regado.add((col, fila))

        self.regar_area_recursiva(col + 1, fila, visitados) # Derecha
        self.regar_area_recursiva(col - 1, fila, visitados) # Izquierda
        self.regar_area_recursiva(col, fila + 1, visitados) # Abajo
        self.regar_area_recursiva(col, fila - 1, visitados) # Arriba

    def intentar_regar(self, mouse_pos, cam_x, cam_y, jugador_rect):
        """Inicia la acción de riego, la cual desencadena la recursión."""
        tile_rect, col, fila = self.get_tile_info(mouse_pos, cam_x, cam_y)
        area_interaccion = jugador_rect.inflate(self.tile_w * 1.5, self.tile_h * 1.5)
        
        if tile_rect.colliderect(area_interaccion) and (col, fila) in self.terreno_arado:
            self.regar_area_recursiva(col, fila)

    def intentar_usar_hacha(self, mouse_pos, cam_x, cam_y, jugador_rect, inventario):
        """Con el hacha cosechas las plantas maduras o destruyes terreno arado."""
        tile_rect, col, fila = self.get_tile_info(mouse_pos, cam_x, cam_y)
        area_interaccion = jugador_rect.inflate(self.tile_w * 1.5, self.tile_h * 1.5)
        
        if tile_rect.colliderect(area_interaccion):
            if (col, fila) in self.cultivos:
                datos = self.cultivos[(col, fila)]
                # Solo cosecha item real si estaba maduro
                if datos["etapa"] == 3: 
                    if datos["tipo"] == "elote":
                        inventario.sumar_tienda(5, 1, datos["item"]) 
                    elif datos["tipo"] == "tomate":
                        inventario.sumar_tienda(6, 1, datos["item"])
                del self.cultivos[(col, fila)]
            elif (col, fila) in self.terreno_arado:
                del self.terreno_arado[(col, fila)]
                if (col, fila) in self.terreno_regado:
                    self.terreno_regado.remove((col, fila))

    def avanzar_dia(self):
        """Progresa la etapa de los cultivos si estaban regados y seca la tierra."""
        for pos, datos in self.cultivos.items():
            if pos in self.terreno_regado and datos["etapa"] < 3:
                datos["etapa"] += 1 
        self.terreno_regado.clear()

    def draw(self, superficie, cam_x, cam_y):
        """Renderiza todo el mapa base y los cultivos."""
        col_inicio = int(cam_x // self.tile_w)
        col_fin = int((cam_x + ANCHO_PANTALLA) // self.tile_w) + 1
        fila_inicio = int(cam_y // self.tile_h)
        fila_fin = int((cam_y + ALTO_PANTALLA) // self.tile_h) + 1

        for c in range(col_inicio, col_fin):
            for f in range(fila_inicio, fila_fin):
                x = c * self.tile_w - cam_x
                y = f * self.tile_h - cam_y
                superficie.blit(self.tile, (x, y))
                if (c, f) in self.terreno_arado:
                    superficie.blit(self.terreno_arado[(c, f)], (x, y))
                    if (c, f) in self.terreno_regado:
                        sombra = pygame.Surface((self.tile_w, self.tile_h), pygame.SRCALPHA)
                        sombra.fill((0, 0, 0, 60)) 
                        superficie.blit(sombra, (x, y))
                if (c, f) in self.cultivos:
                    datos = self.cultivos[(c, f)]
                    superficie.blit(datos["fases"][datos["etapa"]], (x, y))

    def draw_hover(self, superficie, mouse_pos, cam_x, cam_y, jugador_rect, objetos, inventario, accion="arar"):
        """Dibuja un rectángulo selector si la acción es permitida."""
        dibujar = False
        tile_rect, col, fila = self.get_tile_info(mouse_pos, cam_x, cam_y)
        area_interaccion = jugador_rect.inflate(self.tile_w * 1.5, self.tile_h * 1.5)
        if not tile_rect.colliderect(area_interaccion): return
        
        if accion == "arar":
            if self.es_arable(mouse_pos, cam_x, cam_y, jugador_rect, objetos): dibujar = True
        elif accion == "plantar_elote":
            if self.es_plantable(mouse_pos, cam_x, cam_y, jugador_rect, inventario, 3): dibujar = True
        elif accion == "plantar_tomate":
            if self.es_plantable(mouse_pos, cam_x, cam_y, jugador_rect, inventario, 4): dibujar = True
        elif accion == "hacha":
            if (col, fila) in self.cultivos or (col, fila) in self.terreno_arado: dibujar = True
        elif accion == "regar":
            if (col, fila) in self.terreno_arado: dibujar = True
                
        if dibujar:
            rect_dibujo = pygame.Rect(tile_rect.x - cam_x, tile_rect.y - cam_y, self.tile_w, self.tile_h)
            pygame.draw.rect(superficie, (255, 0, 0) if accion != "regar" else (0, 100, 255), rect_dibujo, 3)

class Inventario:
    """Maneja los items que el jugador porta actualmente."""
    def __init__(self, imagen):
        ancho_deseado = 600
        escala = ancho_deseado / imagen.get_width()
        self.image = pygame.transform.scale(imagen, (ancho_deseado, int(imagen.get_height() * escala)))
        self.rect = self.image.get_rect(topleft=(ANCHO_PANTALLA // 2 - 300, ALTO_PANTALLA - self.image.get_height() - 10))
        
        self.slots = [None] * 7
        self.cantidades = {3: 0, 4: 0, 5: 0, 6: 0} 
        self.seleccionado = 0  
        self.fuente_cant = pygame.font.Font(None, 24)

    def set_item(self, indice_slot, sprite, cantidad=0):
        """Asigna un ítem manualmente a un slot."""
        if 0 <= indice_slot < len(self.slots):
            self.slots[indice_slot] = sprite
            if indice_slot in self.cantidades:
                self.cantidades[indice_slot] = cantidad

    def sumar_tienda(self, indice_slot, cantidad, sprite_default):
        """Actualiza la cantidad de ítems del jugador desde la tienda."""
        if indice_slot in self.cantidades:
            self.cantidades[indice_slot] += cantidad
            if self.cantidades[indice_slot] > 0 and self.slots[indice_slot] is None:
                self.slots[indice_slot] = sprite_default
            elif self.cantidades[indice_slot] <= 0:
                self.cantidades[indice_slot] = 0
                self.slots[indice_slot] = None

    def gastar_semilla(self, indice_slot):
        """Resta una semilla del inventario. Si llega a 0, la borra."""
        if indice_slot in self.cantidades and self.cantidades[indice_slot] > 0:
            self.cantidades[indice_slot] -= 1
            if self.cantidades[indice_slot] <= 0:
                self.slots[indice_slot] = None 

    def draw(self, superficie):
        """Dibuja el inventario en la parte inferior de la pantalla."""
        superficie.blit(self.image, self.rect)
        margen_x_inicial = 20  
        margen_y_inicial = 55  
        espacio_entre_slots = 82 
        tam_sprite = 64
        radio_sombra = 35
        
        for i in range(7):
            x = self.rect.x + margen_x_inicial + (i * espacio_entre_slots)
            y = self.rect.y + margen_y_inicial
            
            if i == self.seleccionado:
                sombra_surface = pygame.Surface((radio_sombra*2, radio_sombra*2), pygame.SRCALPHA)
                pygame.draw.circle(sombra_surface, (0, 0, 0, 100), (radio_sombra, radio_sombra), radio_sombra)
                centro_x = x + (tam_sprite // 2) - radio_sombra
                centro_y = y + (tam_sprite // 2) - radio_sombra
                superficie.blit(sombra_surface, (centro_x, centro_y))

            if self.slots[i]:
                superficie.blit(self.slots[i], (x, y))
                if i in self.cantidades and self.cantidades[i] > 0:
                    texto_cant = str(self.cantidades[i])
                    dibujar_texto_con_borde(superficie, self.fuente_cant, texto_cant, (x + 45, y + 45), (255, 255, 255), (0, 0, 0))

# ==========================================
# FUNCIÓN PRINCIPAL
# ==========================================
def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
    pygame.display.set_caption("Moonvale - Versión Final OOP & Recursión")
    reloj = pygame.time.Clock()
    
    estado_juego = EstadoJuego()
    transicion_dia_restante = 0.0
    tienda_abierta = False
    modo_tienda = "compra"

    base = "Sprout Lands - Sprites - Basic pack"
    try:
        hoja_pasto = pygame.image.load(asset_path(base, "Tilesets", "Grass.png")).convert_alpha()
        hoja_cercas = pygame.image.load(asset_path(base, "Tilesets", "Fences.png")).convert_alpha()
        hoja_pj = pygame.image.load(asset_path(base, "Characters", "Basic Charakter Spritesheet.png")).convert_alpha()
        hoja_vacas = pygame.image.load(asset_path(base, "Characters", "Free Cow Sprites.png")).convert_alpha()
        hoja_iconos_blancos = pygame.image.load(asset_path("Sprout Lands - UI Pack - Basic pack", "Sprite sheets", "Icons", "white icons.png")).convert_alpha()
        hoja_plantas = pygame.image.load(asset_path(base, "Objects", "Basic_Plants.png")).convert_alpha()
        ui_menu_tienda = pygame.image.load(asset_path("Sprout Lands - UI Pack - Basic pack", "Sprite sheets", "Setting menu.png")).convert_alpha()
        ui_boton = pygame.image.load(asset_path("Sprout Lands - UI Pack - Basic pack", "Sprite sheets", "buttons", "Square Buttons 26x19.png")).convert_alpha()
        hoja_objs = pygame.image.load(asset_path(base, "Objects", "Basic Grass Biom things 1.png")).convert_alpha()
        hoja_tierra = pygame.image.load(asset_path(base, "Tilesets", "Tilled Dirt.png")).convert_alpha()
        casa_superior = pygame.image.load(asset_path("House4.png")).convert_alpha()
        casa_superior = pygame.transform.scale(casa_superior, (int(casa_superior.get_width() * ESCALA_CASA), int(casa_superior.get_height() * ESCALA_CASA)))

        ruta_fuente = asset_path("Sprout Lands - UI Pack - Basic pack", "fonts", "pixelFont-7-8x14-sproutLands.ttf")
        fuente_dia = pygame.font.Font(ruta_fuente, 44)
        fuente_transicion = pygame.font.Font(ruta_fuente, 56)
        fuente_muerte = pygame.font.Font(ruta_fuente, 100) 
        fuente_tienda_titulo = pygame.font.Font(ruta_fuente, 36)
        fuente_tienda = pygame.font.Font(ruta_fuente, 24)
       
        img_inventario = pygame.image.load(asset_path(base, "Objects", "Inventory_Light_example_with_slots.png")).convert_alpha()
        hoja_herramientas = pygame.image.load(asset_path(base, "Objects", "Basic tools and meterials.png")).convert_alpha()
        
        pygame.mixer.music.load(asset_path("audio.mpeg"))
        pygame.mixer.music.set_volume(VOLUMEN_MUSICA)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Error cargando archivos: {e}")
        return

    sprites_tierra = [extraer_sprite_exacto(hoja_tierra, c, f, 1, 1, ESCALA) for c, f in [(1,1), (2,1), (3,1), (1,2), (2,2), (3,2)]]
    
    # ----------------------------------------------------
    # DICCIONARIO DE DECORACIONES Y MAPA "BOSQUE FRONDOSO"
    # ----------------------------------------------------
    sprites = {
        'A': extraer_sprite_exacto(hoja_objs, 2, 1, 2, 2, ESCALA),        
        'B': extraer_sprite_exacto(hoja_objs, 4, 1, 2, 2, ESCALA),      
        'C': extraer_sprite_exacto(hoja_objs, 2, 3, 2, 2, ESCALA),            
        'D': extraer_sprite_exacto(hoja_objs, 9, 3, 1, 2, ESCALA),            
        'E': extraer_sprite_exacto(hoja_objs, 6, 4, 1, 1, ESCALA),    
        'F': extraer_sprite_exacto(hoja_objs, 7, 4, 1, 1, ESCALA),        
        'G': extraer_sprite_exacto(hoja_objs, 7, 2, 1, 1, ESCALA),    
        'H': extraer_sprite_exacto(hoja_objs, 8, 2, 1, 1, ESCALA),    
        'I': extraer_sprite_exacto(hoja_objs, 9, 2, 1, 1, ESCALA),      
        'J': extraer_sprite_exacto(hoja_objs, 7, 3, 1, 1, ESCALA),      
        'K': extraer_sprite_exacto(hoja_objs, 9, 5, 1, 1, ESCALA),        
    }

    # Marco lateral denso, zona de casa rodeada y centro libre
    layout = [
        # Borde Izquierdo
        ('A', 0, 0), ('B', 2, 0), ('D', 4, 0), ('A', 1, 2), ('H', 3, 2), ('B', 0, 4), 
        ('J', 2, 4), ('A', 4, 4), ('A', 1, 6), ('D', 3, 6), ('B', 0, 8), ('H', 2, 8), 
        ('A', 4, 8), ('A', 1, 10), ('J', 3, 10), ('B', 0, 12), ('D', 2, 12), ('A', 4, 12), 
        ('A', 1, 14), ('H', 3, 14), ('B', 0, 16), ('J', 2, 16), ('A', 4, 16), ('A', 1, 18), 
        ('D', 3, 18), ('B', 0, 20), ('H', 2, 20), ('A', 4, 20), ('A', 1, 22), ('J', 3, 22), 
        ('B', 0, 24), ('D', 2, 24), ('A', 4, 24), ('A', 1, 26), ('H', 3, 26), ('B', 0, 28), 
        ('J', 2, 28), ('A', 4, 28), ('A', 1, 30), ('D', 3, 30),

        # Borde Derecho
        ('A', 27, 0), ('B', 29, 0), ('D', 31, 0), ('A', 28, 2), ('H', 30, 2), ('B', 27, 4), 
        ('J', 29, 4), ('A', 31, 4), ('A', 28, 6), ('D', 30, 6), ('B', 27, 8), ('H', 29, 8), 
        ('A', 31, 8), ('A', 28, 10), ('J', 30, 10), ('B', 27, 12), ('D', 29, 12), ('A', 31, 12), 
        ('A', 28, 14), ('H', 30, 14), ('B', 27, 16), ('J', 29, 16), ('A', 31, 16), ('A', 28, 18), 
        ('D', 30, 18), ('B', 27, 20), ('H', 29, 20), ('A', 31, 20), ('A', 28, 22), ('J', 30, 22), 
        ('B', 27, 24), ('D', 29, 24), ('A', 31, 24), ('A', 28, 26), ('H', 30, 26), ('B', 27, 28), 
        ('J', 29, 28), ('A', 31, 28), ('A', 28, 30), ('D', 30, 30),

        # Alrededor de la casa (Arriba al centro)
        ('A', 6, 0), ('B', 8, 1), ('A', 10, 0), ('D', 12, 1), ('A', 18, 0), ('B', 20, 1), 
        ('H', 22, 0), ('A', 24, 1), ('A', 26, 0), ('B', 7, 2), ('J', 9, 3), ('A', 11, 2), 
        ('A', 19, 3), ('D', 21, 2), ('A', 23, 3), ('B', 25, 2),

        # Borde Inferior
        ('A', 6, 30), ('B', 9, 29), ('J', 12, 30), ('A', 15, 29), ('D', 18, 30), ('B', 21, 29), ('A', 24, 30)
    ]

    tile_pasto = extraer_sprite_exacto(hoja_pasto, 1, 6, 1, 1, ESCALA)
    
    cerca_w, cerca_h = hoja_cercas.get_width() // 4, hoja_cercas.get_height() // 2
    def ext_cerca(c, f):
        s = pygame.Surface((cerca_w, cerca_h), pygame.SRCALPHA)
        s.blit(hoja_cercas, (0, 0), pygame.Rect((c-1)*cerca_w, (f-1)*cerca_h, cerca_w, cerca_h))
        return pygame.transform.scale(s.subsurface((0,0,cerca_w,cerca_h//2)), (TAM_TILE, int(TAM_TILE*1)))

    sprite_cerca_izq, sprite_cerca_mid, sprite_cerca_der = ext_cerca(2, 2), ext_cerca(3, 2), ext_cerca(4, 2)
    sprite_azada = extraer_sprite_exacto(hoja_herramientas, 3, 1, 1, 1, ESCALA)
    sprite_hacha = extraer_sprite_exacto(hoja_herramientas, 2, 1, 1, 1, ESCALA)
    sprite_regadera = extraer_sprite_exacto(hoja_herramientas, 1, 1, 1, 1, ESCALA)

    sprite_semilla_elote = extraer_sprite_exacto(hoja_plantas, 1, 1, 1, 1, ESCALA)
    fases_elote = [extraer_sprite_exacto(hoja_plantas, col, 1, 1, 1, ESCALA) for col in range(2, 6)]
    item_elote = extraer_sprite_exacto(hoja_plantas, 6, 1, 1, 1, ESCALA)

    sprite_semilla_tomate = extraer_sprite_exacto(hoja_plantas, 1, 2, 1, 1, ESCALA)
    fases_tomate = [extraer_sprite_exacto(hoja_plantas, col, 2, 1, 1, ESCALA) for col in range(2, 6)]
    item_tomate = extraer_sprite_exacto(hoja_plantas, 6, 2, 1, 1, ESCALA)

    icono_rect = pygame.Rect(34, 19, 13, 9)
    icono_carrito = pygame.transform.scale(
        hoja_iconos_blancos.subsurface(icono_rect), (icono_rect.width * 5, icono_rect.height * 5)
    )

    icono_semilla_1 = extraer_sprite_exacto(hoja_plantas, 1, 1, 1, 1, ESCALA_SEMILLA_MENU)
    icono_semilla_2 = extraer_sprite_exacto(hoja_plantas, 1, 2, 1, 1, ESCALA_SEMILLA_MENU)
    icono_planta_1 = extraer_sprite_exacto(hoja_plantas, 6, 1, 1, 1, ESCALA_SEMILLA_MENU)
    icono_planta_2 = extraer_sprite_exacto(hoja_plantas, 6, 2, 1, 1, ESCALA_SEMILLA_MENU)

    icono_semilla_1_venta = pygame.transform.scale(icono_semilla_1, (TAM_ICONO_VENTA, TAM_ICONO_VENTA))
    icono_semilla_2_venta = pygame.transform.scale(icono_semilla_2, (TAM_ICONO_VENTA, TAM_ICONO_VENTA))
    icono_planta_1_venta = pygame.transform.scale(icono_planta_1, (TAM_ICONO_VENTA, TAM_ICONO_VENTA))
    icono_planta_2_venta = pygame.transform.scale(icono_planta_2, (TAM_ICONO_VENTA, TAM_ICONO_VENTA))

    ui_menu_tienda = pygame.transform.scale(ui_menu_tienda, (660, 372))
    ui_boton = ui_boton.subsurface(pygame.Rect(0, 0, 26, 19))

    granja = Granja(tile_pasto, sprites_tierra)
    jugador = Jugador(ANCHO_MAPA // 2, ALTO_MAPA // 2, hoja_pj)
    camara = Camara(ANCHO_PANTALLA, ALTO_PANTALLA)
   
    inventario = Inventario(img_inventario)
    inventario.set_item(0, sprite_azada)
    inventario.set_item(1, sprite_hacha)
    inventario.set_item(2, sprite_regadera)
    inventario.set_item(3, sprite_semilla_elote, cantidad=5)
    inventario.set_item(4, sprite_semilla_tomate, cantidad=5)

    objetos = [Obstaculo(c*TAM_TILE, f*TAM_TILE, sprites[t]) for t, c, f in layout]
    casa_x, casa_y = (ANCHO_MAPA // 2) - (casa_superior.get_width() // 2), 0
    objetos.append(Obstaculo(casa_x, casa_y, casa_superior))

    cerca_y = casa_y + int(casa_superior.get_height() * 0.78)
    for i in range(6):
        objetos.append(Obstaculo(casa_x - ((i + 1) * TAM_TILE), cerca_y + (TAM_TILE // 8), 
                                 sprite_cerca_der if i==0 else sprite_cerca_izq if i==5 else sprite_cerca_mid))
        objetos.append(Obstaculo(casa_x + casa_superior.get_width() + (i * TAM_TILE), cerca_y + (TAM_TILE // 8), 
                                 sprite_cerca_izq if i==0 else sprite_cerca_der if i==5 else sprite_cerca_mid))

    vacas = [Vaca(casa_x - (6 * TAM_TILE) + (TAM_TILE // 2) - 32, cerca_y + (TAM_TILE // 8) + TAM_TILE - 21, hoja_vacas, icono_carrito)]
    panel_tienda_rect = ui_menu_tienda.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2))
    layout_tienda = construir_layout_tienda(panel_tienda_rect)

    puerta_rect = pygame.Rect(casa_x + (casa_superior.get_width() // 2) - (TAM_TILE // 2), casa_y + int(casa_superior.get_height() * 0.66), TAM_TILE, int(TAM_TILE * 1.3))
    zona_interaccion_puerta = puerta_rect.inflate(int(TAM_TILE * 0.35), int(TAM_TILE * 0.5))
    zona_interaccion_puerta.y += int(TAM_TILE * 0.5)

    while True:
        dt = reloj.tick(FPS) / 1000.0
        
        # ==========================================
        # CONDICIÓN DE VICTORIA (Rúbrica)
        # ==========================================
        if estado_juego.monedas >= META_MONEDAS_VICTORIA:
            pantalla.fill((0, 0, 0))
            dibujar_texto_con_borde(
                pantalla, fuente_transicion, "¡HAS GANADO!",
                (ANCHO_PANTALLA // 2 - 150, ALTO_PANTALLA // 2 - 50),
                (255, 215, 0), (0, 0, 0)
            )
            dibujar_texto_con_borde(
                pantalla, fuente_dia, f"Conseguiste {META_MONEDAS_VICTORIA} monedas.",
                (ANCHO_PANTALLA // 2 - 200, ALTO_PANTALLA // 2 + 20),
                (255, 255, 255), (0, 0, 0)
            )
            pygame.display.flip()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            continue

        # ==========================================
        # CONDICIÓN DE DERROTA (YOU DIED)
        # ==========================================
        elif estado_juego.dia_actual >= DIA_LIMITE_DERROTA:
            pantalla.fill((0, 0, 0))
            texto_muerte = fuente_muerte.render("YOU DIED", True, (200, 0, 0))
            sombra_muerte = fuente_muerte.render("YOU DIED", True, (50, 0, 0))
            x_m = ANCHO_PANTALLA // 2 - texto_muerte.get_width() // 2
            y_m = ALTO_PANTALLA // 2 - texto_muerte.get_height() // 2
            
            pantalla.blit(sombra_muerte, (x_m + 4, y_m + 4))
            pantalla.blit(texto_muerte, (x_m, y_m))
            
            dibujar_texto_con_borde(
                pantalla, fuente_dia, f"No conseguiste {META_MONEDAS_VICTORIA} monedas.",
                (ANCHO_PANTALLA // 2 - 260, ALTO_PANTALLA // 2 + 60),
                (180, 180, 180), (0, 0, 0)
            )
            pygame.display.flip()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            continue

        if transicion_dia_restante > 0:
            transicion_dia_restante = max(0.0, transicion_dia_restante - dt)

        mouse_pos = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE and tienda_abierta:
                    tienda_abierta = False
                elif ev.key == pygame.K_e:
                    cerca_de_vaca = any(jugador.hitbox.colliderect(vaca.hitbox.inflate(70, 70)) for vaca in vacas)
                    if tienda_abierta:
                        tienda_abierta = False
                    elif cerca_de_vaca and transicion_dia_restante == 0:
                        tienda_abierta = True
                    elif transicion_dia_restante == 0 and not tienda_abierta and jugador.hitbox.colliderect(zona_interaccion_puerta):
                        estado_juego.dia_actual += 1
                        transicion_dia_restante = DURACION_TRANSICION_DIA
                        granja.avanzar_dia()

                elif not tienda_abierta:
                    for i in range(7):
                        if ev.key == getattr(pygame, f"K_{i+1}"): inventario.seleccionado = i
           
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1 and tienda_abierta:
                    mpos = ev.pos
                    if layout_tienda["cerrar"].collidepoint(mpos):
                        tienda_abierta = False
                    elif layout_tienda["tab_compra"].collidepoint(mpos):
                        modo_tienda = "compra"
                    elif layout_tienda["tab_venta"].collidepoint(mpos):
                        modo_tienda = "venta"
                    elif modo_tienda == "compra" and layout_tienda["accion1"].collidepoint(mpos):
                        if estado_juego.monedas >= PRECIO_COMPRA_SEMILLA_1:
                            estado_juego.monedas -= PRECIO_COMPRA_SEMILLA_1
                            inventario.sumar_tienda(3, 1, sprite_semilla_elote)
                    elif modo_tienda == "compra" and layout_tienda["accion2"].collidepoint(mpos):
                        if estado_juego.monedas >= PRECIO_COMPRA_SEMILLA_2:
                            estado_juego.monedas -= PRECIO_COMPRA_SEMILLA_2
                            inventario.sumar_tienda(4, 1, sprite_semilla_tomate)
                    elif modo_tienda == "venta" and layout_tienda["venta_s1"].collidepoint(mpos):
                        if inventario.cantidades.get(3, 0) > 0:
                            inventario.sumar_tienda(3, -1, sprite_semilla_elote)
                            estado_juego.monedas += PRECIO_VENTA_SEMILLA_1
                    elif modo_tienda == "venta" and layout_tienda["venta_p1"].collidepoint(mpos):
                        if inventario.cantidades.get(5, 0) > 0:
                            inventario.sumar_tienda(5, -1, item_elote)
                            estado_juego.monedas += PRECIO_VENTA_PLANTA_1
                    elif modo_tienda == "venta" and layout_tienda["venta_s2"].collidepoint(mpos):
                        if inventario.cantidades.get(4, 0) > 0:
                            inventario.sumar_tienda(4, -1, sprite_semilla_tomate)
                            estado_juego.monedas += PRECIO_VENTA_SEMILLA_2
                    elif modo_tienda == "venta" and layout_tienda["venta_p2"].collidepoint(mpos):
                        if inventario.cantidades.get(6, 0) > 0:
                            inventario.sumar_tienda(6, -1, item_tomate)
                            estado_juego.monedas += PRECIO_VENTA_PLANTA_2

                elif ev.button == 1 and not tienda_abierta and transicion_dia_restante == 0:
                    item_actual = inventario.seleccionado
                    if item_actual == 0:
                        granja.intentar_arar(mouse_pos, camara.x, camara.y, jugador.hitbox, objetos)
                    elif item_actual == 1:
                        granja.intentar_usar_hacha(mouse_pos, camara.x, camara.y, jugador.hitbox, inventario)
                    elif item_actual == 2:
                        granja.intentar_regar(mouse_pos, camara.x, camara.y, jugador.hitbox)
                    elif item_actual == 3:
                        granja.intentar_plantar(mouse_pos, camara.x, camara.y, jugador.hitbox, fases_elote, "elote", item_elote, inventario, 3)
                    elif item_actual == 4:
                        granja.intentar_plantar(mouse_pos, camara.x, camara.y, jugador.hitbox, fases_tomate, "tomate", item_tomate, inventario, 4)

        if transicion_dia_restante == 0 and not tienda_abierta:
            jugador.update(muros=[obj.hitbox for obj in objetos] + [v.hitbox for v in vacas])
        for vaca in vacas:
            vaca.update(dt)
            
        camara.actualizar(jugador.rect)

        granja.draw(pantalla, camara.x, camara.y)

        entidades = objetos + vacas + [jugador]
        entidades.sort(key=lambda e: e.rect.bottom)
        for e in entidades:
            e.draw(pantalla, camara.x, camara.y)

        if not tienda_abierta and transicion_dia_restante == 0:
            accion_hover = "ninguna"
            if inventario.seleccionado == 0: accion_hover = "arar"
            elif inventario.seleccionado == 1: accion_hover = "hacha"
            elif inventario.seleccionado == 2: accion_hover = "regar"
            elif inventario.seleccionado == 3: accion_hover = "plantar_elote"
            elif inventario.seleccionado == 4: accion_hover = "plantar_tomate"
            
            if accion_hover != "ninguna":
                granja.draw_hover(pantalla, mouse_pos, camara.x, camara.y, jugador.hitbox, objetos, inventario, accion=accion_hover)

        # Interfaz general
        dibujar_texto_con_borde(pantalla, fuente_dia, f"Dia: {estado_juego.dia_actual}/{DIA_LIMITE_DERROTA}", (20, 20), (255, 255, 255), (0, 0, 0))
        dibujar_texto_con_borde(pantalla, fuente_dia, f"Monedas: {estado_juego.monedas}/{META_MONEDAS_VICTORIA}", (20, 70), (255, 215, 0), (0, 0, 0))

        if transicion_dia_restante > 0:
            overlay = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA))
            overlay.fill((0, 0, 0))
            alpha = int(255 * (transicion_dia_restante / DURACION_TRANSICION_DIA))
            overlay.set_alpha(alpha)
            pantalla.blit(overlay, (0, 0))
            dibujar_texto_con_borde(pantalla, fuente_transicion, f"Dia {estado_juego.dia_actual}", (ANCHO_PANTALLA // 2 - 70, ALTO_PANTALLA // 2 - 36), (255, 255, 255), (0, 0, 0))

        if tienda_abierta and transicion_dia_restante == 0:
            semillas_info = {'semilla1': inventario.cantidades.get(3, 0), 'semilla2': inventario.cantidades.get(4, 0)}
            cosechas_info = {'planta1': inventario.cantidades.get(5, 0), 'planta2': inventario.cantidades.get(6, 0)}
            draw_tienda(pantalla, ui_menu_tienda, ui_boton, fuente_tienda_titulo, fuente_tienda, layout_tienda, modo_tienda, 
                        estado_juego, semillas_info, cosechas_info, icono_semilla_1, icono_semilla_2, icono_planta_1, icono_planta_2, 
                        icono_semilla_1_venta, icono_semilla_2_venta, icono_planta_1_venta, icono_planta_2_venta)

        if not tienda_abierta and transicion_dia_restante == 0:
            inventario.draw(pantalla)
            
        pygame.display.flip()

if __name__ == "__main__":
    main()