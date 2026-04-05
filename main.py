import pygame
import sys
import os

# ==========================================
# 0. CONFIGURACIÓN Y CONSTANTES
# ==========================================
os.environ['SDL_VIDEO_CENTERED'] = '1'

ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600
FPS = 60

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

# --- CONFIGURACIÓN MAPA ---
TILE_ANCHO = 64
TILE_ALTO = 64

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
        self.regada = False
    def regar(self):
        self.regada = True

class Granja:
    def __init__(self, ancho, alto, hoja_tiles):
        self.ancho = ancho
        self.alto = alto
        self.columnas_pantalla = (ANCHO_PANTALLA // TILE_ANCHO) + 1
        self.filas_pantalla = ((ALTO_PANTALLA - 100) // TILE_ALTO) + 1
        
        self.tile_base = obtiene_tile(hoja_tiles, 0, 0, TILE_ANCHO, TILE_ALTO)
        self.tile_regado = obtiene_tile(hoja_tiles, 1, 0, TILE_ANCHO, TILE_ALTO)

        self.matriz = [[Parcela(PASTEL_SKY_BLUE,DARK_GRAY_UI) for _ in range(alto)] for _ in range(ancho)]
        
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

    def draw(self, pantalla):
        for col in range(self.columnas_pantalla):
            for fila in range(self.filas_pantalla):
                pantalla.blit(self.tile_base, (col * TILE_ANCHO, fila * TILE_ALTO))
        
        for x in range(self.ancho):
            for y in range(self.alto):
                if self.matriz[x][y].regada:
                    pantalla.blit(self.tile_regado, (x * TILE_ANCHO, y * TILE_ALTO))

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
            sys.exit()
        
        self.y_bottom = y + self.image.get_height()

    def draw(self, pantalla):
        pantalla.blit(self.image, (self.x, self.y))

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

    def draw(self, pantalla):
        pantalla.blit(self.image, (self.x, self.y))

    def update(self):
        self.animation_timer += VELOCIDAD_ANIMACION_ARBOL
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.frame_index = 0
            self.image = self.frames[self.frame_index]

    def draw(self, pantalla):
        pantalla.blit(self.image, (self.x, self.y))

# ==========================================
# 4. CLASE JUGADOR 
# ==========================================
class Jugador:
    def __init__(self, x_inicio, y_inicio):
        self.x = x_inicio
        self.y = y_inicio
        self.vx = 0
        self.vy = 0
        
        try:
            hoja_idle = pygame.image.load("assets/idle.png").convert_alpha()
            hoja_walk = pygame.image.load("assets/walking.png").convert_alpha()
        except FileNotFoundError:
            print("ERROR: Faltan 'assets/idle.png' o 'assets/walking.png'.")
            sys.exit()

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

    def update(self):
        self.x += self.vx
        self.y += self.vy
        
        self.x = max(0, min(self.x, ANCHO_PANTALLA - SPRITE_ANCHO_JUEGO))
        self.y = max(0, min(self.y, ALTO_PANTALLA - 100 - SPRITE_ALTO_JUEGO))
        
        self.y_bottom = self.y + SPRITE_ALTO_JUEGO

        self.animation_timer += VELOCIDAD_ANIMACION_JUGADOR
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.frame_index += 1
            current_anim = self.animations[f'{self.state}_{self.direction}']
            if self.frame_index >= len(current_anim):
                self.frame_index = 0
            self.image = current_anim[self.frame_index]

    def draw(self, pantalla):
        pantalla.blit(self.image, (self.x, self.y))

# ==========================================
# 5. CICLO PRINCIPAL
# ==========================================
def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
    pygame.display.set_caption("Moonvale - Hackathon Prototype")
    reloj = pygame.time.Clock()

    try:
        hoja_tiles = pygame.image.load("assets/FieldsTileset.png").convert_alpha()
    except FileNotFoundError:
        print("ERROR: No se encontró 'assets/FieldsTileset.png'.")
        sys.exit()
    
    granja = Granja(10, 10, hoja_tiles)
    jugador = Jugador(ANCHO_PANTALLA//2, (ALTO_PANTALLA//2) - 100)

    try:
        hoja_arboles = pygame.image.load("assets/treeAnims.png").convert_alpha()
    except FileNotFoundError:
        print("ERROR: No se encontró 'assets/treeAnims.png'.")
        sys.exit()

    decoraciones = [
        Casa("assets/House1.png", 20, 20),
        Casa("assets/House2.png", 264, 20), 
        Casa("assets/House3.png", 600, 20), 
        Casa("assets/House4.png", 600, 250), 
    ]
    
    arboles = [
        Arbol(hoja_arboles, 250, 200, 0), 
        Arbol(hoja_arboles, 400, 300, 3), 
        # A esta instancia en específico le decimos que tome 96 píxeles de ancho
        Arbol(hoja_arboles, 550, 200, 6, ancho_override=96)  
    ]
    
    corriendo = True
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    print("\n--- Iniciando DEMO de Riego Recursivo ---")
                    granja.regar_en_cadena(5, 5, 4)

        jugador.handle_input()
        jugador.update()

        for arb in arboles:
            arb.update()

        granja.draw(pantalla)
        
        pygame.draw.rect(pantalla, DARK_GRAY_UI, (0, ALTO_PANTALLA - 100, ANCHO_PANTALLA, 100))
        fuente = pygame.font.SysFont("Arial", 22)
        texto = fuente.render("Área de Inventario (WASD mover, ESPACIO demo Recursividad)", True, (200, 200, 200))
        pantalla.blit(texto, (20, ALTO_PANTALLA - 60))

        todos_los_sprites = decoraciones + arboles + [jugador]
        todos_los_sprites.sort(key=lambda s: s.y_bottom)
        
        for spr in todos_los_sprites:
            spr.draw(pantalla)

        pygame.display.flip()
        reloj.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()