ARCHIVO main.py — Punto de entrada del programa

═══════════════════════════════════════════════════════
SECCIÓN 1 — IMPORTS Y RUTAS
═══════════════════════════════════════════════════════

Importar librerías: pandas, numpy, random, time, folium, matplotlib, pathlib
Importar desde recocido_simulado las 5 funciones

BASE ← carpeta padre de src/ (sube dos niveles desde __file__)

ruta_nodos       ← BASE / "Data" / "datos_distribucion_tiendas.csv"
ruta_distancias  ← BASE / "Data" / "matriz_distancias.csv"
ruta_combustible ← BASE / "Data" / "matriz_costos_combustible.csv"

═══════════════════════════════════════════════════════
SECCIÓN 2 — CARGA DE DATOS
═══════════════════════════════════════════════════════

df_tiendas        ← pd.read_csv(ruta_nodos)
df_distancias     ← pd.read_csv(ruta_distancias)
df_combustible    ← pd.read_csv(ruta_combustible)

matriz_distancias  ← df_distancias.to_numpy()
matriz_combustible ← df_combustible.to_numpy()

═══════════════════════════════════════════════════════
SECCIÓN 3 — SOLUCIÓN INICIAL
═══════════════════════════════════════════════════════

rutas_inicial ← solucion_inicial(df_tiendas, matriz_distancias)
(costo_ini, distancia_ini, gasolina_ini) ← costo_total(rutas_inicial, ...)

Imprimir:
    "=== SOLUCIÓN INICIAL ==="
    costo ponderado, distancia total, gasolina total

PARA cada (i, ruta) en enumerate(rutas_inicial):
    (costo_r, dist_r, gas_r) ← costo_ruta(ruta, i, ...)
    Imprimir: Ruta i → nodos → costo, distancia, gasolina

═══════════════════════════════════════════════════════
SECCIÓN 4 — EJECUCIÓN DEL RECOCIDO SIMULADO
═══════════════════════════════════════════════════════

Imprimir "=== OPTIMIZANDO ==="
inicio ← time.time()

(mejor_rutas, mejor_costo, mejor_dist, mejor_gas,
 hist_costos, hist_dist, hist_gas, hist_mejora) ←
    optimizacion_recocido_simulado(
        df_tiendas, matriz_distancias, matriz_combustible,
        t0=1000, factor_enfriamiento=0.99,
        iteraciones=1000, tf=1e-6
    )

fin ← time.time()
tiempo_total ← fin - inicio

═══════════════════════════════════════════════════════
SECCIÓN 5 — RESULTADOS Y COMPARACIÓN
═══════════════════════════════════════════════════════

Imprimir:
    "=== SOLUCIÓN OPTIMIZADA ==="
    tiempo de ejecución
    costo ponderado, distancia total, gasolina total

PARA cada (i, ruta) en enumerate(mejor_rutas):
    (costo_r, dist_r, gas_r) ← costo_ruta(ruta, i, ...)
    Imprimir: Ruta i → nodos → costo, distancia, gasolina

Imprimir:
    "=== COMPARACIÓN ==="
    mejora en costo     → valor absoluto y porcentaje
    mejora en distancia → valor absoluto y porcentaje
    mejora en gasolina  → valor absoluto y porcentaje

═══════════════════════════════════════════════════════
SECCIÓN 6 — MAPA FOLIUM
═══════════════════════════════════════════════════════

lat_media, lon_media ← promedio de coordenadas de df_tiendas
mapa ← folium.Map(location=[lat_media, lon_media], zoom_start=12)
coords ← columnas Latitud_WGS84 y Longitud_WGS84 de df_tiendas como numpy

PARA cada CD en df_tiendas donde Tipo == "Centro de Distribución":
    Agregar marcador rojo con ícono "home" en su coordenada

PARA cada tienda en df_tiendas donde Tipo == "Tienda":
    Agregar marcador azul con ícono "shopping-cart" en su coordenada

colores ← lista de 10 colores hex, uno por CD

PARA cada (id_cedis, ruta) en enumerate(mejor_rutas):
    puntos ← [coord_CD] + [coord de cada tienda en ruta] + [coord_CD]
    Agregar PolyLine con el color de ese CD

mapa.save(BASE / "mapa_rutas_optimizadas.html")
Imprimir "Mapa generado"

═══════════════════════════════════════════════════════
SECCIÓN 7 — GRÁFICAS MATPLOTLIB
═══════════════════════════════════════════════════════

Crear figura con 4 subplots (2 filas × 2 columnas)
Título general: "Evolución del Recocido Simulado"

Subplot [0,0] → hist_costos     → color azul   → "Costo Ponderado Total"
Subplot [0,1] → hist_dist       → color naranja → "Distancia Total"
Subplot [1,0] → hist_gas        → color verde   → "Consumo de Gasolina"
Subplot [1,1] → hist_mejora     → color morado  → "Mejora respecto al inicio (%)"

Cada subplot tiene: título, etiqueta X "Iteraciones", etiqueta Y, grid

plt.tight_layout()
plt.show()