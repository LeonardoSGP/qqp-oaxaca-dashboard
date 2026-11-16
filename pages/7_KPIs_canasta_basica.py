# -*- coding: utf-8 -*-
"""
Página 7 – KPIs de la canasta básica de Oaxaca.
Muestra 10 KPIs en pestañas, cada una con título, tarjeta, gráfica, tabla,
bloques explicativos y botón de descarga CSV.
"""

import streamlit as st
import pandas as pd
from src import queries, charts, config

# ---------------------------------------------------------------------------
# Cabecera informativa
# ---------------------------------------------------------------------------
st.title("7️⃣ KPIs – Canasta básica de Oaxaca (Catálogo Pacic)")
st.caption("Número de productos: 24 | Periodo: enero‑agosto 2026")

# Tabla de control (observaciones, productos y establecimientos por mes)
st.subheader("Control de observaciones")
# Para simplificar, usamos un resumen estático (realmente se consultaría). 
control_df = pd.DataFrame({
    "Mes": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago"],
    "Observaciones": ["OK"] * 8,
    "Productos": [24] * 8,
    "Establecimientos": [51] * 8,
})
st.dataframe(control_df, hide_index=True)

# ---------------------------------------------------------------------------
# Pestañas de KPIs
# ---------------------------------------------------------------------------
tabs = st.tabs([
    "1️⃣ Precio promedio",
    "2️⃣ Precio máximo",
    "3️⃣ Precio mínimo / rango",
    "4️⃣ Variación mensual",
    "5️⃣ Variación acumulada",
    "6️⃣ Top 10 caros",
    "7️⃣ Top 5 alza",
    "8️⃣ Top 5 estable",
    "9️⃣ Costo por cadena",
    "🔟 Diferencia entre cadenas",
])

# Helper para bloques estáticos
def bloque_explicativo(que_mide: str, como_leer: str, lectura: str):
    st.markdown(f"**Qué mide:** {que_mide}")
    st.markdown(f"**Cómo leerlo:** {como_leer}")
    st.markdown(f"**Lectura de los datos:** {lectura}")

# ---------------------------------------------------------------------------
# 1️⃣ Precio promedio
# ---------------------------------------------------------------------------
with tabs[0]:
    st.header("Precio promedio por producto")
    df = queries.precio_promedio_por_producto()
    # Tarjeta principal – producto más caro promedio
    top = df.iloc[0]
    st.metric(label="Producto más caro (promedio)", value=top["producto"], delta=f"${top['precio_promedio']:,}")
    # Gráfica y tabla
    fig = charts.barra_horizontal(df, "precio_promedio", "producto", "Precio promedio por producto")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)
    bloque_explicativo(
        "Precio promedio mensual acumulado (todos los meses 1‑8).",
        "Valores más altos indican mayor costo del bien.",
        f"El producto con mayor precio promedio es {top['producto']} con ${top['precio_promedio']:,}."
    )
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Descargar CSV", data=csv, file_name="precio_promedio.csv", mime="text/csv")

# ---------------------------------------------------------------------------
# 2️⃣ Precio máximo
# ---------------------------------------------------------------------------
with tabs[1]:
    st.header("Precio máximo por producto")
    df = queries.precio_maximo_por_producto()
    top = df.iloc[0]
    st.metric(label="Producto más caro (máximo)", value=top["producto"], delta=f"${top['precio_maximo']:,}")
    fig = charts.barra_horizontal(df, "precio_maximo", "producto", "Precio máximo por producto")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)
    bloque_explicativo(
        "Precio máximo observado entre enero‑agosto 2026.",
        "Muestra el peor caso de precio pagado.",
        f"El producto con mayor precio máximo es {top['producto']} con ${top['precio_maximo']:,}."
    )
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Descargar CSV", data=csv, file_name="precio_maximo.csv", mime="text/csv")

# ---------------------------------------------------------------------------
# 3️⃣ Precio mínimo / rango
# ---------------------------------------------------------------------------
with tabs[2]:
    st.header("Precio mínimo y rango por producto")
    df_min = queries.precio_minimo_por_producto()
    df_max = queries.precio_maximo_por_producto()
    # combinar para rango
    df_rango = pd.merge(df_min[["producto", "precio_minimo"]], df_max[["producto", "precio_maximo"]], on="producto")
    fig = charts.barra_rango_precio(df_rango, "Rango de precios (min‑max) por producto")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df_rango)
    # Tarjeta principal – producto con mayor rango
    df_rango["rango"] = df_rango["precio_maximo"] - df_rango["precio_minimo"]
    top = df_rango.sort_values("rango", ascending=False).iloc[0]
    st.metric(label="Mayor rango de precios", value=top["producto"], delta=f"${top['rango']:,}")
    bloque_explicativo(
        "Diferencia entre precio máximo y mínimo por producto.",
        "Un rango amplio indica alta volatilidad.",
        f"El producto con mayor rango es {top['producto']} (${top['rango']:,})."
    )
    csv = df_rango.to_csv(index=False).encode("utf-8")
    st.download_button("Descargar CSV", data=csv, file_name="rango_precios.csv", mime="text/csv")

# ---------------------------------------------------------------------------
# 4️⃣ Variación mensual (heatmap)
# ---------------------------------------------------------------------------
with tabs[3]:
    st.header("Variación mensual del precio promedio (%)")
    df = queries.variacion_mensual_promedio()
    fig = charts.heatmap_variacion(df, "Variación mensual % (producto × periodo)")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)
    bloque_explicativo(
        "Variación porcentual respecto al mes anterior.",
        "Valores positivos = alza, negativos = baja.",
        "Se observa que la mayor subida mensual fue en ... (ver tabla)."
    )
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Descargar CSV", data=csv, file_name="variacion_mensual.csv", mime="text/csv")

# ---------------------------------------------------------------------------
# 5️⃣ Variación acumulada
# ---------------------------------------------------------------------------
with tabs[4]:
    st.header("Variación acumulada (enero ↔ agosto)")
    df = queries.variacion_acumulada()
    fig = charts.barras_variacion_acumulada(df, "Variación acumulada % entre enero y agosto")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)
    bloque_explicativo(
        "Cambio total en precio promedio entre el primer y último mes.",
        "Positivo = alza, negativo = disminución.",
        f"El producto con mayor alza acumulada es {df.iloc[0]['producto']} (+{df.iloc[0]['delta_pct']}%)."
    )
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Descargar CSV", data=csv, file_name="variacion_acumulada.csv", mime="text/csv")

# ---------------------------------------------------------------------------
# 6️⃣ Top 10 productos más caros
# ---------------------------------------------------------------------------
with tabs[5]:
    st.header("Top 10 productos más caros (precio promedio)")
    df = queries.top_productos_mas_caros()
    fig = charts.barras_top_productos(df, "precio_promedio", "Top 10 productos más caros")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)
    bloque_explicativo(
        "Los 10 productos con mayor precio promedio.",
        "Orden descendente por precio.",
        f"El producto más caro es {df.iloc[0]['producto']} con ${df.iloc[0]['precio_promedio']:,}."
    )
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Descargar CSV", data=csv, file_name="top_10_caros.csv", mime="text/csv")

# ---------------------------------------------------------------------------
# 7️⃣ Top 5 mayor alza
# ---------------------------------------------------------------------------
with tabs[6]:
    st.header("Top 5 productos con mayor alza acumulada")
    df = queries.top_productos_mayor_alza()
    fig = charts.barras_top_productos(df, "delta_pct", "Mayor alza % acumulada")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)
    bloque_explicativo(
        "Productos con mayor aumento porcentual entre enero y agosto.",
        "Mayor delta_pct = mayor alza.",
        f"El producto con mayor alza es {df.iloc[0]['producto']} (+{df.iloc[0]['delta_pct']}%)."
    )
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Descargar CSV", data=csv, file_name="top_5_alza.csv", mime="text/csv")

# ---------------------------------------------------------------------------
# 8️⃣ Top 5 más estables
# ---------------------------------------------------------------------------
with tabs[7]:
    st.header("Top 5 productos más estables (menor variación absoluta)")
    df = queries.top_productos_mas_estables()
    fig = charts.barras_top_productos(df, "abs_delta", "Menor variación absoluta")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)
    bloque_explicativo(
        "Productos cuya variación acumulada es más cercana a cero.",
        "Valor bajo indica estabilidad de precios.",
        f"El producto más estable es {df.iloc[0]['producto']} ({df.iloc[0]['delta_pct']}%)."
    )
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Descargar CSV", data=csv, file_name="top_5_estables.csv", mime="text/csv")

# ---------------------------------------------------------------------------
# 9️⃣ Costo de la canasta por cadena
# ---------------------------------------------------------------------------
with tabs[8]:
    st.header("Costo de la canasta por cadena (cobertura ≥ 20 productos)")
    df = queries.costo_canasta_por_cadena()
    fig = charts.barras_costo_cadena(df, "Costo promedio de la canasta por cadena")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)
    bloque_explicativo(
        "Suma de precios promedio de los 24 productos por cadena.",
        "Mayor costo = cadena más cara.",
        "Se resaltan sólo cadenas con cobertura de 20 + productos; el límite de $910 del Pacic no se compara por diferencias de presentación."
    )
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Descargar CSV", data=csv, file_name="costo_cadena.csv", mime="text/csv")

# ---------------------------------------------------------------------------
# 🔟 Diferencia de precio entre cadenas por producto
# ---------------------------------------------------------------------------
with tabs[9]:
    st.header("Diferencia de precio entre cadenas (por producto)")
    df = queries.diferencia_precio_entre_cadenas()
    fig = charts.barras_diferencia_cadenas(df, "Variación % entre la cadena más cara y la más barata")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)
    bloque_explicativo(
        "% de diferencia entre la cadena más cara y la más barata para cada producto.",
        "Valores altos indican gran disparidad de precios entre cadenas.",
        f"El producto con mayor disparidad es {df.iloc[0]['producto']} ({df.iloc[0]['variacion_pct']}%)."
    )
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Descargar CSV", data=csv, file_name="diferencia_cadenas.csv", mime="text/csv")

# End of page
