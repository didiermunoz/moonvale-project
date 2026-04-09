# Moonvale Project

Proyecto de juego 2D estilo farming/sandbox hecho con pygame.

## Que incluye el juego

- Mapa grande con camara que sigue al jugador.
- Sistema de movimiento 8 direcciones con colisiones.
- Herramientas base: azada, hacha y regadera.
- Sistema de terreno arado, riego recursivo y crecimiento de cultivos.
- Inventario visual con seleccion de slots y cantidades.
- NPC vaca con animacion y tienda de compra/venta.
- Cambio de dia al dormir en la puerta de la casa.
- Condicion de victoria por monedas y derrota por limite de dias.
- UI con fuente pixel y musica de fondo en loop.

## Requerimientos

- Python 3.10+
- Sistema con soporte de ventana (pygame)
- Carpeta Assets completa incluida en el repo

## Dependencias

Dependencias directas usadas por el modulo principal:

- pygame
- numpy

Dependencias de libreria estandar usadas:

- sys
- os
- random

Instalacion rapida:

```bash
python -m venv .venv
source .venv/bin/activate
pip install pygame numpy
```

Ejecucion:

```bash
python main.py
```

## Estructura del proyecto

```text
moonvale-project/
  main.py
  README.md
  Assets/
    House1.png
    House2.png
    House3.png
    House4.png
    Cloud_Country.mp3
    FieldsTileset.png
    idle.png
    walking.png
    treeAnims.png
    Sprout Lands - Sprites - Basic pack/
    Sprout Lands - UI Pack - Basic pack/
```

## Referencia del modulo

Modulo principal:

- main.py

Punto de entrada:

- main()

Constantes de gameplay relevantes:

- ANCHO_PANTALLA, ALTO_PANTALLA, FPS
- ESCALA, TAM_TILE, ANCHO_MAPA, ALTO_MAPA
- VELOCIDAD_JUGADOR, VELOCIDAD_ANIMACION, VELOCIDAD_ANIMACION_VACA
- DURACION_TRANSICION_DIA
- META_MONEDAS_VICTORIA, DIA_LIMITE_DERROTA
- Precios de compra/venta de semillas y plantas

## Clases

### EstadoJuego

Responsabilidad:

- Estado global de partida: monedas y dia actual.

POO:

- Encapsulamiento con atributo privado __monedas.
- Property monedas con validacion para no permitir valores negativos.

### EntidadVisible

Responsabilidad:

- Clase base renderizable (image + rect + draw).

POO:

- Abstraccion de una entidad visible del mundo.
- Reutilizacion por herencia en entidades concretas.

### Obstaculo(EntidadVisible)

Responsabilidad:

- Objeto estatico con hitbox de colision.

POO:

- Herencia de draw y estructura base de entidad.

### Vaca(EntidadVisible)

Responsabilidad:

- NPC animado con icono de carrito flotante.

POO:

- Herencia de EntidadVisible.
- Polimorfismo al sobreescribir draw.

### Jugador(EntidadVisible)

Responsabilidad:

- Input, animacion por direccion, movimiento y colisiones.

POO:

- Herencia de EntidadVisible.
- Estado interno de animaciones por direccion.

### Camara

Responsabilidad:

- Seguimiento del jugador y clamping a limites del mapa.

### Granja

Responsabilidad:

- Logica agricola: arar, plantar, regar, cosechar y dibujar tiles/cultivos.

POO:

- Alta cohesion de reglas de farming en una sola entidad.
- Metodo recursivo regar_area_recursiva para propagacion de riego.

### Inventario

Responsabilidad:

- Slots, cantidades, consumo de semillas y render de UI de inventario.

## Funciones

### Utilidades de recursos y sprites

- asset_path(*rutas)
- cargar_imagen_variantes(*rutas_relativas)
- cargar_musica_variantes(*rutas_relativas)
- extraer_sprite_exacto(hoja, col, fila, ancho_tiles, alto_tiles, escala)
- dibujar_texto_con_borde(superficie, fuente, texto, pos, color_texto, color_borde)

### UI de tienda

- construir_layout_tienda(panel_rect)
- draw_tienda(superficie, panel_img, boton_img, fuente_titulo, fuente_texto, layout, modo_tienda, ...)

### Runtime principal

- main()

## Runtime flow summary

1. main() inicializa pygame, ventana, reloj y estado global.
2. Carga hojas de sprites, UI, fuentes, audio y recursos del mapa.
3. Construye objetos del mundo: granja, jugador, camara, inventario, obstaculos y vaca.
4. En cada frame procesa eventos de teclado/raton.
5. Aplica logica de tienda, herramientas, sembrado, riego/cosecha y dormir.
6. Actualiza entidades dinamicas (jugador, vaca, camara).
7. Renderiza mundo, entidades, hover de accion, HUD, prompts y UI de tienda/inventario.
8. Evalua condiciones de victoria/derrota y transiciones de dia.
9. Repite el loop hasta cerrar ventana.

## Controles

- Movimiento: W A S D o flechas.
- Seleccion de slot: teclas 1..7.
- Accion contextual/interaccion: E.
- Uso de herramienta/siembra/regar/cosechar: clic izquierdo.
- Cerrar tienda: ESC.

## Assets usados

### Mundo y tiles

- Sprout Lands - Sprites - Basic pack/Tilesets/Grass.png
- Sprout Lands - Sprites - Basic pack/Tilesets/Fences.png
- Sprout Lands - Sprites - Basic pack/Tilesets/Tilled Dirt.png

### Personajes y NPC

- Sprout Lands - Sprites - Basic pack/Characters/Basic Charakter Spritesheet.png
- Sprout Lands - Sprites - Basic pack/Characters/Free Cow Sprites.png

### Objetos y plantas

- Sprout Lands - Sprites - Basic pack/Objects/Basic Grass Biom things 1.png
- Sprout Lands - Sprites - Basic pack/Objects/Basic_Plants.png
- Sprout Lands - Sprites - Basic pack/Objects/Basic tools and meterials.png
- Sprout Lands - Sprites - Basic pack/Objects/inventory_Light_example_with_slots.png

### UI

- Sprout Lands - UI Pack - Basic pack/Sprite sheets/Setting menu.png
- Sprout Lands - UI Pack - Basic pack/Sprite sheets/buttons/Square Buttons 26x19.png
- Sprout Lands - UI Pack - Basic pack/Sprite sheets/Icons/white icons.png
- Sprout Lands - UI Pack - Basic pack/fonts/pixelFont-7-8x14-sproutLands.ttf

### Extras locales

- House4.png
- Cloud_Country.mp3

## Herencias

Relaciones de herencia declaradas en el codigo:

- EntidadVisible -> clase base
- Obstaculo(EntidadVisible)
- Vaca(EntidadVisible)
- Jugador(EntidadVisible)

## Analisis POO detallado

### Encapsulamiento

- EstadoJuego protege monedas con __monedas y property monedas.
- Regla de negocio embebida: nunca monedas negativas.

### Abstraccion

- EntidadVisible abstrae lo comun de cualquier entidad dibujable.
- Camara abstrae desplazamiento y limites del viewport.
- Granja abstrae reglas de dominio agricola.

### Herencia

- Reutilizacion de logica comun de draw/rect en entidad base.
- Simplifica la composicion del listado entidades para render por profundidad.

### Polimorfismo

- Vaca redefine draw para agregar icono flotante sin romper contrato base.
- Entidades diferentes se procesan uniformemente en la lista entidades.

### Cohesion y responsabilidad

- Granja concentra operaciones del terreno/cultivos.
- Inventario concentra estado de slots/cantidades y su visualizacion.
- draw_tienda separa render de tienda del loop principal.

### Acoplamiento

- main() mantiene alto acoplamiento por centralizar orquestacion de recursos y estados.
- Recomendacion: extraer subsistemas (input, escena, UI, audio) a modulos separados.

### Recursion aplicada

- Granja.regar_area_recursiva implementa flood-fill sobre tiles arados.
- Usa set de visitados para evitar ciclos infinitos.

### Fortalezas actuales

- Arquitectura clara para un prototipo jugable.
- Buen uso de herencia simple y encapsulamiento de estado critico.
- Flujo gameplay completo: recolectar, vender, dormir, progresion por dias.

### Oportunidades de mejora

- Dividir main.py en paquetes (core, entities, systems, ui, data).
- Definir dataclasses para configuracion y assets.
- Desacoplar input de logica de dominio.
- Agregar pruebas unitarias para EstadoJuego y Granja.
- Incorporar tipado estatico progresivo (typing).

---

## Historial de cambios hechos

- Correccion de arranque de main.py.
- Agregado de casa superior en el mapa.
- Sistema de dia y texto en pantalla.
- Dormir por interaccion con puerta + transicion.
- Ajustes iterativos de hitbox de puerta.
- Cercas a ambos lados de la casa.
- Agregado de vaca y posicionamiento.
- Animacion de vaca.
- Icono flotante de carrito sobre la vaca.
- Fuente personalizada para UI.
- Menu de tienda con la vaca (compra/venta).
- Compra de semillas.
- Venta de sobres y plantas (precios distintos).
- Layout de venta reorganizado.
- Correccion de click en venta.
- Prompt contextual en casa.
- Musica de fondo en loop.
