# -*- coding: utf-8 -*-
"""
Página 7 – KPIs de la canasta básica de Oaxaca.
Muestra 10 KPIs en pestañas, cada una con título, tarjeta, gráfica, tabla,
bloques explicativos y botón de descarga CSV.
"""

import streamlit as st
import pandas as pd
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile
from src import queries, charts
from src.config import PACIC_LIMITE

# ---------------------------------------------------------------------------
# Cabecera informativa
# ---------------------------------------------------------------------------
st.title("KPIs – Canasta básica de Oaxaca (Catálogo Pacic)")
st.caption("Número de productos: 24 | Periodo: enero‑agosto 2026")

st.subheader("Control de observaciones")
with st.spinner("Consultando cobertura mensual…"):
    control_df = queries.control_canasta_mensual()
if control_df.empty:
    st.info("No hay datos de cobertura para el catálogo Pacic en el periodo seleccionado.")
else:
    control_df = control_df.rename(columns={
        "mes": "Mes",
        "observaciones": "Observaciones",
        "productos": "Productos",
        "establecimientos": "Establecimientos",
    })
    st.dataframe(control_df, use_container_width=True, hide_index=True)

st.markdown("---")
st.subheader("Costo mensual de la canasta PACIC")
st.markdown(
    "El PACIC contempla 24 productos esenciales y establece un precio de referencia "
    f"de **${PACIC_LIMITE:,.0f}**. El costo mostrado se calcula sumando el precio "
    "promedio mensual de cada producto disponible."
)

with st.spinner("Calculando el costo mensual de la canasta…"):
    costo_df = queries.costo_canasta_mensual()

if costo_df.empty:
    st.info("No hay datos suficientes para calcular el costo mensual de la canasta.")
else:
    costo_df["estado_limite"] = costo_df["costo_canasta"].apply(
        lambda value: "Dentro del límite" if value <= PACIC_LIMITE else "Sobre el límite"
    )
    primero = costo_df.iloc[0]
    ultimo = costo_df.iloc[-1]
    cambio = float(ultimo["costo_canasta"] - primero["costo_canasta"])
    if abs(cambio) < 0.01:
        tendencia = "se mantuvo estable"
    elif cambio > 0:
        tendencia = "subió"
    else:
        tendencia = "bajó"

    met1, met2, met3 = st.columns(3)
    met1.metric("Costo más reciente", f"${ultimo['costo_canasta']:,.2f}")
    met2.metric("Cambio enero–agosto", f"${cambio:,.2f}")
    met3.metric("Productos cubiertos", f"{int(ultimo['productos_cubiertos'])}/24")

    st.plotly_chart(
        charts.linea_costo_canasta(
            costo_df,
            PACIC_LIMITE,
            "Costo mensual de la canasta vs. límite PACIC",
        ),
        use_container_width=True,
    )
    st.dataframe(
        costo_df.rename(columns={
            "mes": "Mes",
            "productos_cubiertos": "Productos cubiertos",
            "costo_canasta": "Costo de la canasta",
            "diferencia_limite": "Diferencia contra $910",
            "estado_limite": "Estado",
        }),
        use_container_width=True,
        hide_index=True,
    )
    if cambio > 0.01:
        lectura = f"subió ${cambio:,.2f}"
    elif cambio < -0.01:
        lectura = f"bajó ${abs(cambio):,.2f}"
    else:
        lectura = "se mantuvo estable"
    st.info(
        f"**Análisis:** entre {primero['mes']} y {ultimo['mes']}, el costo de la "
        f"canasta {lectura}. El último costo registrado está "
        f"{'por encima' if ultimo['costo_canasta'] > PACIC_LIMITE else 'dentro'} "
        f"del límite de ${PACIC_LIMITE:,.0f}."
    )

# Selector de KPI (compatible con Streamlit 1.67)
kpi = st.radio(
    "Selecciona el KPI que deseas visualizar",
    [
        "Precio promedio",
        "Precio máximo",
        "Precio mínimo / rango",
        "Variación mensual",
        "Variación acumulada",
        "Top 10 productos más caros",
        "Top 5 mayor alza",
        "Top 5 más estables",
        "Costo por cadena",
        "Diferencia entre cadenas",
    ],
)

# Función auxiliar para los bloques estáticos
def bloque_explicativo(que_mide: str, como_leer: str, lectura: str):
    st.markdown(f"**Qué mide:** {que_mide}")
    st.markdown(f"**Cómo leerlo:** {como_leer}")
    st.markdown(f"**Lectura de los datos:** {lectura}")


def exigir_datos(df: pd.DataFrame, mensaje: str) -> None:
    """Evita errores poco claros cuando MySQL no devuelve datos para un KPI."""
    if df.empty:
        st.info(mensaje)
        st.stop()


def mostrar_tabla(df: pd.DataFrame) -> None:
    st.dataframe(df, use_container_width=True, hide_index=True)


def generar_zip_kpis() -> bytes:
    """Genera un ZIP con un CSV independiente para cada uno de los 10 KPIs."""
    df_min = queries.precio_minimo_por_producto()
    df_max = queries.precio_maximo_por_producto()
    df_rango = pd.merge(
        df_min[["producto", "precio_minimo"]],
        df_max[["producto", "precio_maximo"]],
        on="producto",
    )
    df_rango["rango"] = df_rango["precio_maximo"] - df_rango["precio_minimo"]

    archivos = {
        "01_precio_promedio.csv": queries.precio_promedio_por_producto(),
        "02_precio_maximo.csv": df_max,
        "03_precio_minimo_rango.csv": df_rango,
        "04_variacion_mensual.csv": queries.variacion_mensual_promedio(),
        "05_variacion_acumulada.csv": queries.variacion_acumulada(),
        "06_top_10_productos_caros.csv": queries.top_productos_mas_caros(),
        "07_top_5_mayor_alza.csv": queries.top_productos_mayor_alza(),
        "08_top_5_mas_estables.csv": queries.top_productos_mas_estables(),
        "09_costo_por_cadena.csv": queries.costo_canasta_por_cadena(),
        "10_diferencia_entre_cadenas.csv": queries.diferencia_precio_entre_cadenas(),
    }

    contenido = BytesIO()
    with ZipFile(contenido, mode="w", compression=ZIP_DEFLATED) as archivo_zip:
        for nombre, df in archivos.items():
            archivo_zip.writestr(nombre, df.to_csv(index=False).encode("utf-8-sig"))
    return contenido.getvalue()


st.download_button(
    "Descargar los 10 KPIs (ZIP)",
    data=generar_zip_kpis(),
    file_name="kpis_canasta_pacic.zip",
    mime="application/zip",
    help="Incluye un archivo CSV independiente para cada KPI.",
)


# -------------------------------------------------------------------------
# Cada opción muestra su contenido
# -------------------------------------------------------------------------
if kpi == "Precio promedio":
    st.header("Precio promedio por producto")
    df = queries.precio_promedio_por_producto()
    exigir_datos(df, "No hay datos de la canasta para el periodo seleccionado.")
    top = df.iloc[0]
    st.metric("Producto más caro (promedio)", top["producto"], f"${top['precio_promedio']:,}")
    fig = charts.barra_horizontal(df, "precio_promedio", "producto", "Precio promedio por producto")
    st.plotly_chart(fig, use_container_width=True)
    mostrar_tabla(df)
    bloque_explicativo(
        "Precio promedio de las observaciones del catálogo durante enero‑agosto 2026.",
        "Valores más altos indican mayor costo del bien.",
        f"El producto con mayor precio promedio es {top['producto']} con ${top['precio_promedio']:,}."
    )
    st.download_button("Descargar CSV", df.to_csv(index=False).encode("utf-8"),
                       file_name="precio_promedio.csv", mime="text/csv")

elif kpi == "Precio máximo":
    st.header("Precio máximo por producto")
    df = queries.precio_maximo_por_producto()
    exigir_datos(df, "No hay datos de precios máximos para el periodo seleccionado.")
    top = df.iloc[0]
    st.metric("Producto más caro (máximo)", top["producto"], f"${top['precio_maximo']:,}")
    fig = charts.barra_horizontal(df, "precio_maximo", "producto", "Precio máximo por producto")
    st.plotly_chart(fig, use_container_width=True)
    mostrar_tabla(df)
    bloque_explicativo(
        "Precio máximo observado entre enero‑agosto 2026.",
        "Muestra el peor caso de precio pagado.",
        f"El producto con mayor precio máximo es {top['producto']} con ${top['precio_maximo']:,}."
    )
    st.download_button("Descargar CSV", df.to_csv(index=False).encode("utf-8"),
                       file_name="precio_maximo.csv", mime="text/csv")

elif kpi == "Precio mínimo / rango":
    st.header("Precio mínimo y rango por producto")
    df_min = queries.precio_minimo_por_producto()
    df_max = queries.precio_maximo_por_producto()
    df_rango = pd.merge(df_min[["producto", "precio_minimo"]], df_max[["producto", "precio_maximo"]], on="producto")
    exigir_datos(df_rango, "No hay datos suficientes para calcular el rango de precios.")
    fig = charts.barra_rango_precio(df_rango, "Rango de precios (min‑max) por producto")
    st.plotly_chart(fig, use_container_width=True)
    df_rango["rango"] = df_rango["precio_maximo"] - df_rango["precio_minimo"]
    mostrar_tabla(df_rango)
    top = df_rango.sort_values("rango", ascending=False).iloc[0]
    st.metric("Mayor rango de precios", top["producto"], f"${top['rango']:,}")
    bloque_explicativo(
        "Diferencia entre precio máximo y mínimo por producto.",
        "Un rango amplio indica alta volatilidad.",
        f"El producto con mayor rango es {top['producto']} (${top['rango']:,})."
    )
    st.download_button("Descargar CSV", df_rango.to_csv(index=False).encode("utf-8"),
                       file_name="rango_precios.csv", mime="text/csv")

elif kpi == "Variación mensual":
    st.header("Variación mensual del precio promedio (%)")
    df = queries.variacion_mensual_promedio()
    exigir_datos(df, "No hay datos mensuales suficientes para calcular la variación.")
    fig = charts.heatmap_variacion(df, "Variación mensual % (producto × periodo)")
    st.plotly_chart(fig, use_container_width=True)
    mostrar_tabla(df)
    bloque_explicativo(
        "Variación porcentual respecto al mes anterior.",
        "Valores positivos = alza, negativos = baja.",
        "Revisa la tabla para identificar la mayor subida mensual."
    )
    st.download_button("Descargar CSV", df.to_csv(index=False).encode("utf-8"),
                       file_name="variacion_mensual.csv", mime="text/csv")

elif kpi == "Variación acumulada":
    st.header("Variación acumulada (enero ↔ agosto)")
    df = queries.variacion_acumulada()
    exigir_datos(df, "No hay datos de enero y agosto para calcular la variación acumulada.")
    fig = charts.barras_variacion_acumulada(df, "Variación acumulada % entre enero y agosto")
    st.plotly_chart(fig, use_container_width=True)
    mostrar_tabla(df)
    bloque_explicativo(
        "Cambio total en precio promedio entre el primer y último mes.",
        "Positivo = alza, negativo = disminución.",
        f"El producto con mayor alza acumulada es {df.iloc[0]['producto']} (+{df.iloc[0]['delta_pct']}%)."
    )
    st.download_button("Descargar CSV", df.to_csv(index=False).encode("utf-8"),
                       file_name="variacion_acumulada.csv", mime="text/csv")

elif kpi == "Top 10 productos más caros":
    st.header("Top 10 productos más caros (precio promedio)")
    df = queries.top_productos_mas_caros()
    exigir_datos(df, "No hay productos disponibles para construir este ranking.")
    fig = charts.barras_top_productos(df, "precio_promedio", "Top 10 productos más caros")
    st.plotly_chart(fig, use_container_width=True)
    mostrar_tabla(df)
    bloque_explicativo(
        "Los 10 productos con mayor precio promedio.",
        "Orden descendente por precio.",
        f"El producto más caro es {df.iloc[0]['producto']} con ${df.iloc[0]['precio_promedio']:,}."
    )
    st.download_button("Descargar CSV", df.to_csv(index=False).encode("utf-8"),
                       file_name="top_10_caros.csv", mime="text/csv")

elif kpi == "Top 5 mayor alza":
    st.header("Top 5 productos con mayor alza acumulada")
    df = queries.top_productos_mayor_alza()
    exigir_datos(df, "No hay datos suficientes para construir el ranking de alzas.")
    fig = charts.barras_top_productos(df, "delta_pct", "Mayor alza % acumulada")
    st.plotly_chart(fig, use_container_width=True)
    mostrar_tabla(df)
    bloque_explicativo(
        "Productos con mayor aumento porcentual entre enero y agosto.",
        "Mayor delta_pct = mayor alza.",
        f"El producto con mayor alza es {df.iloc[0]['producto']} (+{df.iloc[0]['delta_pct']}%)."
    )
    st.download_button("Descargar CSV", df.to_csv(index=False).encode("utf-8"),
                       file_name="top_5_alza.csv", mime="text/csv")

elif kpi == "Top 5 más estables":
    st.header("Top 5 productos más estables (menor variación absoluta)")
    df = queries.top_productos_mas_estables()
    exigir_datos(df, "No hay datos suficientes para construir el ranking de estabilidad.")
    fig = charts.barras_top_productos(df, "abs_delta", "Menor variación absoluta")
    st.plotly_chart(fig, use_container_width=True)
    mostrar_tabla(df)
    bloque_explicativo(
        "Productos cuya variación acumulada es más cercana a cero.",
        "Valor bajo indica estabilidad de precios.",
        f"El producto más estable es {df.iloc[0]['producto']} ({df.iloc[0]['delta_pct']}%)."
    )
    st.download_button("Descargar CSV", df.to_csv(index=False).encode("utf-8"),
                       file_name="top_5_estables.csv", mime="text/csv")

elif kpi == "Costo por cadena":
    st.header("Costo de la canasta por cadena")
    df = queries.costo_canasta_por_cadena()
    exigir_datos(df, "No hay cadenas con cobertura suficiente para calcular el costo de la canasta.")
    fig = charts.barras_costo_cadena(df, "Costo promedio de la canasta por cadena")
    st.plotly_chart(fig, use_container_width=True)
    mostrar_tabla(df)
    bloque_explicativo(
        "Suma de los precios promedio de los productos disponibles por cadena.",
        "Mayor costo = cadena más cara.",
        "La cobertura se muestra en la tabla para comparar cadenas con cantidades similares de productos."
    )
    st.download_button("Descargar CSV", df.to_csv(index=False).encode("utf-8"),
                       file_name="costo_cadena.csv", mime="text/csv")

elif kpi == "Diferencia entre cadenas":
    st.header("Diferencia de precio entre cadenas (por producto)")
    df = queries.diferencia_precio_entre_cadenas()
    exigir_datos(df, "No hay datos suficientes para comparar cadenas.")
    fig = charts.barras_diferencia_cadenas(df, "Variación % entre la cadena más cara y la más barata")
    st.plotly_chart(fig, use_container_width=True)
    mostrar_tabla(df)
    bloque_explicativo(
        "% de diferencia entre la cadena más cara y la más barata para cada producto.",
        "Valores altos indican gran disparidad de precios entre cadenas.",
        f"El producto con mayor disparidad es {df.iloc[0]['producto']} ({df.iloc[0]['variacion_pct']}%)."
    )
    st.download_button("Descargar CSV", df.to_csv(index=False).encode("utf-8"),
                       file_name="diferencia_cadenas.csv", mime="text/csv")
