#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
detectar_asientos_duplicados.py
-------------------------------
Detecta posibles registros contables duplicados a partir de un CSV
(por ejemplo, una extracción de documentos contables de un ERP).

Pruebas que realiza:
  A1. Número de documento repetido (misma sociedad, ejercicio y número).
  A2. Posible factura duplicada: misma sociedad, cuenta, referencia, importe
      y moneda en documentos distintos.
  A3. Posible duplicado sin referencia coincidente: misma sociedad, cuenta,
      importe, moneda y fecha del documento, con referencias distintas o vacías.

Columnas esperadas en el CSV (renombra los encabezados si es necesario):
  Obligatorias: sociedad, ejercicio, num_documento, cuenta, importe, moneda
  Opcionales:   referencia (habilita A2), fecha_documento (habilita A3),
                usuario_registro

Notas:
  * El archivo debe tener una fila por documento. Si tu extracción es por
    partidas, A1 marcaría documentos normales: usa --omitir-a1.
  * Los importes con formato SAP (por ejemplo "100.00-") se interpretan como negativos.
  * Un resultado es un INDICIO, no un hallazgo: valida con el área contable.

Uso:
    python detectar_asientos_duplicados.py asientos.csv
    python detectar_asientos_duplicados.py asientos.csv --separador-decimal ","

Sin dependencias externas (solo biblioteca estándar, Python 3.8+).
"""
import argparse
import csv
import re
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation

OBLIGATORIAS = ["sociedad", "ejercicio", "num_documento", "cuenta", "importe", "moneda"]


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
        valor = Decimal(t).quantize(Decimal("0.01"))
    except InvalidOperation:
        return None
    return -valor if negativo else valor


def normalizar_referencia(ref):
    """Mayúsculas y sin separadores: 'fac-1001 ' y 'FAC 1001' -> 'FAC1001'."""
    return re.sub(r"[\s\-_/.]", "", (ref or "").upper())


def main():
    p = argparse.ArgumentParser(description="Detección de asientos duplicados.")
    p.add_argument("archivo", help="CSV con los documentos contables")
    p.add_argument("--salida", default="reporte_asientos_duplicados.csv")
    p.add_argument("--delimitador", default=",")
    p.add_argument("--codificacion", default="utf-8-sig")
    p.add_argument("--separador-decimal", default=".", choices=[".", ","])
    p.add_argument("--omitir-a1", action="store_true",
                   help="Omite la prueba de número de documento repetido")
    args = p.parse_args()

    with open(args.archivo, newline="", encoding=args.codificacion) as f:
        lector = csv.DictReader(f, delimiter=args.delimitador)
        columnas = [c.strip() for c in (lector.fieldnames or [])]
        faltan = [c for c in OBLIGATORIAS if c not in columnas]
        if faltan:
            sys.exit(f"Faltan columnas obligatorias: {faltan}")
        filas = [{(k or "").strip(): (v or "").strip() for k, v in r.items()} for r in lector]

    tiene_ref = "referencia" in columnas
    tiene_fecha = "fecha_documento" in columnas
    tiene_usuario = "usuario_registro" in columnas

    registros, invalidos = [], 0
    for fila in filas:
        importe = a_decimal(fila["importe"], args.separador_decimal)
        if importe is None:
            invalidos += 1
            continue
        fila["_importe"] = importe
        fila["_doc"] = f"{fila['sociedad']}/{fila['ejercicio']}/{fila['num_documento']}"
        fila["_ref"] = normalizar_referencia(fila.get("referencia", "")) if tiene_ref else ""
        registros.append(fila)
    if invalidos:
        print(f"[aviso] {invalidos} fila(s) con importe no válido fueron omitidas.")

    hallazgos = []

    def agregar(prueba, descripcion, filas_grupo):
        docs = sorted({r["_doc"] for r in filas_grupo})
        primera = filas_grupo[0]
        hallazgos.append({
            "prueba": prueba, "descripcion": descripcion,
            "documentos": "; ".join(docs),
            "cuenta": primera["cuenta"],
            "importe": str(primera["_importe"]), "moneda": primera["moneda"],
            "referencias": "; ".join(sorted({r.get("referencia", "") for r in filas_grupo})),
            "usuarios": "; ".join(sorted({r.get("usuario_registro", "") for r in filas_grupo})) if tiene_usuario else "",
            "cantidad_documentos": len(docs),
            "cantidad_registros": len(filas_grupo),
        })

    # A1. Número de documento repetido
    if not args.omitir_a1:
        por_doc = defaultdict(list)
        for r in registros:
            por_doc[r["_doc"]].append(r)
        for doc, grupo in sorted(por_doc.items()):
            if len(grupo) > 1:
                agregar("A1", "Número de documento repetido", grupo)

    # A2. Misma referencia, cuenta, importe y moneda en documentos distintos
    if tiene_ref:
        grupos = defaultdict(list)
        for r in registros:
            if r["_ref"]:
                clave = (r["sociedad"], r["cuenta"], r["_ref"], r["_importe"], r["moneda"])
                grupos[clave].append(r)
        for clave, grupo in sorted(grupos.items(), key=lambda x: str(x[0])):
            if len({r["_doc"] for r in grupo}) > 1:
                agregar("A2", "Posible factura duplicada (misma referencia, cuenta e importe)", grupo)

    # A3. Mismo importe, cuenta y fecha, sin referencia coincidente
    if tiene_fecha:
        grupos = defaultdict(list)
        for r in registros:
            clave = (r["sociedad"], r["cuenta"], r["_importe"], r["moneda"], r["fecha_documento"])
            grupos[clave].append(r)
        for clave, grupo in sorted(grupos.items(), key=lambda x: str(x[0])):
            if len({r["_doc"] for r in grupo}) < 2:
                continue
            refs = {r["_ref"] for r in grupo}
            if len(refs) == 1 and "" not in refs:
                continue  # ya cubierto por A2
            agregar("A3", "Posible duplicado: mismo importe, cuenta y fecha", grupo)

    campos = ["prueba", "descripcion", "documentos", "cuenta", "importe", "moneda",
              "referencias", "usuarios", "cantidad_documentos", "cantidad_registros"]
    with open(args.salida, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(hallazgos)

    print(f"Registros analizados: {len(registros)}")
    for codigo in ("A1", "A2", "A3"):
        print(f"  {codigo}: {sum(1 for h in hallazgos if h['prueba'] == codigo)} coincidencia(s)")
    print(f"Reporte generado: {args.salida}")


if __name__ == "__main__":
    main()
