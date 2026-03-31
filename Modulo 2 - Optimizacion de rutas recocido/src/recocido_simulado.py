import math
import random
import numpy as np

# ------------------------------------------------------------
# FUNCIÓN 1: solucion_inicial
#
# El Recocido Simulado necesita un punto de partida válido antes
# de comenzar a explorar. Se usa una heurística greedy: asignar
# cada tienda al CD más cercano según la matriz de distancias
# Haversine. Esto no garantiza la solución óptima, pero produce
# una solución factible rápidamente para que el algoritmo tenga
# desde dónde iterar.
#
# La restricción de cupo máximo (10 tiendas por CD) es crítica:
# sin ella, el greedy acumula todas las tiendas en el CD más
# céntrico. En una versión anterior sin este límite, CD3 terminó
# con 22 tiendas mientras otros quedaban con 3 o 4, lo que
# hacía inútil la paralelización de rutas.
#
# Se usa np.argsort en lugar de np.argmin porque necesitamos
# recorrer los CDs en orden de cercanía: si el más cercano ya
# está lleno, intentamos con el segundo más cercano, y así.
# El break garantiza que cada tienda se asigne exactamente una vez.
#
# El cupo se inicializa con [0]*n_cedis en lugar de hardcodear
# 10 ceros para que la función siga funcionando si el número
# de CDs cambia en versiones futuras del proyecto.
# ------------------------------------------------------------
def solucion_inicial(df_tiendas, matriz_distancias):
    n_cedis = len(df_tiendas[df_tiendas["Tipo"] == "Centro de Distribución"])
    rutas = [[] for _ in range(n_cedis)]
    cupo = [0] * n_cedis

    for i in range(len(df_tiendas)):
        if df_tiendas.loc[i, "Tipo"] == "Tienda":
            distancias_a_cedis = matriz_distancias[i, :n_cedis]
            orden = np.argsort(distancias_a_cedis)
            for cd in orden:
                if cupo[cd] < 10:
                    cupo[cd] += 1
                    rutas[cd].append(i)
                    break

    return rutas

# ------------------------------------------------------------
# FUNCIÓN 2: costo_ruta
#
# Evalúa el costo de una ruta individual simulando el recorrido
# físico del vehículo: parte del CD (id_cedis), visita cada
# tienda en el orden en que aparece en la lista, y regresa al CD.
# La variable `actual` actúa como puntero de posición del vehículo.
#
# Se retornan los 3 valores (costo_ponderado, distancia, gasolina)
# y no solo el ponderado, porque main.py necesita mostrarlos por
# separado en la tabla de resultados. Colapsar todo en un solo
# valor obligaría a recalcular después.
#
# El regreso al CD se suma fuera del bucle for intencionalmente:
# al terminar el for, `actual` apunta a la última tienda visitada,
# no al CD. Si se incluyera dentro del bucle se contaría el
# regreso en cada paso intermedio, duplicando ese tramo.
#
# La ponderación alpha=0.3 / beta=0.7 prioriza combustible sobre
# distancia porque en la operación real el gasto en combustible
# es el principal costo variable de la flota. La distancia igual
# importa (desgaste, tiempo), pero en menor medida.
# La matriz de combustible ya incorpora este factor: fue generada
# como distancia × 0.15, por lo que ambas métricas están en
# escalas comparables.
# ------------------------------------------------------------
def costo_ruta(ruta, id_cedis, matriz_distancias, matriz_combustible):
    costo_distancia = 0
    costo_gasolina  = 0
    actual          = id_cedis
    alpha = 0.3
    beta  = 0.7

    for nodo in ruta:
        costo_distancia += matriz_distancias[actual][nodo]
        costo_gasolina  += matriz_combustible[actual][nodo]
        actual = nodo

    costo_distancia += matriz_distancias[actual][id_cedis]
    costo_gasolina  += matriz_combustible[actual][id_cedis]

    costo_ponderado = (alpha * costo_distancia) + (beta * costo_gasolina)
    return costo_ponderado, costo_distancia, costo_gasolina

# ------------------------------------------------------------
# FUNCIÓN 3: costo_total
#
# El Recocido Simulado compara soluciones completas, no rutas
# individuales. Esta función agrega los costos de los 10 CDs
# en un único valor global que el algoritmo puede comparar entre
# iteraciones.
#
# Se usa enumerate para obtener simultáneamente el índice del CD
# (id_cedis) y su lista de tiendas (ruta), ya que costo_ruta
# necesita saber desde qué nodo parte el vehículo.
#
# La verificación `if ruta` evita llamar a costo_ruta con una
# lista vacía, lo que causaría que el bucle interno no ejecute
# y el último tramo (regreso al CD) se sume desde el propio CD,
# generando un costo de 0 en lugar de un error, pero distorsionando
# el total si las matrices no tienen diagonal exactamente en 0.
# ------------------------------------------------------------
def costo_total(rutas, matriz_distancias, matriz_combustible):
    total_ponderado = 0
    total_distancia = 0
    total_gasolina  = 0

    for id_cedis, ruta in enumerate(rutas):
        if ruta:
            costo_p, distancia, gasolina = costo_ruta(ruta, id_cedis, matriz_distancias, matriz_combustible)
            total_ponderado += costo_p
            total_distancia += distancia
            total_gasolina  += gasolina

    return total_ponderado, total_distancia, total_gasolina

# ------------------------------------------------------------
# FUNCIÓN 4: generar_vecino
#
# El Recocido Simulado explora el espacio de soluciones mediante
# perturbaciones pequeñas. Aquí se implementa el operador swap:
# intercambiar una tienda de un CD con una tienda de otro CD
# distinto. Esto mantiene el conteo total de tiendas por CD
# estable (lo que uno pierde, el otro gana), evitando que el
# algoritmo derive hacia configuraciones muy desbalanceadas.
#
# La copia profunda `[list(r) for r in rutas]` es indispensable.
# Python pasa listas por referencia, no por valor. Sin esta copia,
# modificar rutas_vecinas también modificaría `actual` en el
# algoritmo principal, y el Recocido Simulado no podría comparar
# el estado anterior con el vecino generado.
#
# El while `r1 == r2 and idx1 == idx2` evita el caso degenerado
# donde se "intercambia" un nodo consigo mismo, lo que produciría
# un vecino idéntico a la solución actual y desperdiciaría una
# iteración sin explorar nada nuevo.
#
# El caso especial cuando rutas_vecinas[r1] está vacío permite
# mover (no intercambiar) una tienda de r2 a r1, asegurando que
# ningún CD quede permanentemente sin tiendas por azar durante
# la exploración.
# ------------------------------------------------------------
def generar_vecino(rutas):
    rutas_vecinas = [list(r) for r in rutas]
    m = len(rutas_vecinas)

    r1 = random.randint(0, m - 1)
    posibles = [i for i in range(m) if len(rutas_vecinas[i]) > 0 and i != r1]

    if not posibles:
        return rutas_vecinas

    r2 = random.choice(posibles)

    if len(rutas_vecinas[r1]) == 0:
        nodo = rutas_vecinas[r2].pop(random.randint(0, len(rutas_vecinas[r2]) - 1))
        rutas_vecinas[r1].append(nodo)
        return rutas_vecinas

    idx1 = random.randint(0, len(rutas_vecinas[r1]) - 1)
    idx2 = random.randint(0, len(rutas_vecinas[r2]) - 1)

    while r1 == r2 and idx1 == idx2:
        idx2 = random.randint(0, len(rutas_vecinas[r2]) - 1)

    rutas_vecinas[r1][idx1], rutas_vecinas[r2][idx2] = rutas_vecinas[r2][idx2], rutas_vecinas[r1][idx1]
    return rutas_vecinas

# ------------------------------------------------------------
# FUNCIÓN 5: optimizacion_recocido_simulado
#
# Núcleo del algoritmo inspirado en el proceso físico de recocido
# de metales (Kirkpatrick et al., 1983): un metal enfriado lentamente
# encuentra configuraciones de mínima energía porque a alta temperatura
# los átomos tienen libertad de moverse, y al bajar la temperatura
# se estabilizan en posiciones óptimas.
#
# Aquí la "temperatura" controla la probabilidad de aceptar soluciones
# peores que la actual. El criterio de Metropolis formaliza esto:
#   P(aceptar) = exp(-delta / T)
# Cuando T es alta, exp tiende a 1 y casi cualquier vecino se acepta
# (exploración amplia). Cuando T es baja, exp tiende a 0 y solo se
# aceptan mejoras (explotación del mejor vecindario encontrado).
# Esto permite escapar de óptimos locales, a diferencia de un greedy
# puro que quedaría atrapado en el primer mínimo que encuentre.
#
# Parámetros utilizados:
#   t0=1000, factor_enfriamiento=0.99, iteraciones=1000, tf=1e-6
# Con estos valores el algoritmo ejecuta aproximadamente 2,000,000
# de evaluaciones de vecinos, suficiente para converger en una red
# de 100 nodos como la de este proyecto.
#
# Estructura de dos bucles:
#   - Bucle externo: controla el descenso de temperatura.
#   - Bucle interno: explora `iteraciones` vecinos a T constante
#     antes de enfriar. Esto da al algoritmo tiempo para explorar
#     el vecindario de cada nivel de temperatura antes de restringirse.
#
# Sobre las copias profundas:
#   `mejor = [list(r) for r in actual]` es crítico al guardar la
#   mejor solución. Sin esta copia, `mejor` y `actual` apuntarían
#   al mismo objeto en memoria, y `mejor` se sobreescribiría en cada
#   iteración perdiendo la mejor solución encontrada.
#
# historial_costos[0] se usa como referencia base en historial_mejora
# porque representa el costo de la solución inicial (greedy), que es
# el punto de partida natural para medir el porcentaje de mejora.
# ------------------------------------------------------------
def optimizacion_recocido_simulado(df_tiendas, matriz_distancias, matriz_combustible,
                                    t0, factor_enfriamiento, iteraciones, tf):
    actual = solucion_inicial(df_tiendas, matriz_distancias)
    actual_costo, actual_distancia, actual_gasolina = costo_total(actual, matriz_distancias, matriz_combustible)

    mejor = [list(r) for r in actual]
    mejor_costo     = actual_costo
    mejor_distancia = actual_distancia
    mejor_gasolina  = actual_gasolina

    historial_costos      = []
    historial_distancias  = []
    historial_gasolinas   = []
    historial_mejora      = []

    t = t0

    while t > tf:
        for _ in range(iteraciones):
            vecino = generar_vecino(actual)
            vecino_costo, vecino_distancia, vecino_gasolina = costo_total(vecino, matriz_distancias, matriz_combustible)
            delta = vecino_costo - actual_costo

            if delta < 0 or random.random() < math.exp(-delta / t):
                actual          = vecino
                actual_costo    = vecino_costo
                actual_distancia = vecino_distancia
                actual_gasolina  = vecino_gasolina

            if actual_costo < mejor_costo:
                mejor           = [list(r) for r in actual]
                mejor_costo     = actual_costo
                mejor_distancia = actual_distancia
                mejor_gasolina  = actual_gasolina

            historial_costos.append(actual_costo)
            historial_distancias.append(actual_distancia)
            historial_gasolinas.append(actual_gasolina)
            historial_mejora.append(
                ((historial_costos[0] - mejor_costo) / historial_costos[0]) * 100
            )

        t *= factor_enfriamiento

    return mejor, mejor_costo, mejor_distancia, mejor_gasolina, historial_costos, historial_distancias, historial_gasolinas, historial_mejora