"""
scripts/export_sample.py
─────────────────────────────────────────────────────────────────────────────
Exporta muestras representativas de cada tabla del Data Warehouse a archivos
CSV en data/sample/ para usar en modo demo sin conexión a MySQL.
Tamaño total objetivo: < 5 MB.

Uso:
    python scripts/export_sample.py

Requiere las variables de entorno configuradas en .env
"""

import pathlib
import sys

# Agregar raíz del proyecto al path
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import pandas as pd
from sqlalchemy import text
from src.db import get_engine_dw, get_engine_oltp, test_connection

SAMPLE_DIR = pathlib.Path(__file__).parent.parent / "data" / "sample"
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

# Límites de filas por tabla (para mantener < 5 MB total)
EXPORTACIONES_DW = {
    "fact_precio":          "SELECT * FROM fact_precio          LIMIT 2000",
    "dim_producto":         "SELECT * FROM dim_producto         LIMIT 3265",
    "dim_establecimiento":  "SELECT * FROM dim_establecimiento  LIMIT 51",
    "dim_tiempo":           "SELECT * FROM dim_tiempo           LIMIT 500",
    "agg_precio_mensual":   "SELECT * FROM agg_precio_mensual   LIMIT 5000",
}

EXPORTACIONES_OLTP = {
    "stg_qqp":              "SELECT * FROM stg_qqp              LIMIT 500",
    "registro_precio":      "SELECT * FROM registro_precio      LIMIT 500",
    "producto":             "SELECT * FROM producto             LIMIT 781",
    "presentacion_producto":"SELECT * FROM presentacion_producto LIMIT 500",
    "establecimiento":      "SELECT * FROM establecimiento      LIMIT 51",
}

def exportar(engine, consultas: dict, etiqueta: str):
    for tabla, sql in consultas.items():
        print(f"  Exportando {etiqueta}.{tabla}…", end=" ")
        try:
            with engine.connect() as conn:
                df = pd.read_sql(text(sql), conn)
            ruta = SAMPLE_DIR / f"{tabla}.csv"
            df.to_csv(ruta, index=False, encoding="utf-8")
            print(f"OK — {len(df)} filas — {ruta.stat().st_size / 1024:.1f} KB")
        except Exception as e:
            print(f"ERROR: {e}")


def main():
    ok, msg = test_connection()
    if not ok:
        print(f"❌ No se puede conectar a MySQL: {msg}")
        sys.exit(1)

    print(f"✅ Conectado: {msg}")
    print(f"📂 Destino: {SAMPLE_DIR}\n")

    print("── Data Warehouse (qqp_dw) ──────────────────────────")
    exportar(get_engine_dw(), EXPORTACIONES_DW, "dw")

    print("\n── OLTP (qqp_oltp) ──────────────────────────────────")
    exportar(get_engine_oltp(), EXPORTACIONES_OLTP, "oltp")

    # Calcular tamaño total
    total_kb = sum(f.stat().st_size for f in SAMPLE_DIR.glob("*.csv")) / 1024
    print(f"\n✅ Exportación completa. Tamaño total: {total_kb:.1f} KB")


if __name__ == "__main__":
    main()
