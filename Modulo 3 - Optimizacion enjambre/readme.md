# Optimización de Riego con Enjambre de Partículas (PSO)

Proyecto de la materia **Tópicos de Inteligencia Artificial** — Instituto Tecnológico de Culiacán  
**Integrantes:** Denzel Arturo Gutiérrez Chávez · Juan Carlos Quiñonez Madrid

Implementación del algoritmo bio-inspirado **Particle Swarm Optimization (PSO)** para determinar la ubicación óptima de 5 sensores de humedad en un campo agrícola del municipio de Guasave, Sinaloa, con el objetivo de maximizar la eficiencia del sistema de riego.

---

## Librerías a instalar (una por una)
> Si `pip` no funciona, usa `pip3`

```
pip install pandas
```
```
pip install numpy
```
```
pip install scikit-learn
```
```
pip install scipy
```
```
pip install pyswarms
```
```
pip install matplotlib
```
```
pip install seaborn
```

## Versión de Python requerida
Python 3.10 o superior

---

## Estructura del proyecto

```
Modulo 3 - Optimizacion enjambre/
├── data/
│   └── datos_cultivos_guasave.csv   ← 100 puntos del campo con coordenadas GPS y variables ambientales
└── ProyectoModulo3.ipynb            ← notebook principal con todo el algoritmo
```

> **Importante:** el CSV debe estar dentro de la carpeta `data/` para que la ruta del notebook funcione correctamente.

---

## Cómo ejecutar el proyecto

Abrir `ProyectoModulo3.ipynb` en Jupyter Notebook o VS Code y ejecutar todas las celdas en orden (**Run All**).

Desde terminal:
```
jupyter notebook ProyectoModulo3.ipynb
```

El notebook ejecuta automáticamente el pipeline completo:
1. Carga y preprocesamiento del CSV (One-Hot Encoding + MinMaxScaler)
2. Configuración del enjambre (50 partículas, 100 iteraciones)
3. Optimización PSO y búsqueda de las 5 posiciones óptimas
4. Visualización del mapa de colocación de sensores
5. Gráfica de convergencia del algoritmo

---

## Parámetros del algoritmo

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `N_SENSORES` | 5 | Sensores a posicionar |
| `N_PARTICULAS` | 50 | Tamaño del enjambre |
| `ITERACIONES` | 100 | Iteraciones de búsqueda |
| `c1` | 0.5 | Componente cognitiva |
| `c2` | 0.3 | Componente social |
| `w` | 0.9 | Inercia |

---

## Resultados obtenidos

El algoritmo alcanzó un **costo mínimo de 71.1473** (suma de distancias al cuadrado entre los 100 puntos del campo y su sensor más cercano).

| Sensor | Latitud | Longitud | Humedad (%) | Salinidad (dS/m) | Temperatura (°C) |
|--------|---------|----------|-------------|------------------|------------------|
| S1 | 25.5851 | -108.4516 | 40.48 | 2.58 | 29.88 |
| S2 | 25.5519 | -108.4605 | 29.27 | 2.08 | 31.76 |
| S3 | 25.5629 | -108.4681 | 18.38 | 1.31 | 30.82 |
| S4 | 25.5784 | -108.5036 | 23.75 | 1.41 | 32.44 |
| S5 | 25.5867 | -108.4726 | 23.90 | 2.18 | 27.07 |