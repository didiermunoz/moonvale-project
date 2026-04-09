# Moonvale Project - Historial de Cambios

Este documento resume, en orden cronologico, los cambios realizados hasta el momento en el proyecto.

## 1) Sincronizacion con GitHub (forzada)
- Se explico el flujo para traer cambios remotos cuando habia divergencia con el remoto.
- Se aplico sincronizacion forzada del repositorio (descartar cambios locales) para alinear el branch local con origin/main.
- Resultado: repositorio local actualizado con el estado remoto.

## 2) Correccion de arranque de main.py
- Se detecto error al iniciar por nombre de archivo con mayusculas/minusculas distinto al real (Linux es case-sensitive).
- Se corrigio la carga del inventario a:
  - inventory_Light_example_with_slots.png
- Resultado: el juego inicio sin ese error de assets.

## 3) Agregado de casa superior en el mapa
- Se agrego carga de House4.png.
- Se coloco la casa centrada en la parte superior del mapa (y=0).
- Se agrego constante ESCALA_CASA para controlar el tamano visual.
- Resultado: casa visible, ajustable por escala y con colision como obstaculo.

## 4) Sistema de dia y texto en pantalla
- Se agrego indicador de dia en esquina superior izquierda.
- Se implemento helper de texto con borde: dibujar_texto_con_borde(...).
- Inicialmente hubo avance de dia por tiempo; luego se sustituyo por interaccion con puerta.
- Resultado: el numero de dia se muestra con mejor legibilidad.

## 5) Dormir por interaccion con puerta + transicion
- Se implemento zona de puerta (rectangulo de interaccion) en la parte frontal de la casa.
- Al presionar E cerca de la puerta:
  - aumenta dia_actual,
  - inicia transicion negra DURACION_TRANSICION_DIA,
  - se bloquean acciones durante la transicion.
- Se agrego mensaje contextual: "Presiona E para dormir".
- Resultado: cambio de dia controlado por gameplay y no por temporizador.

## 6) Ajustes iterativos de hitbox de puerta
- Se ajusto varias veces la zona de interaccion para que no fuera ni demasiado amplia ni demasiado estricta.
- Ajuste actual:
  - zona_interaccion_puerta = puerta_rect.inflate(int(TAM_TILE * 0.35), int(TAM_TILE * 0.5))
  - zona_interaccion_puerta.y += int(TAM_TILE * 0.5)
- Resultado: interaccion mas usable al frente de la puerta.

## 7) Cercas a ambos lados de la casa
- Se inicio con cercas procedurales y despues se migro a sprites desde Fences.png.
- Se eligieron piezas conectadas horizontales (izquierda, medio, derecha).
- Se dejo visual de una sola linea (recorte de mitad superior del tile de cerca).
- Se aumento altura visual de la cerca en el escalado para mejor presencia.
- Resultado: cercas laterales conectadas, coherentes y con colision.

## 8) Agregado de vaca y posicionamiento
- Se agrego entidad vaca cerca del extremo de la cerca izquierda.
- Se escalo la vaca para que tuviera mayor presencia en escena.
- Se le agrego hitbox para colision con jugador.
- Resultado: NPC/objeto interactivo visible y bloqueante.

## 9) Animacion de vaca
- Se implemento clase Vaca con frames animados del spritesheet.
- Se agrego update con temporizador de animacion independiente.
- Resultado: vaca con movimiento visual continuo.

## 10) Icono flotante de carrito sobre la vaca
- Se agrego icono de carrito extraido de white icons.png.
- Se corrigio recorte del icono usando rectangulo exacto (en lugar de grilla fija).
- Se agrego flotacion vertical suave con seno para feedback visual.
- Resultado: indicador claro de interaccion de tienda.

## 11) Limpieza de archivos de debug
- Se eliminaron imagenes temporales usadas para depurar atlas/grillas:
  - white_icons_grid_debug.png
  - fences_grid_debug.png
  - fences_tiles_big_debug.png
- Resultado: carpeta Assets mas limpia.

## 12) Fuente personalizada para UI
- Se cargo y aplico pixelFont-7-8x14-sproutLands.ttf para textos principales.
- Se uso en dia, transicion y UI de tienda.
- Resultado: estilo visual mas consistente con el pack grafico.

## 13) Menu de tienda con la vaca (compra/venta)
- Se creo modal de tienda al presionar E cerca de la vaca.
- Se agregaron:
  - Tabs: Compra / Venta
  - Boton cerrar (X)
  - Visualizacion de monedas
  - Filas por cultivo
- Se bloquearon movimientos/interacciones normales mientras la tienda esta abierta.
- Resultado: flujo basico de comercio funcional.

## 14) Compra de semillas
- Se definieron dos semillas vendibles:
  - Trigo
  - Jitomate
- Se usan sprites de sobres desde Basic_Plants.png (columna 1, filas 1 y 2).
- Se implementaron precios de compra:
  - PRECIO_COMPRA_SEMILLA_1 = 15
  - PRECIO_COMPRA_SEMILLA_2 = 22
- Resultado: compras descuentan monedas y aumentan inventario de semillas.

## 15) Venta de sobres y plantas (precios distintos)
- Se implemento inventario separado para:
  - semillas (sobres)
  - cosechas (plantas crecidas)
- Se agrego venta por cada tipo con precios independientes.
- Plantas crecidas venden mas caro que sobres.
- Resultado: economia con diferencia de valor entre materia prima y producto final.

## 16) Layout de venta reorganizado
- Panel derecho en modo venta ajustado para mostrar:
  - Sobre arriba
  - Planta abajo
  por cada cultivo.
- Se agregaron iconos pequenos para cada opcion de venta.
- Resultado: lectura mas clara y menos confusa en botones de venta.

## 17) Correccion de click en venta
- Se arreglo conflicto de deteccion de clics en el manejo de eventos.
- Antes algunos clics en venta no entraban por prioridad/condicionales.
- Se condicionaron correctamente acciones de compra y venta segun modo_tienda.
- Resultado: botones de venta detectan correctamente.

## 18) Prompt contextual en casa
- Se agrego mensaje contextual en pantalla para la casa:
  - "Presiona E para dormir"
- Resultado: feedback consistente con el prompt de la vaca.

## 19) Musica de fondo en loop
- Se agrego reproduccion automatica de musica al iniciar el juego.
- Archivo usado en Assets: Cloud_Country.mp3.
- Configuracion actual:
  - Reproduccion infinita con pygame.mixer.music.play(-1)
  - Volumen inicial con constante VOLUMEN_MUSICA = 0.35
- Resultado: el juego ahora tiene musica ambiental continua.

## Estado actual del proyecto
- Juego inicia sin error de assets principal reportado.
- Casa, cercas, vaca, icono flotante y tienda estan integrados.
- Cambio de dia por dormir en puerta esta funcional con transicion negra.
- Economia base de compra/venta implementada.

## Pendiente natural (siguiente mejora sugerida)
- Completar ciclo de cultivo para poblar inventario_cosechas desde gameplay (siembra, crecimiento, cosecha), y no solo por pruebas/manual.
