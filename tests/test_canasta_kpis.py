# -*- coding: utf-8 -*-
"""
Pruebas unitarias para las funciones de gráficos de KPIs de la canasta básica.
No requieren conexión a base de datos.
"""
import pandas as pd
import pytest
from src import charts

@pytest.fixture
def dummy_promedio():
    return pd.DataFrame({
        "producto": ["Aceite", "Arroz"],
        "precio_promedio": [20.5, 15.3],
        "num_registros": [100, 120],
    })

def test_barra_horizontal(dummy_promedio):
    fig = charts.barra_horizontal(dummy_promedio, "precio_promedio", "producto", "Test")
    assert fig.layout.title.text == "Test"
    assert len(fig.data) == 1
    assert fig.data[0].type == "bar"

def test_barra_rango_precio():
    df = pd.DataFrame({
        "producto": ["Aceite", "Arroz"],
        "precio_minimo": [10, 8],
        "precio_maximo": [30, 25],
    })
    fig = charts.barra_rango_precio(df, "Rango")
    assert fig.layout.title.text == "Rango"
    assert len(fig.data) == 1
    assert fig.data[0].type == "bar"

def test_heatmap_variacion():
    df = pd.DataFrame({
        "producto": ["Aceite", "Aceite", "Arroz", "Arroz"],
        "periodo": ["2026-01", "2026-02", "2026-01", "2026-02"],
        "variacion_pct": [5.0, -2.0, 3.5, -1.0],
    })
    fig = charts.heatmap_variacion(df, "Heat")
    assert fig.layout.title.text == "Heat"
    assert fig.data[0].type == "heatmap"

def test_barras_variacion_acumulada():
    df = pd.DataFrame({
        "producto": ["Aceite", "Arroz"],
        "delta_pct": [10.0, -5.0],
        "delta_valor": [5.0, -2.0],
    })
    fig = charts.barras_variacion_acumulada(df, "Variación")
    assert fig.layout.title.text == "Variación"
    assert len(fig.data[0].x) == 2

def test_barras_top_productos():
    df = pd.DataFrame({
        "producto": ["Aceite", "Arroz"],
        "precio_promedio": [20.5, 15.3],
    })
    fig = charts.barras_top_productos(df, "precio_promedio", "Top")
    assert fig.layout.title.text == "Top"

def test_barras_costo_cadena():
    df = pd.DataFrame({
        "cadena_comercial": ["Cadena A", "Cadena B"],
        "costo_promedio": [2000, 1800],
        "productos_cubiertos": [22, 20],
    })
    fig = charts.barras_costo_cadena(df, "Costo")
    assert fig.layout.title.text == "Costo"

def test_barras_diferencia_cadenas():
    df = pd.DataFrame({
        "producto": ["Aceite"],
        "variacion_pct": [25.0],
        "cadena_mas_cara": ["Cadena A"],
        "max_precio": [30.0],
        "cadena_mas_barata": ["Cadena B"],
        "min_precio": [24.0],
    })
    fig = charts.barras_diferencia_cadenas(df, "Dif")
    assert fig.layout.title.text == "Dif"
