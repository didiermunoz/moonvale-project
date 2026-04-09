import pygame
import sys
import os

# ==========================================
# 0. CONFIGURACIÓN Y CONSTANTES
# ==========================================
os.environ['SDL_VIDEO_CENTERED'] = '1'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")
if not os.path.isdir(ASSETS_DIR):
    # Fallback for projects that use lowercase folder names.
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")


def asset_path(filename):
    return os.path.join(ASSETS_DIR, filename)

ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600
FPS = 60
ALTO_UI = 100
ALTO_JUEGO = ALTO_PANTALLA - ALTO_UI

# Zoom de cámara: mayor valor = más cerca del jugador (se ve menos mapa).
CAMARA_ZOOM = 1.35
CAMARA_VISTA_ANCHO = int(ANCHO_PANTALLA / CAMARA_ZOOM)
CAMARA_VISTA_ALTO = int(ALTO_JUEGO / CAMARA_ZOOM)

PASTEL_SKY_BLUE = (173, 216, 230) 
DARK_GRAY_UI = (45, 45, 45)

# --- CONFIGURACIÓN JUGADOR ---
SPRITE_ANCHO_BASE = 64  
SPRITE_ALTO_BASE = 64
# ¡AQUÍ ESTÁ LA MAGIA! Lo cambiamos a 2. Tu personaje ahora será del doble de tamaño visualmente, 
# pero el recorte de 64x64 original se mantiene intacto.
FACTOR_ESCALA_JUGADOR = 2 
SPRITE_ANCHO_JUEGO = SPRITE_ANCHO_BASE * FACTOR_ESCALA_JUGADOR
SPRITE_ALTO_JUEGO = SPRITE_ALTO_BASE * FACTOR_ESCALA_JUGADOR

VELOCIDAD_JUGADOR = 4
VELOCIDAD_ANIMACION_JUGADOR = 0.15

DIR_ABAJO = 0
DIR_IZQUIERDA = 1
DIR_DERECHA = 2
DIR_ARRIBA = 3

HERRAMIENTA_HACHA = "hacha"
HERRAMIENTA_AZADA = "azada"
HERRAMIENTA_REGADERA = "regadera"

# --- CONFIGURACIÓN MAPA ---
TILE_ANCHO = 64
TILE_ALTO = 64
MAPA_ANCHO = 20
MAPA_ALTO = 20

# --- CONFIGURACIÓN ÁRBOL ---
FRAME_ARBOL_ANCHO = 64  
FRAMES_ANIMACION_ARBOL = 4      # Cuántos cuadros queremos que se muevan en el juego
TOTAL_FILAS_SPRITESHEET = 13    # <-- ¡EL DATO CLAVE! La imagen tiene 13 árboles hacia abajo
VELOCIDAD_ANIMACION_ARBOL = 0.05

# ==========================================
# 1. FUNCIONES HELPER DE RECORTE
# ==========================================
def obtener_frames(hoja_sprites, fila, total_frames, ancho_frame, alto_frame):
    frames = []
    for col in range(total_frames):
        superficie = pygame.Surface((ancho_frame, alto_frame), pygame.SRCALPHA)
        x = col * ancho_frame
        y = fila * alto_frame
        superficie.blit(hoja_sprites, (0, 0), (x, y, ancho_frame, alto_frame))
        # Escala al jugador al doble de tamaño
        imagen_final = pygame.transform.scale(superficie, (SPRITE_ANCHO_JUEGO, SPRITE_ALTO_JUEGO))
        frames.append(imagen_final)
    return frames

def obtener_frames_columna_inteligente(hoja_sprites, inicio_x, frames_a_extraer, total_filas, ancho_frame):
    frames = []
    alto_frame_exacto = hoja_sprites.get_height() // total_filas
    
    for fila in range(frames_a_extraer):
        superficie = pygame.Surface((ancho_frame, alto_frame_exacto), pygame.SRCALPHA)
        y = fila * alto_frame_exacto
        superficie.blit(hoja_sprites, (0, 0), (inicio_x, y, ancho_frame, alto_frame_exacto))
        frames.append(superficie)
    return frames, alto_frame_exacto

def obtiene_tile(hoja_tiles, col, fila, ancho_tile, alto_tile):
    superficie = pygame.Surface((ancho_tile, alto_tile), pygame.SRCALPHA)
    x = col * ancho_tile
    y = fila * alto_tile
    superficie.blit(hoja_tiles, (0, 0), (x, y, ancho_tile, alto_tile))
    return superficie

# ==========================================
# 2. JERARQUÍA DE INVENTARIO Y RECURSIVIDAD
# ==========================================
class Item:
    def __init__(self, nombre, valor):
        self.__nombre = nombre 
        self.__valor = valor
    def get_nombre(self): return self.__nombre
    def get_valor(self): return self.__valor

class Semilla(Item):
    def __init__(self, nombre, valor, tiempo_crecimiento):
        super().__init__(nombre, valor)
        self.tiempo_crecimiento = tiempo_crecimiento

class Parcela:
    def __init__(self, color_base, color_regado):
        self.labrada = False
        self.regada = False

    def arar(self):
        self.labrada = True

    def regar(self):
        self.regada = True

class Granja:
    def __init__(self, ancho, alto, hoja_tiles):
        self.ancho = ancho
        self.alto = alto
        self.ancho_px = ancho * TILE_ANCHO
        self.alto_px = alto * TILE_ALTO
        
        self.tile_base = obtiene_tile(hoja_tiles, 0, 0, TILE_ANCHO, TILE_ALTO)
        self.tile_regado = obtiene_tile(hoja_tiles, 1, 0, TILE_ANCHO, TILE_ALTO)
        self.tile_labrado = self.tile_base.copy()
        tinte_labrado = pygame.Surface((TILE_ANCHO, TILE_ALTO), pygame.SRCALPHA)
        tinte_labrado.fill((148, 99, 58, 120))
        self.tile_labrado.blit(tinte_labrado, (0, 0))
        self.tile_regado_labrado = self.tile_regado.copy()
        tinte_regado_labrado = pygame.Surface((TILE_ANCHO, TILE_ALTO), pygame.SRCALPHA)
        tinte_regado_labrado.fill((40, 28, 20, 95))
        self.tile_regado_labrado.blit(tinte_regado_labrado, (0, 0))

        self.matriz = [[Parcela(PASTEL_SKY_BLUE,DARK_GRAY_UI) for _ in range(alto)] for _ in range(ancho)]

    def posicion_a_parcela(self, mundo_x, mundo_y):
        parcela_x = int(mundo_x // TILE_ANCHO)
        parcela_y = int(mundo_y // TILE_ALTO)
        if parcela_x < 0 or parcela_x >= self.ancho or parcela_y < 0 or parcela_y >= self.alto:
            return None
        return parcela_x, parcela_y

    def arar_parcela(self, parcela_x, parcela_y):
        if parcela_x < 0 or parcela_x >= self.ancho or parcela_y < 0 or parcela_y >= self.alto:
            return False

        parcela = self.matriz[parcela_x][parcela_y]
        if parcela.labrada:
            return False

        parcela.arar()
        parcela.regada = False
        return True

    def regar_parcela(self, parcela_x, parcela_y):
        if parcela_x < 0 or parcela_x >= self.ancho or parcela_y < 0 or parcela_y >= self.alto:
            return False

        parcela = self.matriz[parcela_x][parcela_y]
        if not parcela.labrada or parcela.regada:
            return False

        parcela.regar()
        return True
        
    def regar_en_cadena(self, x, y, nivel_carga):
        if x < 0 or x >= self.ancho or y < 0 or y >= self.alto or nivel_carga <= 0: return
        parcela_actual = self.matriz[x][y]
        if parcela_actual.regada: return

        parcela_actual.regar()
        print(f"Recursión: Regada Parcela ({x}, {y}). Energía: {nivel_carga}")

        self.regar_en_cadena(x + 1, y, nivel_carga - 1)
        self.regar_en_cadena(x - 1, y, nivel_carga - 1)
        self.regar_en_cadena(x, y + 1, nivel_carga - 1)
        self.regar_en_cadena(x, y - 1, nivel_carga - 1)

    def draw(self, superficie, cam_x, cam_y):
        # 1) Terreno base repetido para que nunca se vea fondo vacío al mover la cámara.
        start_col = (cam_x // TILE_ANCHO) - 1
        end_col = ((cam_x + CAMARA_VISTA_ANCHO) // TILE_ANCHO) + 1
        start_row = (cam_y // TILE_ALTO) - 1
        end_row = ((cam_y + CAMARA_VISTA_ALTO) // TILE_ALTO) + 1

        for col in range(start_col, end_col + 1):
            for fila in range(start_row, end_row + 1):
                draw_x = (col * TILE_ANCHO) - cam_x
                draw_y = (fila * TILE_ALTO) - cam_y
                superficie.blit(self.tile_base, (draw_x, draw_y))

        # 2) Parcelas regadas: solo dentro de la granja lógica.
        for x in range(self.ancho):
            for y in range(self.alto):
                parcela = self.matriz[x][y]

                if not parcela.labrada and not parcela.regada:
                    continue

                draw_x = x * TILE_ANCHO - cam_x
                draw_y = y * TILE_ALTO - cam_y

                if draw_x <= -TILE_ANCHO or draw_x >= CAMARA_VISTA_ANCHO:
                    continue
                if draw_y <= -TILE_ALTO or draw_y >= CAMARA_VISTA_ALTO:
                    continue

                if parcela.regada:
                    if parcela.labrada:
                        superficie.blit(self.tile_regado_labrado, (draw_x, draw_y))
                    else:
                        superficie.blit(self.tile_regado, (draw_x, draw_y))
                elif parcela.labrada:
                    superficie.blit(self.tile_labrado, (draw_x, draw_y))


class Camara:
    def __init__(self, ancho_mundo, alto_mundo):
        self.ancho_mundo = max(ancho_mundo, CAMARA_VISTA_ANCHO)
        self.alto_mundo = max(alto_mundo, CAMARA_VISTA_ALTO)
        self.x = 0
        self.y = 0

    def update(self, objetivo_x, objetivo_y):
        centro_x = objetivo_x + (SPRITE_ANCHO_JUEGO / 2)
        centro_y = objetivo_y + (SPRITE_ALTO_JUEGO / 2)

        self.x = int(centro_x - (CAMARA_VISTA_ANCHO / 2))
        self.y = int(centro_y - (CAMARA_VISTA_ALTO / 2))

        # Limita la cámara a los bordes del mundo jugable.
        self.x = max(0, min(self.x, self.ancho_mundo - CAMARA_VISTA_ANCHO))
        self.y = max(0, min(self.y, self.alto_mundo - CAMARA_VISTA_ALTO))

# ==========================================
# 3. CLASES DE DECORACIÓN 
# ==========================================
class Casa:
    def __init__(self, ruta_imagen, x, y):
        self.x = x
        self.y = y
        try:
            self.image = pygame.image.load(ruta_imagen).convert_alpha()
        except FileNotFoundError:
            print(f"ERROR: No se encontró '{ruta_imagen}'.")
            sys.exit(1)
        
        self.y_bottom = y + self.image.get_height()

    def draw(self, superficie, cam_x, cam_y):
        superficie.blit(self.image, (self.x - cam_x, self.y - cam_y))

    def get_collision_rect(self):
        # Solo la base de la casa bloquea al jugador.
        hit_w = int(self.image.get_width() * 0.62)
        hit_h = int(self.image.get_height() * 0.30)
        hit_x = self.x + (self.image.get_width() - hit_w) // 2
        hit_y = self.y + self.image.get_height() - hit_h
        return pygame.Rect(hit_x, hit_y, hit_w, hit_h)

class Arbol:
    # Añadimos el parámetro opcional al final
    def __init__(self, hoja_sprites, x, y, tipo_arbol_columna=0, ancho_override=None):
        self.x = x
        self.y = y
        
        # Si le pasaste un ancho personalizado, lo usa. Si no, usa el de 64 por defecto.
        ancho = ancho_override if ancho_override else FRAME_ARBOL_ANCHO
        
        # Su posición de inicio siempre será su columna * 64
        inicio_x = tipo_arbol_columna * FRAME_ARBOL_ANCHO 
        
        self.frames, altura_exacta = obtener_frames_columna_inteligente(
            hoja_sprites, 
            inicio_x, 
            FRAMES_ANIMACION_ARBOL, 
            TOTAL_FILAS_SPRITESHEET, 
            ancho  # Le pasamos el ancho final
        )
        
        self.frame_index = 0
        self.animation_timer = 0
        self.image = self.frames[self.frame_index]
        self.y_bottom = y + altura_exacta

    def update(self):
        self.animation_timer += VELOCIDAD_ANIMACION_ARBOL
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.frame_index = 0
            self.image = self.frames[self.frame_index]

    def draw(self, superficie, cam_x, cam_y):
        superficie.blit(self.image, (self.x - cam_x, self.y - cam_y))

    def get_collision_rect(self):
        # El tronco/base del árbol es la zona sólida.
        hit_w = int(self.image.get_width() * 0.45)
        hit_h = int(self.image.get_height() * 0.22)
        hit_x = self.x + (self.image.get_width() - hit_w) // 2
        hit_y = self.y + self.image.get_height() - hit_h
        return pygame.Rect(hit_x, hit_y, hit_w, hit_h)

    def update(self):
        self.animation_timer += VELOCIDAD_ANIMACION_ARBOL
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.frame_index = 0
            self.image = self.frames[self.frame_index]

    def draw(self, superficie, cam_x, cam_y):
        superficie.blit(self.image, (self.x - cam_x, self.y - cam_y))

# ==========================================
# 4. CLASE JUGADOR 
# ==========================================
class Jugador:
    def __init__(self, x_inicio, y_inicio, ancho_mundo, alto_mundo):
        self.x = x_inicio
        self.y = y_inicio
        self.ancho_mundo = ancho_mundo
        self.alto_mundo = alto_mundo
        self.vx = 0
        self.vy = 0
        
        try:
            hoja_idle = pygame.image.load(asset_path("idle.png")).convert_alpha()
            hoja_walk = pygame.image.load(asset_path("walking.png")).convert_alpha()
        except FileNotFoundError:
            print("ERROR: Faltan 'idle.png' o 'walking.png' en la carpeta Assets.")
            sys.exit(1)

        COLUMNAS_IDLE = 4 
        COLUMNAS_WALK = 6 

        self.animations = {
            'idle_down':  obtener_frames(hoja_idle, DIR_ABAJO, COLUMNAS_IDLE, SPRITE_ANCHO_BASE, SPRITE_ALTO_BASE),
            'idle_up':    obtener_frames(hoja_idle, DIR_ARRIBA, COLUMNAS_IDLE, SPRITE_ANCHO_BASE, SPRITE_ALTO_BASE),
            'idle_left':  obtener_frames(hoja_idle, DIR_IZQUIERDA, COLUMNAS_IDLE, SPRITE_ANCHO_BASE, SPRITE_ALTO_BASE),
            'idle_right': obtener_frames(hoja_idle, DIR_DERECHA, COLUMNAS_IDLE, SPRITE_ANCHO_BASE, SPRITE_ALTO_BASE),
            
            'walk_down':  obtener_frames(hoja_walk, DIR_ABAJO, COLUMNAS_WALK, SPRITE_ANCHO_BASE, SPRITE_ALTO_BASE),
            'walk_up':    obtener_frames(hoja_walk, DIR_ARRIBA, COLUMNAS_WALK, SPRITE_ANCHO_BASE, SPRITE_ALTO_BASE),
            'walk_left':  obtener_frames(hoja_walk, DIR_IZQUIERDA, COLUMNAS_WALK, SPRITE_ANCHO_BASE, SPRITE_ALTO_BASE),
            'walk_right': obtener_frames(hoja_walk, DIR_DERECHA, COLUMNAS_WALK, SPRITE_ANCHO_BASE, SPRITE_ALTO_BASE)
        }

        self.state = 'idle'
        self.direction = 'down'
        self.frame_index = 0
        self.animation_timer = 0
        
        self.image = self.animations[f'{self.state}_{self.direction}'][self.frame_index]
        self.rect = self.image.get_rect()
        self.y_bottom = y_inicio + SPRITE_ALTO_JUEGO

    def handle_input(self):
        self.vx, self.vy = 0, 0
        self.state = 'idle'
        teclas = pygame.key.get_pressed()
        
        if teclas[pygame.K_w]:
            self.vy = -VELOCIDAD_JUGADOR
            self.direction = 'up'
            self.state = 'walk'
        elif teclas[pygame.K_s]:
            self.vy = VELOCIDAD_JUGADOR
            self.direction = 'down'
            self.state = 'walk'
            
        if teclas[pygame.K_a]:
            self.vx = -VELOCIDAD_JUGADOR
            self.direction = 'left'
            self.state = 'walk'
        elif teclas[pygame.K_d]:
            self.vx = VELOCIDAD_JUGADOR
            self.direction = 'right'
            self.state = 'walk'

        if self.vx != 0 and self.vy != 0:
            self.vx *= 0.7071
            self.vy *= 0.7071

    def _get_rect_colision(self, pos_x=None, pos_y=None):
        x = self.x if pos_x is None else pos_x
        y = self.y if pos_y is None else pos_y

        # Hitbox de pies: permite acercarse visualmente sin atravesar objetos.
        hit_w = int(SPRITE_ANCHO_JUEGO * 0.34)
        hit_h = int(SPRITE_ALTO_JUEGO * 0.26)
        hit_x = int(x + (SPRITE_ANCHO_JUEGO - hit_w) / 2)
        hit_y = int(y + SPRITE_ALTO_JUEGO - hit_h)
        return pygame.Rect(hit_x, hit_y, hit_w, hit_h)

    def update(self, obstaculos):
        nuevo_x = self.x + self.vx
        nuevo_x = max(0, min(nuevo_x, self.ancho_mundo - SPRITE_ANCHO_JUEGO))
        rect_x = self._get_rect_colision(pos_x=nuevo_x, pos_y=self.y)
        for obstaculo in obstaculos:
            if rect_x.colliderect(obstaculo):
                if self.vx > 0:
                    nuevo_x = obstaculo.left - (SPRITE_ANCHO_JUEGO - rect_x.width) / 2 - rect_x.width
                elif self.vx < 0:
                    nuevo_x = obstaculo.right - (SPRITE_ANCHO_JUEGO - rect_x.width) / 2
                rect_x = self._get_rect_colision(pos_x=nuevo_x, pos_y=self.y)
        self.x = max(0, min(nuevo_x, self.ancho_mundo - SPRITE_ANCHO_JUEGO))

        nuevo_y = self.y + self.vy
        nuevo_y = max(0, min(nuevo_y, self.alto_mundo - SPRITE_ALTO_JUEGO))
        rect_y = self._get_rect_colision(pos_x=self.x, pos_y=nuevo_y)
        for obstaculo in obstaculos:
            if rect_y.colliderect(obstaculo):
                if self.vy > 0:
                    nuevo_y = obstaculo.top - (SPRITE_ALTO_JUEGO - rect_y.height) - rect_y.height
                elif self.vy < 0:
                    nuevo_y = obstaculo.bottom - (SPRITE_ALTO_JUEGO - rect_y.height)
                rect_y = self._get_rect_colision(pos_x=self.x, pos_y=nuevo_y)
        self.y = max(0, min(nuevo_y, self.alto_mundo - SPRITE_ALTO_JUEGO))
        
        self.y_bottom = self.y + SPRITE_ALTO_JUEGO

        self.animation_timer += VELOCIDAD_ANIMACION_JUGADOR
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.frame_index += 1
            current_anim = self.animations[f'{self.state}_{self.direction}']
            if self.frame_index >= len(current_anim):
                self.frame_index = 0
            self.image = current_anim[self.frame_index]

    def draw(self, superficie, cam_x, cam_y):
        superficie.blit(self.image, (self.x - cam_x, self.y - cam_y))

    def obtener_punto_frontal(self, distancia=TILE_ANCHO // 2):
        punto_x = self.x + (SPRITE_ANCHO_JUEGO / 2)
        punto_y = self.y + (SPRITE_ALTO_JUEGO * 0.72)

        if self.direction == 'up':
            punto_y -= distancia
        elif self.direction == 'down':
            punto_y += distancia
        elif self.direction == 'left':
            punto_x -= distancia
        elif self.direction == 'right':
            punto_x += distancia

        return int(punto_x), int(punto_y)

# ==========================================
# 5. CICLO PRINCIPAL
# ==========================================
def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
    pygame.display.set_caption("Moonvale - Hackathon Prototype")
    reloj = pygame.time.Clock()
    superficie_camara = pygame.Surface((CAMARA_VISTA_ANCHO, CAMARA_VISTA_ALTO), pygame.SRCALPHA)

    try:
        hoja_tiles = pygame.image.load(asset_path("FieldsTileset.png")).convert_alpha()
    except FileNotFoundError:
        print("ERROR: No se encontró 'FieldsTileset.png' en la carpeta Assets.")
        sys.exit(1)
    
    granja = Granja(MAPA_ANCHO, MAPA_ALTO, hoja_tiles)

    try:
        hoja_arboles = pygame.image.load(asset_path("treeAnims.png")).convert_alpha()
    except FileNotFoundError:
        print("ERROR: No se encontró 'treeAnims.png' en la carpeta Assets.")
        sys.exit(1)

    decoraciones = [
        Casa(asset_path("House1.png"), 20, 20),
        Casa(asset_path("House2.png"), 264, 20), 
        Casa(asset_path("House3.png"), 600, 20), 
        Casa(asset_path("House4.png"), 600, 250), 
    ]
    
    arboles = [
        Arbol(hoja_arboles, 250, 200, 0), 
        Arbol(hoja_arboles, 400, 300, 3), 
        # A esta instancia en específico le decimos que tome 96 píxeles de ancho
        Arbol(hoja_arboles, 550, 200, 6, ancho_override=96)  
    ]

    # Tamaño del mundo basado en el mapa principal.
    ancho_mundo = granja.ancho_px
    alto_mundo = granja.alto_px

    jugador = Jugador(ancho_mundo // 2, alto_mundo // 2, ancho_mundo, alto_mundo)
    camara = Camara(ancho_mundo, alto_mundo)

    herramienta_actual = HERRAMIENTA_HACHA
    mensaje_accion = "Herramienta lista"
    tiempo_mensaje = 0
    
    corriendo = True
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1:
                    herramienta_actual = HERRAMIENTA_HACHA
                    mensaje_accion = "Herramienta activa: Hacha"
                    tiempo_mensaje = 180
                elif evento.key == pygame.K_2:
                    herramienta_actual = HERRAMIENTA_AZADA
                    mensaje_accion = "Herramienta activa: Azada"
                    tiempo_mensaje = 180
                elif evento.key == pygame.K_3:
                    herramienta_actual = HERRAMIENTA_REGADERA
                    mensaje_accion = "Herramienta activa: Regadera"
                    tiempo_mensaje = 180

                if evento.key == pygame.K_e:
                    punto_frontal = jugador.obtener_punto_frontal()
                    accion_exitosa = False

                    if herramienta_actual == HERRAMIENTA_HACHA:
                        for arbol in arboles[:]:
                            if arbol.get_collision_rect().collidepoint(punto_frontal):
                                arboles.remove(arbol)
                                accion_exitosa = True
                                break

                        mensaje_accion = "Arbol talado" if accion_exitosa else "No hay arbol al frente"

                    elif herramienta_actual == HERRAMIENTA_AZADA:
                        parcela_objetivo = granja.posicion_a_parcela(*punto_frontal)
                        if parcela_objetivo:
                            accion_exitosa = granja.arar_parcela(parcela_objetivo[0], parcela_objetivo[1])
                        mensaje_accion = "Tierra labrada" if accion_exitosa else "No se puede labrar ahi"

                    elif herramienta_actual == HERRAMIENTA_REGADERA:
                        parcela_objetivo = granja.posicion_a_parcela(*punto_frontal)
                        if parcela_objetivo:
                            accion_exitosa = granja.regar_parcela(parcela_objetivo[0], parcela_objetivo[1])
                        mensaje_accion = "Tierra regada" if accion_exitosa else "Primero labra la tierra"

                    tiempo_mensaje = 180

                if evento.key == pygame.K_SPACE:
                    print("\n--- Iniciando DEMO de Riego Recursivo ---")
                    granja.regar_en_cadena(5, 5, 4)

        jugador.handle_input()

        obstaculos = [obj.get_collision_rect() for obj in decoraciones + arboles]
        jugador.update(obstaculos)
        camara.update(jugador.x, jugador.y)

        for arb in arboles:
            arb.update()

        superficie_camara.fill(PASTEL_SKY_BLUE)
        granja.draw(superficie_camara, camara.x, camara.y)

        todos_los_sprites = decoraciones + arboles + [jugador]
        todos_los_sprites.sort(key=lambda s: s.y_bottom)
        
        for spr in todos_los_sprites:
            spr.draw(superficie_camara, camara.x, camara.y)

        vista_escalada = pygame.transform.smoothscale(superficie_camara, (ANCHO_PANTALLA, ALTO_JUEGO))
        pantalla.blit(vista_escalada, (0, 0))

        pygame.draw.rect(pantalla, DARK_GRAY_UI, (0, ALTO_JUEGO, ANCHO_PANTALLA, ALTO_UI))
        fuente = pygame.font.SysFont("Arial", 22)
        texto_controles = "WASD mover | 1 Hacha | 2 Azada | 3 Regadera | E usar"
        texto_herramienta = f"Herramienta actual: {herramienta_actual.upper()}"
        pantalla.blit(fuente.render(texto_controles, True, (200, 200, 200)), (20, ALTO_JUEGO + 20))
        pantalla.blit(fuente.render(texto_herramienta, True, (240, 240, 160)), (20, ALTO_JUEGO + 50))

        if tiempo_mensaje > 0:
            pantalla.blit(fuente.render(mensaje_accion, True, (170, 255, 170)), (420, ALTO_JUEGO + 50))
            tiempo_mensaje -= 1

        pygame.display.flip()
        reloj.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()