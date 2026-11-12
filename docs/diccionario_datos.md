# Diccionario de datos

## Dataset original (UCI Online Retail)
| Variable | Tipo | Descripción |
|---|---|---|
| InvoiceNo | Categórica | Nº de factura (6 dígitos); prefijo `C` = cancelación |
| StockCode | Categórica | Código de producto (5 dígitos) |
| Description | Texto | Nombre del producto |
| Quantity | Entero | Unidades por transacción |
| InvoiceDate | Fecha | Fecha y hora de la transacción |
| UnitPrice | Continua (£) | Precio unitario |
| CustomerID | Categórica | Código de cliente (5 dígitos) |
| Country | Texto | País del cliente |

## Variables derivadas (`clientes_rfm.csv`, `clientes_segmentados.csv`)
| Variable | Descripción |
|---|---|
| Recency | Días desde la última compra hasta la fecha de referencia |
| Frequency | Facturas distintas del cliente |
| Monetary | Gasto total (£) = Σ Quantity × UnitPrice |
| AvgTicket | Monetary / Frequency |
| UniqueProducts | Productos (StockCode) distintos |
| TotalQuantity, AvgItemsPerInvoice | Unidades totales y por factura |
| TenureDays | Días entre primera y última compra |
| CancelledInvoices, ReturnRate | Facturas canceladas y su proporción |
| Country | País más frecuente |
| Segmento, NombreSegmento | Segmento asignado por el modelo final (-1 = ruido) |
| PC1, PC2 | Coordenadas PCA para visualización |
