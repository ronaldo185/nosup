# Resultados

*Documento generado automáticamente por el pipeline.*

- Periodo: 2010-12-01 → 2011-12-09
- Clientes segmentados: **4,334**
- Ingresos analizados: **£8,737,228**
- Modelo final: **K-Means** `{'k': 4}`
- Silhouette: 0.237 · Davies-Bouldin: 1.300 · Estabilidad (ARI): 0.907

## Comparación de algoritmos

           modelo                                  parametros  n_clusters  ruido_pct  silhouette  davies_bouldin  calinski_harabasz  estabilidad_ari  elegible  ranking_compuesto
          K-Means                                    {'k': 4}           4       0.00       0.237           1.300           2014.979            0.907      True               1.75
Jerárquico (Ward)                                    {'k': 5}           5       0.00       0.167           1.430           1348.589            0.337      True               2.75
              GMM                                    {'k': 6}           6       0.00       0.065           2.996            735.325            0.988      True               3.00
           DBSCAN              {'eps': 0.6, 'min_samples': 5}           6       7.25       0.087           0.905            364.922            0.950      True               2.50
          HDBSCAN {'min_cluster_size': 20, 'min_samples': 20}           2      20.58       0.283           1.228           1781.144            0.937     False                NaN

## Segmentos

### Campeones (segmento 0)
- 860 clientes (19.8%), 71.2% de ingresos
- Mediana: recencia 11 d, frecuencia 8, gasto £3,443
- Acción: Programa VIP, acceso anticipado a novedades y pedidos personalizados. Proteger la relación: son la base de ingresos.

### Clientes leales (segmento 1)
- 1,216 clientes (28.1%), 13.1% de ingresos
- Mediana: recencia 23 d, frecuencia 3, gasto £848
- Acción: Venta cruzada, programa de puntos y descuentos por volumen para aumentar el ticket medio.

### Compradores únicos de alto ticket (segmento 2)
- 1,178 clientes (27.2%), 13.3% de ingresos
- Mediana: recencia 116 d, frecuencia 1, gasto £600
- Acción: Compraron una sola vez un pedido grande y no volvieron: contacto comercial directo, oferta de recompra y revisión de su experiencia.

### Perdidos / inactivos (segmento 3)
- 1,080 clientes (24.9%), 2.5% de ingresos
- Mediana: recencia 144 d, frecuencia 1, gasto £176
- Acción: Campaña de bajo costo de 'te extrañamos'; no invertir en retención intensiva.
