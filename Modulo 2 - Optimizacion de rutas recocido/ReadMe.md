## Librerias a instalar (una por una) para ejecutar el proyecto desde la raíz del proyecto
## puede ser que no funcione con pip y sea con pip3
```
pip install pandas
```
```
pip install numpy
```
```
pip install matplotlib
```
```
pip install folium
```

## Version de python requerida
python 3.10 o superior

## Como ejecutar el proyecto
Ejecutar main.py desde la raíz del proyecto (Proyecto-IA-Recocido/)
**No desde dentro de src/** 

## Estructura del proyecto
Proyecto-IA-Recocido/
├── Data/
│   ├── datos_distribucion_tiendas.csv     ← nodos con coordenadas GPS
│   ├── matriz_distancias.csv              ← distancias Haversine en km (100x100)
│   ├── matriz_costos_combustible.csv      ← costo combustible = distancia x 0.15
│   ├── asignacion_cd_tiendas.csv          ← SOLO INFORMATIVO, no se importa en el código
│   └── mapa_asignacion_culiacan.html      ← visualización del estado inicial
└── src/
    ├── recocido_simulado.py               ← funciones del algoritmo
    └── main.py                            ← punto de entrada

## Archivos generados al ejecutar
mapa_rutas_optimizadas.html   ← se genera en la raíz del proyecto

## Nota sobre las matrices
Las matrices fueron regeneradas desde las coordenadas GPS reales usando
la fórmula de Haversine. NO usar las matrices originales del xlsx —
esas no correspondían a las coordenadas del CSV.

## Nota sobre la asignacion 
asignacion_cd_tiendas.csv es un archivo de referencia que muestra qué
tiendas pertenecen a cada Centro de Distribución. La asignación está
balanceada entre 8 y 10 tiendas por CD. Este archivo no se carga en
ningún punto del código.

## Ejecución del programa
Para ejecutar el programa desde la raíz del proyecto (Proyecto-IA-Recocido/):
```
python src/main.py
```
O con el boton de ejecucion de vsc, va a tardar un poco en cargar los datos y luego se ejecuta, esto va a tardar un poco en cargar y luego en generar el mapa y las graficas que saldran y podras abrirlo directamente al darle click. 
la imagen esta adjunta en la carpeta llamada imagenes

## Nota sobre el mapa
El mapa se genera en la raíz del proyecto (Proyecto-IA-Recocido/) y no en src/ para que sea accesible directamente sin navegar subcarpetas - para verlo en el navegador se hace con una extension de vsc
por ejemplo podria usar live server para verlo en el navegador, en el archiv que se creo le das click derecho y abre con live server automaitcamente se va a abrir en el navegador que tengas predetermiando.