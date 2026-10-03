#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
detectar_benford.py
-------------------
Análisis de la Ley de Benford sobre los importes de un CSV (asientos,
facturas, pagos, etc.). Compara la frecuencia real de los primeros dígitos
con la esperada: P(d) = log10(1 + 1/d).

Qué calcula:
  * Distribución del primer dígito (o de los dos primeros con --digitos 2).
  * Prueba z por dígito (marca |z| > 1.96).
  * Chi-cuadrada global contra el valor crítico al 5% y al 1%.
  * MAD (desviación absoluta media) con los rangos de conformidad de Nigrini.
  * Opcional: el mismo análisis por grupo (usuario, cuenta, proveedor) con --grupo.

IMPORTANTE:
  * Una desviación es un INDICIO, no una prueba de fraude. Benford no aplica bien
    a importes asignados (precios fijos, tarifas), con rangos muy acotados o con
    pocos datos (idealmente más de 1,000 registros; con menos de 300 poco fiable).
  * Para grupos pequeños usa la chi-cuadrada: los rangos de MAD se definieron
    para muestras grandes y generan falsas alarmas con pocos datos.

Uso:
    python detectar_benford.py asientos.csv
    python detectar_benford.py asientos.csv --digitos 2
    python detectar_benford.py asientos.csv --grupo usuario_registro

Sin dependencias externas (solo biblioteca estándar, Python 3.8+).
"""
import argparse
import csv
import math
import sys
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation

# Valores críticos de chi-cuadrada (5% y 1%): gl = 8 (1 dígito) y gl = 89 (2 dígitos)
CRITICOS = {1: (15.507, 20.090), 2: (112.022, 122.942)}

# Rangos de conformidad de Nigrini para MAD
MAD_RANGOS = {
    1: [(0.006, "Conformidad cercana"), (0.012, "Conformidad aceptable"),
        (0.015, "Conformidad marginal")],
    2: [(0.0012, "Conformidad cercana"), (0.0018, "Conformidad aceptable"),
        (0.0022, "Conformidad marginal")],
}


def a_decimal(texto, separador_decimal="."):
    t = (texto or "").strip().replace(" ", "")
    if not t:
        return None
    negativo = False
    if t.endswith("-"):  # formato SAP: 100.00-
        negativo, t = True, t[:-1]
    if separador_decimal == ",":
        t = t.replace(".", "").replace(",", ".")
    else:
        t = t.replace(",", "")
    try:
        valor = Decimal(t)
    except InvalidOperation:
        return None
    return -valor if negativo else valor


def primeros_digitos(valor, n):
    """Primeros n dígitos significativos de |valor| (None si es cero)."""
    v = abs(valor)
    if v == 0:
        return None
    digitos = list(v.normalize().as_tuple().digits)[:n]
    while len(digitos) < n:
        digitos.append(0)
    return int("".join(str(d) for d in digitos))


def esperado(d):
    return math.log10(1 + 1 / d)


def analizar(valores, n):
    """Devuelve (filas por dígito, N, chi2, MAD)."""
    cuentas = Counter()
    for v in valores:
        d = primeros_digitos(v, n)
        if d is not None:
            cuentas[d] += 1
    total = sum(cuentas.values())
    rango = range(1, 10) if n == 1 else range(10, 100)
    filas, chi2, suma_abs = [], 0.0, 0.0
    for d in rango:
        e = esperado(d)
        obs = cuentas.get(d, 0)
        p = obs / total if total else 0.0
        chi2 += ((obs - e * total) ** 2) / (e * total) if total else 0.0
        suma_abs += abs(p - e)
        z = 0.0
        if total:
            num = abs(p - e) - 1 / (2 * total)
            z = max(0.0, num) / math.sqrt(e * (1 - e) / total)
        filas.append({
            "digito": d, "observados": obs,
            "observado_pct": round(100 * p, 2), "esperado_pct": round(100 * e, 2),
            "diferencia_pp": round(100 * (p - e), 2), "z": round(z, 2),
            "marca": "REVISAR" if z > 1.96 else "",
        })
    mad = suma_abs / len(rango)
    return filas, total, chi2, mad


def nivel_mad(mad, n):
    for limite, nombre in MAD_RANGOS[n]:
        if mad <= limite:
            return nombre
    return "No conformidad"


def main():
    p = argparse.ArgumentParser(description="Análisis de la Ley de Benford.")
    p.add_argument("archivo", help="CSV con los importes")
    p.add_argument("--col-importe", default="importe")
    p.add_argument("--digitos", type=int, choices=[1, 2], default=1,
                   help="1 = primer dígito, 2 = primeros dos dígitos")
    p.add_argument("--grupo", default=None,
                   help="Columna para analizar por grupo (ej. usuario_registro)")
    p.add_argument("--minimo-grupo", type=int, default=100,
                   help="Tamaño mínimo de un grupo para analizarlo (por defecto 100)")
    p.add_argument("--minimo-importe", type=float, default=0.0,
                   help="Ignora importes menores a este valor (en valor absoluto)")
    p.add_argument("--separador-decimal", default=".", choices=[".", ","])
    p.add_argument("--delimitador", default=",")
    p.add_argument("--codificacion", default="utf-8-sig")
    p.add_argument("--salida", default="reporte_benford.csv")
    p.add_argument("--salida-grupos", default="reporte_benford_grupos.csv")
    args = p.parse_args()

    with open(args.archivo, newline="", encoding=args.codificacion) as f:
        lector = csv.DictReader(f, delimiter=args.delimitador)
        columnas = [c.strip() for c in (lector.fieldnames or [])]
        if args.col_importe not in columnas:
            sys.exit(f"No existe la columna '{args.col_importe}'. Columnas: {columnas}")
        if args.grupo and args.grupo not in columnas:
            sys.exit(f"No existe la columna de grupo '{args.grupo}'.")
        filas = [{(k or "").strip(): (v or "").strip() for k, v in r.items()} for r in lector]

    importes, por_grupo, invalidos = [], defaultdict(list), 0
    minimo = Decimal(str(args.minimo_importe))
    for fila in filas:
        v = a_decimal(fila[args.col_importe], args.separador_decimal)
        if v is None:
            invalidos += 1
            continue
        if v == 0 or abs(v) < minimo:
            continue
        importes.append(v)
        if args.grupo:
            por_grupo[fila.get(args.grupo, "")].append(v)
    if invalidos:
        print(f"[aviso] {invalidos} fila(s) con importe no válido fueron omitidas.")
    if not importes:
        sys.exit("No hay importes utilizables.")

    n = args.digitos
    resultado, total, chi2, mad = analizar(importes, n)
    crit5, crit1 = CRITICOS[n]

    with open(args.salida, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.DictWriter(f, fieldnames=list(resultado[0].keys()))
        escritor.writeheader()
        escritor.writerows(resultado)

    print(f"Importes analizados: {total}")
    if total < 300:
        print("[aviso] Menos de 300 importes: el resultado es poco fiable.")
    print(f"MAD: {mad:.4f} -> {nivel_mad(mad, n)}")
    veredicto = ("supera el valor crítico al 1%" if chi2 > crit1
                 else "supera el valor crítico al 5%" if chi2 > crit5
                 else "no supera el valor crítico")
    print(f"Chi-cuadrada: {chi2:.2f} (5%: {crit5}, 1%: {crit1}) -> {veredicto}")
    marcados = [r["digito"] for r in resultado if r["marca"]]
    print(f"Dígitos a revisar (|z| > 1.96): {marcados if marcados else 'ninguno'}")
    print(f"Reporte generado: {args.salida}")

    if args.grupo:
        filas_grupo = []
        for nombre, valores in por_grupo.items():
            if len(valores) < args.minimo_grupo:
                continue
            res, tot, chi, m = analizar(valores, 1)
            mas_desviado = max(res, key=lambda r: r["diferencia_pp"])
            filas_grupo.append({
                "grupo": nombre, "importes": tot, "mad": round(m, 4),
                "nivel_mad": nivel_mad(m, 1), "chi2": round(chi, 2),
                "supera_5pct": "SI" if chi > CRITICOS[1][0] else "NO",
                "supera_1pct": "SI" if chi > CRITICOS[1][1] else "NO",
                "digito_mas_sobrerrepresentado": mas_desviado["digito"],
                "exceso_pp": mas_desviado["diferencia_pp"],
            })
        filas_grupo.sort(key=lambda r: r["chi2"], reverse=True)
        if filas_grupo:
            with open(args.salida_grupos, "w", newline="", encoding="utf-8-sig") as f:
                escritor = csv.DictWriter(f, fieldnames=list(filas_grupo[0].keys()))
                escritor.writeheader()
                escritor.writerows(filas_grupo)
            print(f"\nAnálisis por '{args.grupo}' (grupos con al menos {args.minimo_grupo} importes):")
            for r in filas_grupo:
                print(f"  {r['grupo']:<14} n={r['importes']:<5} chi2={r['chi2']:<8} "
                      f">5%:{r['supera_5pct']:<3} >1%:{r['supera_1pct']:<3} "
                      f"dígito {r['digito_mas_sobrerrepresentado']} (+{r['exceso_pp']} pp)")
            print(f"Reporte por grupo: {args.salida_grupos}")
        else:
            print(f"[aviso] Ningún grupo alcanzó el mínimo de {args.minimo_grupo} importes.")


if __name__ == "__main__":
    main()
