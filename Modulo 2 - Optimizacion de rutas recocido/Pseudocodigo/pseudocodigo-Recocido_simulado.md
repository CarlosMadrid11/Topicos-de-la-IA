# Pseudocódigo — recocido_simulado.py
## Proyecto: Optimización de Rutas de Distribución con Recocido Simulado
### Culiacán, Sinaloa — TecNM

---

## Contexto del problema

Se tiene una red logística de **100 nodos** dentro de Culiacán:
- **10 Centros de Distribución (CDs)** — índices 0 al 9 en las matrices
- **90 Tiendas** — índices 10 al 99 en las matrices

Las matrices son **100×100**, simétricas y con diagonal = 0. Fueron generadas
con la fórmula de Haversine a partir de coordenadas GPS reales. La matriz de
combustible es exactamente `distancia × 0.15`.

El objetivo es minimizar la función de costo ponderado:
```
costo = (0.3 × distancia_total) + (0.7 × combustible_total)
```
Se prioriza el combustible (70%) por ser el factor de mayor impacto operativo.

---

## Función 1 — `solucion_inicial`

### Por qué existe
El algoritmo de Recocido Simulado necesita un punto de partida. Esta función
genera una solución base usando una heurística greedy: asigna cada tienda al
CD más cercano. La diferencia clave respecto al proyecto del semestre anterior
es la **restricción de cupo máximo de 10 tiendas por CD**, lo que evita que
un solo CD acumule demasiadas tiendas (el semestre pasado CD3 terminó con 22).

### Pseudocódigo
```
FUNCIÓN solucion_inicial(df_tiendas, matriz_distancias):

    n_cedis ← cantidad de filas donde Tipo == "Centro de Distribución"
    rutas   ← lista de n_cedis listas vacías
    cupo    ← lista de n_cedis ceros

    PARA cada índice i en df_tiendas:
        SI df_tiendas[i]["Tipo"] == "Tienda":

            distancias_a_cedis ← fila i de matriz_distancias, solo columnas 0 a n_cedis
            orden ← índices de distancias_a_cedis ordenados de menor a mayor (argsort)

            PARA cada cd en orden:
                SI cupo[cd] < 10:
                    rutas[cd].agregar(i)
                    cupo[cd] += 1
                    PARAR búsqueda (break)

    RETORNAR rutas
```

### Decisiones tomadas
- Se usa `np.argsort` en lugar de `np.argmin` para poder recorrer opciones
  en orden si el CD más cercano ya está lleno.
- El cupo se inicializa con `[0] * n_cedis` en lugar de hardcodear 10 ceros,
  para que funcione aunque cambie el número de CDs.
- El `break` garantiza que cada tienda se asigne a exactamente un CD.

---

## Función 2 — `costo_ruta`

### Por qué existe
Necesitamos evaluar qué tan buena o mala es una ruta individual. Esta función
simula el recorrido físico de un vehículo: parte del CD, visita cada tienda
asignada en orden, y regresa al CD. Suma distancia y combustible de cada tramo
y aplica la fórmula ponderada.

### Pseudocódigo
```
FUNCIÓN costo_ruta(ruta, id_cedis, matriz_distancias, matriz_combustible):

    costo_distancia ← 0
    costo_gasolina  ← 0
    actual          ← id_cedis    # el vehículo arranca en el CD
    alpha ← 0.3
    beta  ← 0.7

    PARA cada nodo en ruta:
        costo_distancia += matriz_distancias[actual][nodo]
        costo_gasolina  += matriz_combustible[actual][nodo]
        actual ← nodo              # el vehículo avanza al siguiente punto

    # Regreso al CD desde la última tienda
    costo_distancia += matriz_distancias[actual][id_cedis]
    costo_gasolina  += matriz_combustible[actual][id_cedis]

    costo_ponderado ← (alpha × costo_distancia) + (beta × costo_gasolina)

    RETORNAR (costo_ponderado, costo_distancia, costo_gasolina)
```

### Decisiones tomadas
- Se retornan los 3 valores (no solo el ponderado) porque `main.py` necesita
  imprimir distancia y gasolina por separado en la tabla de resultados.
- El regreso al CD fuera del `for` es intencional — el bucle no cubre ese
  último tramo porque `actual` ya no es un nodo de la ruta sino la última tienda.
- `alpha = 0.3` y `beta = 0.7` priorizan combustible sobre distancia, decisión
  justificada en que el costo de combustible es el gasto operativo principal.

---

## Función 3 — `costo_total`

### Por qué existe
Es el agregador global. El algoritmo necesita comparar soluciones completas
(todas las rutas juntas), no rutas individuales. Esta función llama a
`costo_ruta` para cada CD y acumula los resultados.

### Pseudocódigo
```
FUNCIÓN costo_total(rutas, matriz_distancias, matriz_combustible):

    total_ponderado ← 0
    total_distancia ← 0
    total_gasolina  ← 0

    PARA cada (id_cedis, ruta) en enumerate(rutas):
        SI ruta no está vacía:
            (costo_p, distancia, gasolina) ← costo_ruta(ruta, id_cedis, ...)
            total_ponderado += costo_p
            total_distancia += distancia
            total_gasolina  += gasolina

    RETORNAR (total_ponderado, total_distancia, total_gasolina)
```

### Decisiones tomadas
- Se usa `enumerate` para obtener simultáneamente el índice del CD y su ruta,
  ya que `costo_ruta` necesita saber desde qué nodo parte el recorrido.
- La verificación `if ruta` evita llamar a `costo_ruta` con una lista vacía,
  lo que podría generar errores si algún CD no tiene tiendas asignadas.

---

## Función 4 — `generar_vecino`

### Por qué existe
El Recocido Simulado explora el espacio de soluciones generando variaciones
de la solución actual. Esta función implementa el operador **swap**: intercambia
una tienda de un CD con una tienda de otro CD distinto. Esto permite explorar
configuraciones diferentes sin romper la estructura de las rutas.

### Pseudocódigo
```
FUNCIÓN generar_vecino(rutas):

    rutas_vecinas ← copia profunda de rutas    # no modificar el original

    r1 ← índice aleatorio entre 0 y m-1
    posibles ← CDs con al menos 1 tienda y distintos a r1

    SI posibles está vacío:
        RETORNAR rutas_vecinas sin cambios

    r2 ← elegir aleatoriamente de posibles

    SI rutas_vecinas[r1] está vacía:
        # Caso especial: mover tienda de r2 a r1
        nodo ← extraer tienda aleatoria de r2
        agregar nodo a r1
        RETORNAR rutas_vecinas

    # Caso general: swap
    idx1 ← índice aleatorio dentro de r1
    idx2 ← índice aleatorio dentro de r2

    MIENTRAS r1 == r2 Y idx1 == idx2:
        idx2 ← nuevo índice aleatorio dentro de r2

    intercambiar rutas_vecinas[r1][idx1] con rutas_vecinas[r2][idx2]

    RETORNAR rutas_vecinas
```

### Decisiones tomadas
- La copia profunda `[list(r) for r in rutas]` es esencial — sin ella Python
  modifica la solución original por referencia y el algoritmo no puede comparar
  la solución actual con el vecino.
- El swap mantiene el conteo de tiendas por CD estable (lo que uno pierde,
  el otro gana), evitando que CDs queden con muy pocas tiendas con el tiempo.
- El `while r1 == r2 and idx1 == idx2` evita el swap de un nodo consigo mismo,
  que generaría un vecino idéntico a la solución actual.

---

## Función 5 — `optimizacion_recocido_simulado`

### Por qué existe
Es el núcleo del algoritmo. Coordina todas las funciones anteriores en un
proceso iterativo inspirado en el enfriamiento de metales: empieza con alta
temperatura (acepta casi cualquier solución) y la va reduciendo gradualmente
(se vuelve más selectivo). Esto le permite escapar de óptimos locales.

### Pseudocódigo
```
FUNCIÓN optimizacion_recocido_simulado(df_tiendas, matriz_distancias,
                                        matriz_combustible, t0,
                                        factor_enfriamiento, iteraciones, tf):

    # Punto de partida
    actual ← solucion_inicial(df_tiendas, matriz_distancias)
    (actual_costo, actual_distancia, actual_gasolina) ← costo_total(actual, ...)

    # Guardar la mejor solución encontrada hasta ahora
    mejor           ← copia profunda de actual
    mejor_costo     ← actual_costo
    mejor_distancia ← actual_distancia
    mejor_gasolina  ← actual_gasolina

    # Inicializar historiales para las 4 gráficas
    historial_costos     ← []
    historial_distancias ← []
    historial_gasolinas  ← []
    historial_mejora     ← []

    t ← t0

    # Bucle principal: corre mientras la temperatura sea mayor que tf
    MIENTRAS t > tf:

        # Bucle interno: explora 'iteraciones' vecinos a temperatura constante
        REPETIR 'iteraciones' veces:

            vecino ← generar_vecino(actual)
            (vecino_costo, vecino_dist, vecino_gas) ← costo_total(vecino, ...)
            delta ← vecino_costo - actual_costo

            # Criterio de aceptación de Metropolis
            SI delta < 0:
                actual ← vecino          # siempre acepta si mejora
            SINO SI random() < exp(-delta / t):
                actual ← vecino          # acepta empeoramiento con probabilidad

            # Actualizar mejor solución global si corresponde
            SI actual_costo < mejor_costo:
                mejor ← copia profunda de actual
                mejor_costo ← actual_costo
                ...

            # Registrar estado actual en historiales
            historial_costos.agregar(actual_costo)
            historial_distancias.agregar(actual_distancia)
            historial_gasolinas.agregar(actual_gasolina)
            historial_mejora.agregar(
                ((historial_costos[0] - mejor_costo) / historial_costos[0]) × 100
            )

        # Enfriar temperatura al terminar las iteraciones de este ciclo
        t ← t × factor_enfriamiento

    RETORNAR mejor, mejor_costo, mejor_distancia, mejor_gasolina,
             historial_costos, historial_distancias,
             historial_gasolinas, historial_mejora
```

### Decisiones tomadas
- `t0=1000`, `factor_enfriamiento=0.99`, `iteraciones=1000`, `tf=1e-6` son
  los parámetros usados. Con estos valores el algoritmo corre ~2,000,000
  iteraciones totales, suficiente para converger en este problema.
- `historial_costos[0]` como referencia para `historial_mejora` representa
  el costo de la solución inicial — el punto de comparación base.
- La copia profunda `[list(r) for r in actual]` al guardar `mejor` es crítica:
  sin ella `mejor` y `actual` apuntarían al mismo objeto y `mejor` cambiaría
  en cada iteración perdiendo la mejor solución encontrada.
- El criterio `exp(-delta / t)` es la función de Metropolis: cuando `t` es
  alta, `exp` es cercano a 1 y acepta casi todo. Cuando `t` es baja, `exp`
  es cercano a 0 y solo acepta mejoras. Esto simula el enfriamiento gradual.

---

## Parámetros del algoritmo

| Parámetro | Valor | Descripción |
|---|---|---|
| `t0` | 1000 | Temperatura inicial — alta para explorar ampliamente |
| `factor_enfriamiento` | 0.99 | Multiplica la temperatura cada ciclo |
| `iteraciones` | 1000 | Vecinos explorados por nivel de temperatura |
| `tf` | 1e-6 | Temperatura mínima para detener el algoritmo |
| `alpha` | 0.3 | Peso de la distancia en el costo ponderado |
| `beta` | 0.7 | Peso del combustible en el costo ponderado |

---

## Fórmula de costo ponderado

```
costo_ponderado = (0.3 × distancia_total) + (0.7 × gasolina_total)
```

Se prioriza el combustible porque representa el mayor gasto operativo variable
en una flota de distribución. La distancia influye menos porque los costos
fijos (tiempo, desgaste) son secundarios al consumo de combustible.