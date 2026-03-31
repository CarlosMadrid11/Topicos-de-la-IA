import pandas as pd
import numpy as np
import random
import time
import folium
import matplotlib.pyplot as plt
from pathlib import Path
from recocido_simulado import (
    solucion_inicial,
    costo_ruta,
    costo_total,
    optimizacion_recocido_simulado
)

# ═══════════════════════════════════════════════════════
# SECCIÓN 1 — RUTAS A LOS ARCHIVOS DE DATOS
#
# Path(__file__).resolve().parent.parent sube dos niveles
# desde src/ hasta la raíz del proyecto (Proyecto-IA-Recocido/).
# Usar Path en lugar de strings evita problemas de separadores
# de ruta entre Windows (\) y Linux/macOS (/), lo que hace
# el proyecto portable sin modificar rutas manualmente.
# ═══════════════════════════════════════════════════════
BASE             = Path(__file__).resolve().parent.parent
ruta_nodos       = BASE / "Data" / "datos_distribucion_tiendas.csv"
ruta_distancias  = BASE / "Data" / "matriz_distancias.csv"
ruta_combustible = BASE / "Data" / "matriz_costos_combustible.csv"

# ═══════════════════════════════════════════════════════
# SECCIÓN 2 — CARGA DE DATOS
#
# df_tiendas se mantiene como DataFrame porque las funciones
# en recocido_simulado.py acceden a columnas por nombre
# (df_tiendas.loc[i, "Tipo"]), lo que no es posible con numpy.
#
# Las matrices sí se convierten a numpy con to_numpy() porque
# el acceso por índice [i][j] dentro de los bucles del algoritmo
# es significativamente más rápido en numpy que en DataFrame.
# Con ~2,000,000 de iteraciones, esta diferencia es relevante.
# ═══════════════════════════════════════════════════════
df_tiendas         = pd.read_csv(ruta_nodos)
df_distancias      = pd.read_csv(ruta_distancias)
df_combustible     = pd.read_csv(ruta_combustible)

matriz_distancias  = df_distancias.to_numpy()
matriz_combustible = df_combustible.to_numpy()


def main():

    # ═══════════════════════════════════════════════════════
    # SECCIÓN 3 — SOLUCIÓN INICIAL
    #
    # Se genera y evalúa la solución greedy antes de optimizar
    # por dos razones: primero, para tener una línea base de
    # comparación al final del programa. Segundo, porque
    # optimizacion_recocido_simulado llama internamente a
    # solucion_inicial, así que imprimir esto aquí no agrega
    # tiempo de cómputo extra.
    #
    # Se imprime el detalle por ruta (no solo el total) para
    # detectar si algún CD quedó con una asignación muy
    # desbalanceada en la solución inicial.
    # ═══════════════════════════════════════════════════════
    rutas_inicial = solucion_inicial(df_tiendas, matriz_distancias)
    costo_ini, distancia_ini, gasolina_ini = costo_total(
        rutas_inicial, matriz_distancias, matriz_combustible
    )

    print("=== SOLUCIÓN INICIAL ===")
    print(f"Costo ponderado: {costo_ini:.4f}")
    print(f"Distancia total: {distancia_ini:.4f}")
    print(f"Gasolina total:  {gasolina_ini:.4f}\n")

    for i, ruta in enumerate(rutas_inicial):
        costo_r, dist_r, gas_r = costo_ruta(ruta, i, matriz_distancias, matriz_combustible)
        print(f"Ruta {i} → nodos: {ruta}")
        print(f"  Costo: {costo_r:.4f} | Distancia: {dist_r:.4f} | Gasolina: {gas_r:.4f}\n")

    # ═══════════════════════════════════════════════════════
    # SECCIÓN 4 — EJECUCIÓN DEL RECOCIDO SIMULADO
    #
    # time.time() envuelve la llamada para medir el tiempo real
    # de ejecución del algoritmo. Con t0=1000, factor=0.99,
    # iteraciones=1000 y tf=1e-6, el algoritmo ejecuta
    # aproximadamente 2,000,000 evaluaciones de vecinos.
    #
    # El desempaquetado en 8 variables es necesario porque
    # optimizacion_recocido_simulado retorna la mejor solución
    # encontrada más los 4 historiales para las gráficas de la
    # Sección 7. No se puede separar esta llamada en dos sin
    # ejecutar el algoritmo dos veces.
    # ═══════════════════════════════════════════════════════
    print("=== OPTIMIZANDO CON RECOCIDO SIMULADO ===")
    inicio = time.time()

    (
        mejor_rutas,
        mejor_costo,
        mejor_dist,
        mejor_gas,
        hist_costos,
        hist_dist,
        hist_gas,
        hist_mejora
    ) = optimizacion_recocido_simulado(
        df_tiendas,
        matriz_distancias,
        matriz_combustible,
        t0=1000,
        factor_enfriamiento=0.99,
        iteraciones=1000,
        tf=1e-6
    )

    fin = time.time()
    tiempo_total = fin - inicio

    # ═══════════════════════════════════════════════════════
    # SECCIÓN 5 — RESULTADOS Y COMPARACIÓN
    #
    # Las mejoras se calculan en valor absoluto y porcentaje
    # para que la comparación sea interpretable: el valor
    # absoluto muestra cuánto se redujo el costo en unidades
    # reales, y el porcentaje permite comparar la eficiencia
    # del algoritmo independientemente de la escala del problema.
    #
    # La guarda condicional (if costo_ini != 0) evita división
    # por cero en el caso hipotético de que la solución inicial
    # tenga costo 0, lo que no ocurre en este problema pero
    # hace el código robusto ante datos atípicos.
    # ═══════════════════════════════════════════════════════
    print("\n=== SOLUCIÓN OPTIMIZADA ===")
    print(f"Tiempo de ejecución: {tiempo_total:.2f} segundos")
    print(f"Costo ponderado: {mejor_costo:.4f}")
    print(f"Distancia total: {mejor_dist:.4f}")
    print(f"Gasolina total:  {mejor_gas:.4f}\n")

    for i, ruta in enumerate(mejor_rutas):
        costo_r, dist_r, gas_r = costo_ruta(ruta, i, matriz_distancias, matriz_combustible)
        print(f"Ruta {i} → nodos: {ruta}")
        print(f"  Costo: {costo_r:.4f} | Distancia: {dist_r:.4f} | Gasolina: {gas_r:.4f}\n")

    mejora_costo_abs = costo_ini - mejor_costo
    mejora_dist_abs  = distancia_ini - mejor_dist
    mejora_gas_abs   = gasolina_ini - mejor_gas

    mejora_costo_pct = (mejora_costo_abs / costo_ini * 100)     if costo_ini     != 0 else 0
    mejora_dist_pct  = (mejora_dist_abs  / distancia_ini * 100) if distancia_ini != 0 else 0
    mejora_gas_pct   = (mejora_gas_abs   / gasolina_ini * 100)  if gasolina_ini  != 0 else 0

    print("=== COMPARACIÓN ===")
    print(f"Mejora en costo     → {mejora_costo_abs:.4f} ({mejora_costo_pct:.2f}%)")
    print(f"Mejora en distancia → {mejora_dist_abs:.4f}  ({mejora_dist_pct:.2f}%)")
    print(f"Mejora en gasolina  → {mejora_gas_abs:.4f}  ({mejora_gas_pct:.2f}%)")

    # ═══════════════════════════════════════════════════════
    # SECCIÓN 6 — MAPA FOLIUM
    #
    # Se usa folium porque genera mapas interactivos en HTML
    # sin necesidad de API keys, a diferencia de Google Maps.
    # El mapa se centra en el promedio de coordenadas de todos
    # los nodos para que queden visibles al cargar el archivo.
    #
    # Los CDs se marcan en rojo con ícono "home" para distinguirlos
    # visualmente de las tiendas (azul, "shopping-cart"). Folium
    # usa íconos de Font Awesome, de ahí el prefix="fa".
    #
    # Cada ruta se dibuja como una PolyLine que recorre:
    # coord_CD → coord_tienda_1 → ... → coord_tienda_n → coord_CD
    # replicando el recorrido físico del vehículo. Los 10 colores
    # hex permiten distinguir las rutas de cada CD sin que se
    # confundan entre sí en el mapa.
    #
    # Se guarda en la raíz del proyecto (BASE) y no en src/ para
    # que sea accesible directamente sin navegar subcarpetas.
    # ═══════════════════════════════════════════════════════
    lat_media = df_tiendas["Latitud_WGS84"].mean()
    lon_media = df_tiendas["Longitud_WGS84"].mean()
    mapa = folium.Map(location=[lat_media, lon_media], zoom_start=12)

    for _, fila in df_tiendas[df_tiendas["Tipo"] == "Centro de Distribución"].iterrows():
        folium.Marker(
            location=[fila["Latitud_WGS84"], fila["Longitud_WGS84"]],
            icon=folium.Icon(color="red", icon="home", prefix="fa"),
            tooltip=f"CD {int(fila.name)}"
        ).add_to(mapa)

    for _, fila in df_tiendas[df_tiendas["Tipo"] == "Tienda"].iterrows():
        folium.Marker(
            location=[fila["Latitud_WGS84"], fila["Longitud_WGS84"]],
            icon=folium.Icon(color="blue", icon="shopping-cart", prefix="fa"),
            tooltip=f"Tienda {int(fila.name)}"
        ).add_to(mapa)

    colores = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
    ]

    cds = df_tiendas[df_tiendas["Tipo"] == "Centro de Distribución"].reset_index(drop=True)
    for id_cedis, ruta in enumerate(mejor_rutas):
        punto_cd = [cds.loc[id_cedis, "Latitud_WGS84"], cds.loc[id_cedis, "Longitud_WGS84"]]
        puntos   = [punto_cd]

        for nodo in ruta:
            fila_tienda = df_tiendas.loc[nodo]
            puntos.append([fila_tienda["Latitud_WGS84"], fila_tienda["Longitud_WGS84"]])

        puntos.append(punto_cd)

        folium.PolyLine(
            puntos,
            color=colores[id_cedis % len(colores)],
            weight=4,
            opacity=0.8,
            tooltip=f"Ruta CD {id_cedis}"
        ).add_to(mapa)

    mapa_path = BASE / "mapa_rutas_optimizadas.html"
    mapa.save(mapa_path)
    print(f"\nMapa generado: {mapa_path}")

    # ═══════════════════════════════════════════════════════
    # SECCIÓN 7 — GRÁFICAS MATPLOTLIB
    #
    # Los 4 subplots muestran la evolución del algoritmo a lo
    # largo de todas las iteraciones, no solo el resultado final.
    # Esto permite observar el comportamiento del Recocido Simulado:
    # al inicio el costo fluctúa ampliamente (temperatura alta,
    # se aceptan soluciones peores), y conforme avanza se estabiliza
    # (temperatura baja, solo se aceptan mejoras).
    #
    # Se grafican distancia y gasolina por separado (no solo el
    # costo ponderado) para verificar que la optimización no
    # sacrifica excesivamente una métrica en favor de la otra.
    #
    # hist_mejora muestra el porcentaje acumulado de mejora respecto
    # a historial_costos[0] (costo inicial), lo que hace visible
    # en qué etapa del algoritmo se obtuvieron las mayores ganancias.
    #
    # rect=[0, 0.03, 1, 0.95] en tight_layout reserva espacio
    # para el título general (fig.suptitle) que de otro modo
    # se superpone con los subplots superiores.
    # ═══════════════════════════════════════════════════════
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Evolución del Recocido Simulado", fontsize=16, fontweight="bold")

    axs[0, 0].plot(hist_costos, color="tab:blue", linewidth=1)
    axs[0, 0].set_title("Costo Ponderado Total")
    axs[0, 0].set_xlabel("Iteraciones")
    axs[0, 0].set_ylabel("Costo")
    axs[0, 0].grid(True)

    axs[0, 1].plot(hist_dist, color="tab:orange", linewidth=1)
    axs[0, 1].set_title("Distancia Total")
    axs[0, 1].set_xlabel("Iteraciones")
    axs[0, 1].set_ylabel("Distancia (km)")
    axs[0, 1].grid(True)

    axs[1, 0].plot(hist_gas, color="tab:green", linewidth=1)
    axs[1, 0].set_title("Consumo de Gasolina")
    axs[1, 0].set_xlabel("Iteraciones")
    axs[1, 0].set_ylabel("Gasolina")
    axs[1, 0].grid(True)

    axs[1, 1].plot(hist_mejora, color="tab:purple", linewidth=1)
    axs[1, 1].set_title("Mejora respecto al inicio (%)")
    axs[1, 1].set_xlabel("Iteraciones")
    axs[1, 1].set_ylabel("% Mejora")
    axs[1, 1].grid(True)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()


if __name__ == "__main__":
    main()