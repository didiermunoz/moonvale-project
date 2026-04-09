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


VELOCIDAD_JUGADOR = 5
VELOCIDAD_ANIMACION = 0.15
VELOCIDAD_ANIMACION_VACA = 0.05
ESCALA_CASA = 2.5
DURACION_TRANSICION_DIA = 1.0
ESCALA_VACA = 4
ESCALA_ICONO_CARRITO = 5
ESCALA_SEMILLA_MENU = 5
TAM_ICONO_VENTA = 28

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
    """
    Recorta un área específica de la hoja de sprites.
    col/fila: Basado en 1 (ej: Col 1 es el borde izquierdo).
    """
    x = (col - 1) * 16
    y = (fila - 1) * 16
    ancho_px = ancho_tiles * 16
    alto_px = alto_tiles * 16
   
    rect = pygame.Rect(x, y, ancho_px, alto_px)
    imagen = pygame.Surface((ancho_px, alto_px), pygame.SRCALPHA)
    imagen.blit(hoja, (0, 0), rect)
   
    return pygame.transform.scale(imagen, (int(ancho_px * escala), int(alto_px * escala)))


def dibujar_texto_con_borde(superficie, fuente, texto, pos, color_texto, color_borde):
    """Dibuja texto con borde simple para mejorar visibilidad."""
    x, y = pos
    texto_base = fuente.render(texto, True, color_texto)

    for dx in (-2, -1, 0, 1, 2):
        for dy in (-2, -1, 0, 1, 2):
            if dx == 0 and dy == 0:
                continue
            sombra = fuente.render(texto, True, color_borde)
            superficie.blit(sombra, (x + dx, y + dy))

    superficie.blit(texto_base, (x, y))


def construir_layout_tienda(panel_rect):
    """Genera rectangulos de UI para la tienda en base al panel."""
    boton_w = 120
    boton_h = 44

    tab_compra = pygame.Rect(panel_rect.x + 30, panel_rect.y + 58, boton_w, boton_h)
    tab_venta = pygame.Rect(panel_rect.x + 170, panel_rect.y + 58, boton_w, boton_h)
    cerrar = pygame.Rect(panel_rect.right - 54, panel_rect.y + 14, 32, 32)

    fila1_y = panel_rect.y + 122
    fila2_y = panel_rect.y + 228

    accion1 = pygame.Rect(panel_rect.right - 140, fila1_y + 8, 98, 38)
    accion2 = pygame.Rect(panel_rect.right - 140, fila2_y + 8, 98, 38)

    # En modo venta: Sobre arriba y Planta abajo, por cada cultivo.
    venta_x = panel_rect.right - 140
    venta_s1 = pygame.Rect(venta_x, fila1_y + 2, 98, 30)
    venta_p1 = pygame.Rect(venta_x, fila1_y + 42, 98, 30)
    venta_s2 = pygame.Rect(venta_x, fila2_y + 2, 98, 30)
    venta_p2 = pygame.Rect(venta_x, fila2_y + 42, 98, 30)

    return {
        "tab_compra": tab_compra,
        "tab_venta": tab_venta,
        "cerrar": cerrar,
        "accion1": accion1,
        "accion2": accion2,
        "venta_s1": venta_s1,
        "venta_p1": venta_p1,
        "venta_s2": venta_s2,
        "venta_p2": venta_p2,
        "fila1_y": fila1_y,
        "fila2_y": fila2_y,
    }


def draw_tienda(
    superficie,
    panel_img,
    boton_img,
    fuente_titulo,
    fuente_texto,
    layout,
    modo_tienda,
    monedas,
    semillas,
    cosechas,
    icono_semilla_1,
    icono_semilla_2,
    icono_planta_1,
    icono_planta_2,
    icono_semilla_1_venta,
    icono_semilla_2_venta,
    icono_planta_1_venta,
    icono_planta_2_venta,
):
    """Dibuja el menu de compra/venta y regresa sus rects de interaccion."""
    overlay = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    superficie.blit(overlay, (0, 0))

    panel_rect = panel_img.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2))
    superficie.blit(panel_img, panel_rect)

    # Tabs de modo
    color_on = (244, 219, 171)
    color_off = (184, 154, 118)
    pygame.draw.rect(superficie, color_on if modo_tienda == "compra" else color_off, layout["tab_compra"], border_radius=8)
    pygame.draw.rect(superficie, color_on if modo_tienda == "venta" else color_off, layout["tab_venta"], border_radius=8)

    # Botones de accion
    if modo_tienda == "compra":
        superficie.blit(boton_img, layout["accion1"])
        superficie.blit(boton_img, layout["accion2"])
    else:
        superficie.blit(boton_img, layout["venta_s1"])
        superficie.blit(boton_img, layout["venta_p1"])
        superficie.blit(boton_img, layout["venta_s2"])
        superficie.blit(boton_img, layout["venta_p2"])

    # Boton cerrar
    pygame.draw.rect(superficie, (120, 56, 48), layout["cerrar"], border_radius=6)

    dibujar_texto_con_borde(superficie, fuente_titulo, "Tienda de Vaca", (panel_rect.x + 24, panel_rect.y + 14), (34, 25, 20), (255, 255, 255))
    dibujar_texto_con_borde(superficie, fuente_texto, f"Monedas: {monedas}", (panel_rect.right - 210, panel_rect.y + 20), (34, 25, 20), (255, 255, 255))

    dibujar_texto_con_borde(superficie, fuente_texto, "Comprar", (layout["tab_compra"].x + 18, layout["tab_compra"].y + 11), (30, 20, 15), (255, 255, 255))
    dibujar_texto_con_borde(superficie, fuente_texto, "Vender", (layout["tab_venta"].x + 26, layout["tab_venta"].y + 11), (30, 20, 15), (255, 255, 255))
    dibujar_texto_con_borde(superficie, fuente_texto, "X", (layout["cerrar"].x + 9, layout["cerrar"].y + 5), (255, 240, 240), (20, 10, 10))

    # Filas de semillas
    icono_x = panel_rect.x + 32
    texto_x = panel_rect.x + 100

    superficie.blit(icono_semilla_1, (icono_x, layout["fila1_y"]))
    superficie.blit(icono_semilla_2, (icono_x, layout["fila2_y"]))

    dibujar_texto_con_borde(
        superficie,
        fuente_texto,
        f"Trigo  S:{semillas['semilla1']} P:{cosechas['planta1']}",
        (texto_x, layout["fila1_y"] + 8),
        (34, 25, 20),
        (255, 255, 255),
    )
    dibujar_texto_con_borde(
        superficie,
        fuente_texto,
        f"Jitomate  S:{semillas['semilla2']} P:{cosechas['planta2']}",
        (texto_x, layout["fila2_y"] + 8),
        (34, 25, 20),
        (255, 255, 255),
    )

    if modo_tienda == "compra":
        t1 = f"Comprar {PRECIO_COMPRA_SEMILLA_1}"
        t2 = f"Comprar {PRECIO_COMPRA_SEMILLA_2}"
        dibujar_texto_con_borde(superficie, fuente_texto, t1, (layout["accion1"].x + 8, layout["accion1"].y + 9), (30, 20, 15), (255, 255, 255))
        dibujar_texto_con_borde(superficie, fuente_texto, t2, (layout["accion2"].x + 8, layout["accion2"].y + 9), (30, 20, 15), (255, 255, 255))
    else:
        # Trigo: Sobre arriba, Planta abajo
        superficie.blit(icono_semilla_1_venta, (layout["venta_s1"].x - 34, layout["venta_s1"].y + 1))
        superficie.blit(icono_planta_1_venta, (layout["venta_p1"].x - 34, layout["venta_p1"].y + 1))
        dibujar_texto_con_borde(superficie, fuente_texto, f"Sobre {PRECIO_VENTA_SEMILLA_1}", (layout["venta_s1"].x + 8, layout["venta_s1"].y + 6), (30, 20, 15), (255, 255, 255))
        dibujar_texto_con_borde(superficie, fuente_texto, f"Planta {PRECIO_VENTA_PLANTA_1}", (layout["venta_p1"].x + 8, layout["venta_p1"].y + 6), (30, 20, 15), (255, 255, 255))

        # Jitomate: Sobre arriba, Planta abajo
        superficie.blit(icono_semilla_2_venta, (layout["venta_s2"].x - 34, layout["venta_s2"].y + 1))
        superficie.blit(icono_planta_2_venta, (layout["venta_p2"].x - 34, layout["venta_p2"].y + 1))
        dibujar_texto_con_borde(superficie, fuente_texto, f"Sobre {PRECIO_VENTA_SEMILLA_2}", (layout["venta_s2"].x + 8, layout["venta_s2"].y + 6), (30, 20, 15), (255, 255, 255))
        dibujar_texto_con_borde(superficie, fuente_texto, f"Planta {PRECIO_VENTA_PLANTA_2}", (layout["venta_p2"].x + 8, layout["venta_p2"].y + 6), (30, 20, 15), (255, 255, 255))

    return layout


# ==========================================
# CLASES DE LÓGICA
# ==========================================
class Camara:
    def __init__(self, ancho, alto):
        self.x = 0
        self.y = 0
        self.ancho = ancho
        self.alto = alto


    def actualizar(self, objetivo_rect):
        self.x = objetivo_rect.centerx - self.ancho // 2
        self.y = objetivo_rect.centery - self.alto // 2
        self.x = max(0, min(self.x, ANCHO_MAPA - self.ancho))
        self.y = max(0, min(self.y, ALTO_MAPA - self.alto))


class Granja:
    def __init__(self, tile_pasto, sprites_arados):
        self.tile = tile_pasto
        self.sprites_arados = sprites_arados
        self.tile_w = tile_pasto.get_width()
        self.tile_h = tile_pasto.get_height()
       
        # Diccionario para terreno arado
        self.terreno_arado = {}


    def get_tile_info(self, mouse_pos, cam_x, cam_y):
        """Calcula info útil (rect, col, fila) del tile bajo el ratón."""
        mx, my = mouse_pos
        mundo_x = mx + cam_x
        mundo_y = my + cam_y
        col = int(mundo_x // self.tile_w)
        fila = int(mundo_y // self.tile_h)
        tile_rect = pygame.Rect(col * self.tile_w, fila * self.tile_h, self.tile_w, self.tile_h)
        return tile_rect, col, fila


    def es_arable(self, mouse_pos, cam_x, cam_y, jugador_rect, objetos):
        """Verifica si el tile bajo el ratón cumple los requisitos para arar."""
        tile_rect, col, fila = self.get_tile_info(mouse_pos, cam_x, cam_y)


        # Si ya está arada, no se puede
        if (col, fila) in self.terreno_arado:
            return False


        # --- FIX RADIO: Reducido a la mitad (aprox 1.5 tiles) ---
        area_interaccion = jugador_rect.inflate(self.tile_w * 1.5, self.tile_h * 1.5)
        if not tile_rect.colliderect(area_interaccion):
            return False


        # Comprobar obstáculos
        for obj in objetos:
            if tile_rect.colliderect(obj.rect):
                return False


        return True # Sí es arable


    def intentar_arar(self, mouse_pos, cam_x, cam_y, jugador_rect, objetos):
        """Intenta arar si se cumplen las condiciones de es_arable."""
        if self.es_arable(mouse_pos, cam_x, cam_y, jugador_rect, objetos):
            tile_rect, col, fila = self.get_tile_info(mouse_pos, cam_x, cam_y)
            self.terreno_arado[(col, fila)] = random.choice(self.sprites_arados)


    def draw(self, superficie, cam_x, cam_y):
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


    def draw_hover(self, superficie, mouse_pos, cam_x, cam_y, jugador_rect, objetos):
        """Dibuja un cuadro rojo si el tile bajo el cursor es arable."""
        if self.es_arable(mouse_pos, cam_x, cam_y, jugador_rect, objetos):
            tile_rect, _, _ = self.get_tile_info(mouse_pos, cam_x, cam_y)
            # Dibujar cuadro rojo (relativo a la cámara)
            rect_dibujo = pygame.Rect(tile_rect.x - cam_x, tile_rect.y - cam_y, self.tile_w, self.tile_h)
            pygame.draw.rect(superficie, (255, 0, 0), rect_dibujo, 3) # Rojo, ancho 3


class Inventario:
    def __init__(self, imagen):
        ancho_original, alto_original = imagen.get_size()
        ancho_deseado = 600 # Lo hice un poquito más grande para que quepan 7 slots bien
        escala = ancho_deseado / ancho_original
        nuevo_alto = int(alto_original * escala)
       
        self.image = pygame.transform.scale(imagen, (ancho_deseado, nuevo_alto))
       
        rect_final = self.image.get_rect()
        pos_x = ANCHO_PANTALLA // 2 - rect_final.width // 2
        pos_y = ALTO_PANTALLA - rect_final.height - 10
       
        self.rect = self.image.get_rect(topleft=(pos_x, pos_y))
       
        # --- NUEVO: Lista de 7 espacios (0 al 6) ---
        self.slots = [None] * 7


    def set_item(self, indice_slot, sprite):
        """Coloca un sprite en un slot específico (0 a 6)"""
        if 0 <= indice_slot < len(self.slots):
            self.slots[indice_slot] = sprite


    def draw(self, superficie):
        # Dibujar la barra de inventario
        superficie.blit(self.image, self.rect)
       
        # --- Dibujar los ítems ---
        # ¡OJO AQUI! Vas a tener que ajustar estos números probando
        # hasta que la azada quede perfectamente centrada en tu recuadro.
        margen_x_inicial = 20  # Pixeles desde la izquierda del inventario hasta el primer slot
        margen_y_inicial = 55  # Pixeles desde arriba del inventario hacia abajo
        espacio_entre_slots = 82 # Distancia entre un slot y el siguiente
       
        for i, item_sprite in enumerate(self.slots):
            if item_sprite: # Si hay un ítem en este slot
                x = self.rect.x + margen_x_inicial + (i * espacio_entre_slots)
                y = self.rect.y + margen_y_inicial
                superficie.blit(item_sprite, (x, y))


class Obstaculo:
    def __init__(self, x, y, imagen):
        self.image = imagen
        self.rect = self.image.get_rect(topleft=(x, y))
        hitbox_alto = TAM_TILE  
        hitbox_y = self.rect.bottom - hitbox_alto
        self.hitbox = pygame.Rect(self.rect.x, hitbox_y, self.rect.width, hitbox_alto)


    def draw(self, superficie, cam_x, cam_y):
        superficie.blit(self.image, (self.rect.x - cam_x, self.rect.y - cam_y))


class Vaca:
    def __init__(self, x, y, hoja, icono_carrito=None):
        self.frames = [
            extraer_sprite_exacto(hoja, 1, 1, 2, 2, ESCALA_VACA),
            extraer_sprite_exacto(hoja, 3, 1, 2, 2, ESCALA_VACA),
            extraer_sprite_exacto(hoja, 5, 1, 2, 2, ESCALA_VACA),
        ]
        self.timer = 0.0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))

        # Hitbox amplia para impedir que el jugador se suba visualmente encima.
        hb_w = int(self.rect.width * 0.82)
        hb_h = int(self.rect.height * 0.75)
        self.hitbox = pygame.Rect(0, 0, hb_w, hb_h)
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.bottom = self.rect.bottom - int(self.rect.height * 0.06)

        self.icono_carrito = icono_carrito
        self.t_flotacion = 0.0

    def update(self, dt):
        self.timer += VELOCIDAD_ANIMACION_VACA
        idx = int(self.timer) % len(self.frames)
        self.image = self.frames[idx]
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.bottom = self.rect.bottom - int(self.rect.height * 0.06)
        self.t_flotacion += dt * 5.0

    def draw(self, superficie, cam_x, cam_y):
        superficie.blit(self.image, (self.rect.x - cam_x, self.rect.y - cam_y))

        if self.icono_carrito is not None:
            desfase_y = int(math.sin(self.t_flotacion) * 3)
            icono_x = self.rect.centerx - (self.icono_carrito.get_width() // 2)
            icono_y = self.rect.y - self.icono_carrito.get_height() - 1 + desfase_y
            superficie.blit(self.icono_carrito, (icono_x - cam_x, icono_y - cam_y))


class Jugador:
    def __init__(self, x, y, hoja):
        self.direccion = 'abajo'
        self.timer = 0
        self.animaciones = {
            'abajo': [extraer_sprite_exacto(hoja, (i*3)+1, 1, 3, 3, ESCALA) for i in range(4)],
            'arriba': [extraer_sprite_exacto(hoja, (i*3)+1, 4, 3, 3, ESCALA) for i in range(4)],
            'izquierda': [extraer_sprite_exacto(hoja, (i*3)+1, 7, 3, 3, ESCALA) for i in range(4)],
            'derecha': [extraer_sprite_exacto(hoja, (i*3)+1, 10, 3, 3, ESCALA) for i in range(4)],
        }
        self.image = self.animaciones[self.direccion][0]
        self.rect = self.image.get_rect(topleft=(x, y))
       
        hb_w = TAM_TILE          
        hb_h = TAM_TILE // 2    
        self.hitbox = pygame.Rect(0, 0, hb_w, hb_h)
        self.hitbox.center = self.rect.center
        self.fx = float(self.hitbox.x)
        self.fy = float(self.hitbox.y)


    def update(self, muros):
        teclas = pygame.key.get_pressed()
        vx, vy = 0, 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: vx = -VELOCIDAD_JUGADOR; self.direccion = 'izquierda'
        elif teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: vx = VELOCIDAD_JUGADOR; self.direccion = 'derecha'
        if teclas[pygame.K_UP] or teclas[pygame.K_w]: vy = -VELOCIDAD_JUGADOR; self.direccion = 'arriba'
        elif teclas[pygame.K_DOWN] or teclas[pygame.K_s]: vy = VELOCIDAD_JUGADOR; self.direccion = 'abajo'


        if vx != 0 and vy != 0: vx *= 0.707; vy *= 0.707


        if vx != 0 or vy != 0:
            self.timer += VELOCIDAD_ANIMACION
            self.image = self.animaciones[self.direccion][int(self.timer % 4)]
        else:
            self.image = self.animaciones[self.direccion][0]


        # Colisión X
        self.fx += vx
        self.hitbox.x = round(self.fx)
        for muro in muros:
            if self.hitbox.colliderect(muro):
                if vx > 0: self.hitbox.right = muro.left
                elif vx < 0: self.hitbox.left = muro.right
                self.fx = float(self.hitbox.x)


        # Colisión Y
        self.fy += vy
        self.hitbox.y = round(self.fy)
        for muro in muros:
            if self.hitbox.colliderect(muro):
                if vy > 0: self.hitbox.bottom = muro.top
                elif vy < 0: self.hitbox.top = muro.bottom
                self.fy = float(self.hitbox.y)


        # Posicionamiento visual
        self.rect.center = self.hitbox.center


    def draw(self, superficie, cam_x, cam_y):
        superficie.blit(self.image, (self.rect.x - cam_x, self.rect.y - cam_y))


# ==========================================
# FUNCIÓN PRINCIPAL
# ==========================================
def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
    # --- TÍTULO ACTUALIZADO ---
    pygame.display.set_caption("Moonvale - Inventario y Arado")
    reloj = pygame.time.Clock()
    dia_actual = 1
    transicion_dia_restante = 0.0
    tienda_abierta = False
    modo_tienda = "compra"
    monedas = 120
    inventario_semillas = {"semilla1": 0, "semilla2": 0}
    inventario_cosechas = {"planta1": 0, "planta2": 0}


    base = "Sprout Lands - Sprites - Basic pack"
    try:
        hoja_pasto = pygame.image.load(asset_path(base, "Tilesets", "Grass.png")).convert_alpha()
        hoja_cercas = pygame.image.load(asset_path(base, "Tilesets", "Fences.png")).convert_alpha()
        hoja_pj = pygame.image.load(asset_path(base, "Characters", "Basic Charakter Spritesheet.png")).convert_alpha()
        hoja_vacas = pygame.image.load(asset_path(base, "Characters", "Free Cow Sprites.png")).convert_alpha()
        hoja_iconos_blancos = pygame.image.load(
            asset_path("Sprout Lands - UI Pack - Basic pack", "Sprite sheets", "Icons", "white icons.png")
        ).convert_alpha()
        hoja_plantas = pygame.image.load(asset_path(base, "Objects", "Basic_Plants.png")).convert_alpha()
        ui_menu_tienda = pygame.image.load(
            asset_path("Sprout Lands - UI Pack - Basic pack", "Sprite sheets", "Setting menu.png")
        ).convert_alpha()
        ui_boton = pygame.image.load(
            asset_path("Sprout Lands - UI Pack - Basic pack", "Sprite sheets", "buttons", "Square Buttons 26x19.png")
        ).convert_alpha()
        hoja_objs = pygame.image.load(asset_path(base, "Objects", "Basic Grass Biom things 1.png")).convert_alpha()
        hoja_tierra = pygame.image.load(asset_path(base, "Tilesets", "Tilled Dirt.png")).convert_alpha()
        casa_superior = pygame.image.load(asset_path("House4.png")).convert_alpha()
        casa_superior = pygame.transform.scale(
            casa_superior,
            (
                int(casa_superior.get_width() * ESCALA_CASA),
                int(casa_superior.get_height() * ESCALA_CASA),
            ),
        )

        # Fuente personalizada para los textos del juego
        ruta_fuente = asset_path(
            "Sprout Lands - UI Pack - Basic pack",
            "fonts",
            "pixelFont-7-8x14-sproutLands.ttf",
        )
        fuente_dia = pygame.font.Font(ruta_fuente, 44)
        fuente_transicion = pygame.font.Font(ruta_fuente, 56)
        fuente_tienda_titulo = pygame.font.Font(ruta_fuente, 36)
        fuente_tienda = pygame.font.Font(ruta_fuente, 24)
       
        # --- CARGAMOS LA TEXTURA DEL INVENTARIO ---
        img_inventario = pygame.image.load(asset_path(base, "Objects", "inventory_Light_example_with_slots.png")).convert_alpha()
        hoja_herramientas = pygame.image.load(asset_path(base, "Objects", "Basic tools and meterials.png")).convert_alpha()
    except Exception as e:
        print(f"Error cargando archivos: {e}")
        return


    # Extraer sprites de tierra arada
    coords_tierra = [(1,1), (2,1), (3,1), (1,2), (2,2), (3,2)]
    sprites_tierra = [extraer_sprite_exacto(hoja_tierra, c, f, 1, 1, ESCALA) for c, f in coords_tierra]


    # Sprites corregidos
    sprites = {
        'A': extraer_sprite_exacto(hoja_objs, 2, 1, 2, 2, ESCALA), # Árbol verde        
        'B': extraer_sprite_exacto(hoja_objs, 4, 1, 2, 2, ESCALA), # Árbol corazón      
        'C': extraer_sprite_exacto(hoja_objs, 2, 3, 2, 2, ESCALA), # Arbusto            
        'D': extraer_sprite_exacto(hoja_objs, 9, 3, 1, 2, ESCALA), # Girasol            
        'E': extraer_sprite_exacto(hoja_objs, 6, 4, 1, 1, ESCALA), # Seta rosa/roja    
        'F': extraer_sprite_exacto(hoja_objs, 7, 4, 1, 1, ESCALA), # Seta marrón        
        'G': extraer_sprite_exacto(hoja_objs, 7, 2, 1, 1, ESCALA), # Piedra pequeña    
        'H': extraer_sprite_exacto(hoja_objs, 8, 2, 1, 1, ESCALA), # Piedra mediana    
        'I': extraer_sprite_exacto(hoja_objs, 9, 2, 1, 1, ESCALA), # Piedra grande      
        'J': extraer_sprite_exacto(hoja_objs, 7, 3, 1, 1, ESCALA), # Flor amarilla      
        'K': extraer_sprite_exacto(hoja_objs, 9, 5, 1, 1, ESCALA), # Mata verde        
    }


    # Layout manual del mapa
    layout = [
        ('A',  0,  0), ('B',  2,  0), ('A',  4,  0), ('C',  6,  0), ('B',  8,  0),
        ('C',  0,  2), ('D',  3,  2), ('A',  5,  2), ('D',  7,  2),
        ('C', 20,  0), ('A', 22,  0), ('B', 24,  0), ('C', 26,  0), ('A', 28,  0),
        ('D', 20,  2), ('A', 22,  2), ('C', 24,  2), ('B', 26,  2), ('D', 28,  2),
        ('A',  0,  4), ('E',  3,  4), ('C',  5,  4),
        ('J',  1,  6), ('B',  3,  6), ('G',  5,  6),
        ('H',  0,  8), ('A',  2,  8), ('I',  5,  8),
        ('K',  0, 10), ('C',  2, 10), ('E',  5, 10),
        ('A',  0, 12), ('F',  3, 12), ('D',  4, 12),
        ('J',  1, 14), ('B',  3, 14), ('H',  5, 14),
        ('C',  0, 16), ('K',  2, 16), ('I',  5, 16),
        ('D',  0, 18), ('E',  3, 18), ('F',  6, 18),
        ('A',  0, 20), ('G',  3, 20), ('B',  5, 20),
        ('J',  1, 22), ('C',  3, 22), ('F',  6, 22),
        ('A',  0, 24), ('K',  2, 24), ('H',  5, 24),
        ('D',  0, 26), ('E',  3, 26),
        ('C',  0, 28), ('G',  3, 28), ('I',  5, 28),
        ('A', 24,  4), ('E', 27,  4), ('D', 29,  4),
        ('B', 24,  6), ('J', 27,  6), ('G', 29,  6),
        ('D', 24,  8), ('A', 26,  8), ('I', 29,  8),
        ('E', 24, 10), ('K', 27, 10), ('C', 29, 10),
        ('A', 24, 12), ('G', 27, 12), ('D', 29, 12),
        ('J', 24, 14), ('C', 26, 14), ('H', 29, 14),
        ('B', 24, 16), ('K', 27, 16), ('I', 29, 16),
        ('F', 24, 18), ('D', 26, 18), ('E', 29, 18),
        ('A', 24, 20), ('E', 26, 20), ('B', 29, 20),
        ('J', 25, 22), ('C', 27, 22), ('G', 29, 22),
        ('D', 24, 24), ('A', 26, 24), ('K', 29, 24),
        ('E', 24, 26), ('H', 27, 26),
        ('A', 24, 28), ('F', 27, 28), ('D', 29, 28),
        ('A',  2, 29), ('D',  5, 29), ('E',  8, 29),
        ('F', 10, 29), ('G', 11, 29), ('F', 13, 29),
        ('H', 15, 29), ('G', 16, 29), ('E', 18, 29),
        ('D', 20, 29), ('B', 26, 29),
        ('H',  7,  7), ('F',  7, 13), ('G',  7, 19), ('I',  7, 25),
        ('H', 22,  7), ('F', 22, 13), ('G', 22, 19), ('I', 22, 25),
    ]


    tile_pasto = extraer_sprite_exacto(hoja_pasto, 1, 6, 1, 1, ESCALA)

    # Fences.png viene como atlas 4x2; usamos la fila 2 para cercas horizontales conectadas
    cerca_w = hoja_cercas.get_width() // 4
    cerca_h = hoja_cercas.get_height() // 2

    def extraer_cerca(columna, fila):
        rect = pygame.Rect((columna - 1) * cerca_w, (fila - 1) * cerca_h, cerca_w, cerca_h)
        s = pygame.Surface((cerca_w, cerca_h), pygame.SRCALPHA)
        s.blit(hoja_cercas, (0, 0), rect)

        # Cada tile trae dos hileras; usamos solo la superior para una sola linea visual.
        mitad_h = cerca_h // 2
        una_linea = pygame.Surface((cerca_w, mitad_h), pygame.SRCALPHA)
        una_linea.blit(s, (0, 0), pygame.Rect(0, 0, cerca_w, mitad_h))
        return pygame.transform.scale(una_linea, (TAM_TILE, int(TAM_TILE * 1)))

    sprite_cerca_izq = extraer_cerca(2, 2)
    sprite_cerca_mid = extraer_cerca(3, 2)
    sprite_cerca_der = extraer_cerca(4, 2)
   
    sprite_azada = extraer_sprite_exacto(hoja_herramientas, 3, 1, 1, 1, ESCALA)
    # --- NUEVO: Extraer Hacha y Regadera ---
    # El hacha está en la Columna 2, Fila 1
    sprite_hacha = extraer_sprite_exacto(hoja_herramientas, 2, 1, 1, 1, ESCALA)
   
    # La regadera está en la Columna 1, Fila 1
    sprite_regadera = extraer_sprite_exacto(hoja_herramientas, 1, 1, 1, 1, ESCALA)

    # Icono de carrito: recorte exacto para evitar que se corte al usar una grilla fija.
    # Coordenadas obtenidas por detección de pixeles no transparentes en white icons.png.
    icono_rect = pygame.Rect(34, 19, 13, 9)
    icono_carrito = pygame.Surface((icono_rect.width, icono_rect.height), pygame.SRCALPHA)
    icono_carrito.blit(hoja_iconos_blancos, (0, 0), icono_rect)
    icono_carrito = pygame.transform.scale(
        icono_carrito,
        (icono_rect.width * ESCALA_ICONO_CARRITO, icono_rect.height * ESCALA_ICONO_CARRITO),
    )

    # Semillas vendibles en tienda: los dos sobres (columna 1, filas 1 y 2)
    icono_semilla_1 = extraer_sprite_exacto(hoja_plantas, 1, 1, 1, 1, ESCALA_SEMILLA_MENU)
    icono_semilla_2 = extraer_sprite_exacto(hoja_plantas, 1, 2, 1, 1, ESCALA_SEMILLA_MENU)
    icono_planta_1 = extraer_sprite_exacto(hoja_plantas, 6, 1, 1, 1, ESCALA_SEMILLA_MENU)
    icono_planta_2 = extraer_sprite_exacto(hoja_plantas, 6, 2, 1, 1, ESCALA_SEMILLA_MENU)

    # Versiones pequenas para el panel derecho (venta)
    icono_semilla_1_venta = pygame.transform.scale(icono_semilla_1, (TAM_ICONO_VENTA, TAM_ICONO_VENTA))
    icono_semilla_2_venta = pygame.transform.scale(icono_semilla_2, (TAM_ICONO_VENTA, TAM_ICONO_VENTA))
    icono_planta_1_venta = pygame.transform.scale(icono_planta_1, (TAM_ICONO_VENTA, TAM_ICONO_VENTA))
    icono_planta_2_venta = pygame.transform.scale(icono_planta_2, (TAM_ICONO_VENTA, TAM_ICONO_VENTA))

    # Escalado de UI de tienda
    ui_menu_tienda = pygame.transform.scale(ui_menu_tienda, (660, 372))
    ui_boton = pygame.transform.scale(ui_boton.subsurface(pygame.Rect(0, 0, 26, 19)), (98, 38))

    # Inicializar instancias
    granja = Granja(tile_pasto, sprites_tierra)
    jugador = Jugador(ANCHO_MAPA // 2, ALTO_MAPA // 2, hoja_pj)
    vacas = []
    camara = Camara(ANCHO_PANTALLA, ALTO_PANTALLA)
   
    inventario = Inventario(img_inventario)
   
    inventario.set_item(0, sprite_azada)    # Slot 1: Azada
    inventario.set_item(1, sprite_hacha)    # Slot 2: Hacha
    inventario.set_item(2, sprite_regadera) # Slot 3: Regadera


    objetos = []
    for (tipo, col, fila) in layout:
        img = sprites[tipo]
        ox = col * TAM_TILE
        oy = fila * TAM_TILE
        objetos.append(Obstaculo(ox, oy, img))

    # Casa principal colocada en la parte superior y centrada del mapa
    casa_x = (ANCHO_MAPA // 2) - (casa_superior.get_width() // 2)
    casa_y = 0
    objetos.append(Obstaculo(casa_x, casa_y, casa_superior))

    # Cercas horizontales a izquierda y derecha de la casa
    cerca_y = casa_y + int(casa_superior.get_height() * 0.78)
    tramos_por_lado = 6

    # Lado izquierdo: extremo cercano a casa, medios, extremo exterior
    for i in range(tramos_por_lado):
        x_izq = casa_x - ((i + 1) * TAM_TILE)
        if i == 0:
            sprite = sprite_cerca_der
        elif i == tramos_por_lado - 1:
            sprite = sprite_cerca_izq
        else:
            sprite = sprite_cerca_mid
        objetos.append(Obstaculo(x_izq, cerca_y + (TAM_TILE // 8), sprite))

    # Lado derecho: extremo cercano a casa, medios, extremo exterior
    for i in range(tramos_por_lado):
        x_der = casa_x + casa_superior.get_width() + (i * TAM_TILE)
        if i == 0:
            sprite = sprite_cerca_izq
        elif i == tramos_por_lado - 1:
            sprite = sprite_cerca_der
        else:
            sprite = sprite_cerca_mid
        objetos.append(Obstaculo(x_der, cerca_y + (TAM_TILE // 8), sprite))

    # Colocar vaca al final de la cerca izquierda (referencia de la imagen)
    x_extremo_cerca_izq = casa_x - (tramos_por_lado * TAM_TILE)
    y_linea_cerca = cerca_y + (TAM_TILE // 8)
    vaca_preview = extraer_sprite_exacto(hoja_vacas, 1, 1, 2, 2, ESCALA_VACA)
    vaca_x = x_extremo_cerca_izq + (TAM_TILE // 2) - (vaca_preview.get_width() // 2)
    vaca_y = y_linea_cerca + TAM_TILE - (vaca_preview.get_height() // 3)
    vacas = [Vaca(vaca_x, vaca_y, hoja_vacas, icono_carrito)]
    panel_tienda_rect = ui_menu_tienda.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2))
    layout_tienda = construir_layout_tienda(panel_tienda_rect)

    # Zona de interacción de la puerta (centro inferior de la casa)
    puerta_w = TAM_TILE
    puerta_h = int(TAM_TILE * 1.3)
    puerta_x = casa_x + (casa_superior.get_width() // 2) - (puerta_w // 2)
    puerta_y = casa_y + int(casa_superior.get_height() * 0.66)
    puerta_rect = pygame.Rect(puerta_x, puerta_y, puerta_w, puerta_h)
    # Zona ajustada: un poco más baja y amplia para facilitar interacción enfrente.
    zona_interaccion_puerta = puerta_rect.inflate(int(TAM_TILE * 0.35), int(TAM_TILE * 0.5))
    zona_interaccion_puerta.y += int(TAM_TILE * 0.5)


    while True:
        dt = reloj.tick(FPS) / 1000.0
        if transicion_dia_restante > 0:
            transicion_dia_restante = max(0.0, transicion_dia_restante - dt)

        # --- OBTENER POSICIÓN RATÓN EN CADA FRAME ---
        mouse_pos = pygame.mouse.get_pos()


        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE and tienda_abierta:
                tienda_abierta = False

            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_e:
                cerca_de_vaca = any(jugador.hitbox.colliderect(vaca.hitbox.inflate(70, 70)) for vaca in vacas)
                if tienda_abierta:
                    tienda_abierta = False
                elif cerca_de_vaca and transicion_dia_restante == 0:
                    tienda_abierta = True
                elif transicion_dia_restante == 0 and not tienda_abierta and jugador.hitbox.colliderect(zona_interaccion_puerta):
                    dia_actual += 1
                    transicion_dia_restante = DURACION_TRANSICION_DIA
           
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
                        if monedas >= PRECIO_COMPRA_SEMILLA_1:
                            monedas -= PRECIO_COMPRA_SEMILLA_1
                            inventario_semillas["semilla1"] += 1
                    elif modo_tienda == "compra" and layout_tienda["accion2"].collidepoint(mpos):
                        if monedas >= PRECIO_COMPRA_SEMILLA_2:
                            monedas -= PRECIO_COMPRA_SEMILLA_2
                            inventario_semillas["semilla2"] += 1
                    elif modo_tienda == "venta" and layout_tienda["venta_s1"].collidepoint(mpos):
                        if inventario_semillas["semilla1"] > 0:
                            inventario_semillas["semilla1"] -= 1
                            monedas += PRECIO_VENTA_SEMILLA_1
                    elif modo_tienda == "venta" and layout_tienda["venta_p1"].collidepoint(mpos):
                        if inventario_cosechas["planta1"] > 0:
                            inventario_cosechas["planta1"] -= 1
                            monedas += PRECIO_VENTA_PLANTA_1
                    elif modo_tienda == "venta" and layout_tienda["venta_s2"].collidepoint(mpos):
                        if inventario_semillas["semilla2"] > 0:
                            inventario_semillas["semilla2"] -= 1
                            monedas += PRECIO_VENTA_SEMILLA_2
                    elif modo_tienda == "venta" and layout_tienda["venta_p2"].collidepoint(mpos):
                        if inventario_cosechas["planta2"] > 0:
                            inventario_cosechas["planta2"] -= 1
                            monedas += PRECIO_VENTA_PLANTA_2

                if ev.button == 1 and transicion_dia_restante == 0 and not tienda_abierta:
                    granja.intentar_arar(mouse_pos, camara.x, camara.y, jugador.rect, objetos)


        for vaca in vacas:
            vaca.update(dt)

        muros = [o.hitbox for o in objetos] + [vaca.hitbox for vaca in vacas]
        if not tienda_abierta:
            jugador.update(muros)
            camara.actualizar(jugador.rect)


        pantalla.fill((0, 0, 0))
       
        # 1. Dibujar el mundo base (Pasto y terreno arado)
        granja.draw(pantalla, camara.x, camara.y)
       
        # --- 2. DIBUJAR HOVER ROJO (Después del suelo, antes de los objetos) ---
        granja.draw_hover(pantalla, mouse_pos, camara.x, camara.y, jugador.rect, objetos)


        # 3. Y-Sorting (Objetos y jugador con profundidad)
        entidades = objetos + vacas + [jugador]
        entidades.sort(key=lambda e: e.rect.bottom)


        for e in entidades:
            e.draw(pantalla, camara.x, camara.y)

        if not tienda_abierta and any(jugador.hitbox.colliderect(vaca.hitbox.inflate(70, 70)) for vaca in vacas):
            dibujar_texto_con_borde(
                pantalla,
                fuente_tienda,
                "Presiona E para tienda",
                (ANCHO_PANTALLA // 2 - 128, 76),
                (255, 255, 255),
                (30, 20, 20),
            )

        if (
            not tienda_abierta
            and transicion_dia_restante == 0
            and jugador.hitbox.colliderect(zona_interaccion_puerta)
        ):
            dibujar_texto_con_borde(
                pantalla,
                fuente_tienda,
                "Presiona E para dormir",
                (ANCHO_PANTALLA // 2 - 128, 108),
                (255, 255, 255),
                (30, 20, 20),
            )

        # Indicador de día en la esquina superior izquierda
        dibujar_texto_con_borde(
            pantalla,
            fuente_dia,
            f"Dia {dia_actual}",
            (16, 14),
            (0, 0, 0),
            (255, 255, 255),
        )

        if transicion_dia_restante > 0:
            pantalla.fill((0, 0, 0))
            dibujar_texto_con_borde(
                pantalla,
                fuente_transicion,
                f"Dia {dia_actual}",
                (ANCHO_PANTALLA // 2 - 70, ALTO_PANTALLA // 2 - 36),
                (255, 255, 255),
                (0, 0, 0),
            )
            dibujar_texto_con_borde(
                pantalla,
                fuente_dia,
                "Cambiando de dia...",
                (ANCHO_PANTALLA // 2 - 150, ALTO_PANTALLA // 2 + 16),
                (255, 255, 255),
                (0, 0, 0),
            )

        if tienda_abierta and transicion_dia_restante == 0:
            draw_tienda(
                pantalla,
                ui_menu_tienda,
                ui_boton,
                fuente_tienda_titulo,
                fuente_tienda,
                layout_tienda,
                modo_tienda,
                monedas,
                inventario_semillas,
                inventario_cosechas,
                icono_semilla_1,
                icono_semilla_2,
                icono_planta_1,
                icono_planta_2,
                icono_semilla_1_venta,
                icono_semilla_2_venta,
                icono_planta_1_venta,
                icono_planta_2_venta,
            )
           
        # --- 4. DIBUJAR UI (Inventario estático, siempre arriba de todo) ---
        if transicion_dia_restante == 0 and not tienda_abierta:
            inventario.draw(pantalla)


        pygame.display.flip()


if __name__ == "__main__":
    main()
