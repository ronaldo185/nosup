"""Diccionario de datos: variables originales y derivadas."""
ORIGINAL = [
    ("InvoiceNo", "Identificador", "Nº de factura de 6 dígitos; si empieza con 'C' es una cancelación"),
    ("StockCode", "Identificador", "Código de producto de 5 dígitos (único por producto)"),
    ("Description", "Texto", "Nombre del producto"),
    ("Quantity", "Entero", "Unidades del producto por transacción (negativa en cancelaciones)"),
    ("InvoiceDate", "Fecha y hora", "Momento en que se generó la transacción"),
    ("UnitPrice", "Continua (£)", "Precio por unidad en libras esterlinas"),
    ("CustomerID", "Identificador", "Código de cliente de 5 dígitos (nulo en ~25 % de las filas)"),
    ("Country", "Texto", "País de residencia del cliente"),
]
DERIVADAS = [
    ("TotalPrice", "Continua (£)", "Quantity × UnitPrice (importe de la línea)", False),
    ("Recency", "Entero (días)", "Días desde la última compra hasta la fecha de referencia", True),
    ("Frequency", "Entero", "Nº de facturas distintas del cliente", True),
    ("Monetary", "Continua (£)", "Gasto total del cliente", True),
    ("AvgTicket", "Continua (£)", "Monetary / Frequency: gasto medio por factura", True),
    ("UniqueProducts", "Entero", "Nº de productos distintos comprados", True),
    ("TotalQuantity", "Entero", "Unidades totales compradas", False),
    ("AvgItemsPerInvoice", "Continua", "Unidades promedio por factura", False),
    ("TenureDays", "Entero (días)", "Días entre su primera y su última compra", False),
    ("CancelledInvoices", "Entero", "Nº de facturas canceladas", False),
    ("ReturnRate", "Proporción 0-1", "Canceladas / (compras + canceladas)", False),
    ("Segmento / NombreSegmento", "Categórica", "Grupo asignado por el modelo final (-1 = ruido)", False),
    ("PC1, PC2", "Continua", "Coordenadas PCA (solo para visualizar)", False),
]
