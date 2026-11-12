# Sistema Inteligente de Segmentación de Clientes

Segmentación de clientes con Machine Learning no supervisado sobre **UCI Online Retail**: limpieza trazable, RFM, comparación de 5 algoritmos (K-Means, Jerárquico, GMM, DBSCAN, HDBSCAN), perfiles de negocio, dashboard web, bitácora y reportes PDF.

## Inicio rápido
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run_pipeline.py             # opcional: ya se incluyen resultados (≈1,5 min)
streamlit run dashboard/app.py     # abre http://localhost:8501 en el navegador
```
Atajo: `./iniciar_dashboard.sh` (Linux/macOS) o `iniciar_dashboard.bat` (Windows).

## Dashboard (10 vistas, barra lateral fija)
Resumen · Datos y calidad (limpieza, muestra del dataset, diccionario) · Análisis RFM · Comparación de modelos · Segmentos · **Métodos y conclusiones** (métodos, hallazgos, mejor modelo, cuál conviene, conclusiones, limitaciones) · Explorador de clientes · Clasificador · Reportes y descargas · Bitácora.
Cada gráfico lleva debajo una nota «cómo leerlo» calculada con los resultados reales.

## Estructura
`data/` (raw → interim → processed) · `src/` (código reutilizable) · `notebooks/` · `results/` (figuras, métricas, modelos, logs) · `dashboard/` · `docs/`.

## Bitácora
`results/logs/bitacora.log` (eventos) y `results/logs/ejecuciones.json` (historial con duración por etapa). Se registran también vistas, clasificaciones y descargas del dashboard.

## Notas
- El dataset original en `data/raw/` nunca se modifica.
- Cambiar variables, rangos de k o criterios: `src/config.py`.
- Notebooks: ejecutar desde la carpeta `notebooks/` con el entorno del proyecto.

## Dos diseños del dashboard
- **Oscuro minimalista (por defecto):** `streamlit run dashboard/app.py` → puerto 8501.
- **Claro editorial (títulos serif, acento esmeralda):** `./iniciar_tema_claro.sh` o `iniciar_tema_claro.bat` → puerto 8502.
Puedes abrir ambos a la vez para compararlos. El tema se controla con la variable `DASH_TEMA` (`oscuro` | `claro`) en `dashboard/utils.py`.
