# Metodología

## 1. Datos
UCI Online Retail: 541.909 líneas de factura de un minorista online del Reino Unido (01/12/2010 – 09/12/2011). El archivo original en `data/raw/` **nunca se modifica**.

## 2. Limpieza (`src/preprocessing/limpieza.py`)
| Paso | Justificación |
|---|---|
| Eliminar duplicados exactos | Inflan frecuencia y gasto |
| Eliminar filas sin `CustomerID` | No se puede segmentar sin cliente (≈25 % de filas) |
| Eliminar códigos no-producto (POST, DOT, BANK CHARGES…) | No son compras de producto |
| Separar facturas canceladas (`C…`) | No son ventas; alimentan la **tasa de devolución** |
| Quitar `Quantity ≤ 0` y `UnitPrice ≤ 0` | Ajustes contables |
Cada paso queda registrado en `results/metrics/limpieza_pasos.csv` y en la bitácora.

## 3. Ingeniería de características (`src/features/rfm.py`)
Fecha de referencia = último día del dataset + 1.
- **Recency**: días desde la última compra. **Frequency**: nº de facturas. **Monetary**: gasto total.
- Complementarias: ticket medio, productos distintos, unidades por factura, antigüedad, tasa de devolución, país principal.
- **Variables de clustering**: Recency, Frequency, Monetary, AvgTicket, UniqueProducts → `log1p` (corrige asimetría) → `StandardScaler`.

## 4. Algoritmos (`src/models/`)
| Algoritmo | Parámetros explorados |
|---|---|
| K-Means | k = 2…10 (n_init=20) |
| Jerárquico (Ward) | k = 2…10 |
| GMM (covarianza completa) | k = 2…10, selección por BIC |
| DBSCAN | eps 0.3–1.3 × min_samples {5,10,15,20} |
| HDBSCAN | min_cluster_size {20…150} × min_samples {5,10,20} |

Para modelos con k, se elige k entre **4 y 8** (interpretable para marketing). Con k=2 o 3 el silhouette es mayor, pero la segmentación es demasiado gruesa para actuar.

## 5. Evaluación (`src/evaluation/`)
Silhouette, Davies-Bouldin, Calinski-Harabasz, % de ruido y **estabilidad** (ARI medio entre ajustes en submuestras del 80 %). Se comparan particiones entre modelos con ARI. El modelo final es el de mejor ranking compuesto entre los *elegibles* (4–8 grupos, ≤10 % de ruido).

## 6. Interpretación
Cada segmento se nombra con reglas sobre percentiles de su mediana en R, F, M y ticket, y recibe una acción recomendada (`perfiles.py`). Los IDs se ordenan por gasto mediano descendente.

## 7. Clasificador de clientes nuevos
Un k-NN (k=15) entrenado sobre los segmentos finales permite asignar clientes nuevos, con cualquier algoritmo ganador.

## 8. Limitaciones
Un único minorista, un año de datos, fuerte presencia de mayoristas; métricas internas moderadas (los datos forman un continuo); sin validación externa (no hay etiquetas).
