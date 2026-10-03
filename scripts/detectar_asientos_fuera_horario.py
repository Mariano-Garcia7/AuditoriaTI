#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
detectar_asientos_fuera_horario.py
----------------------------------
Detecta registros contables capturados en fin de semana, fuera del horario
laboral o en días festivos, a partir de un CSV.

Columnas del CSV:
  Obligatorias: fecha_registro, hora_registro
  Opcionales:   num_documento, usuario_registro, importe, sociedad
  (En SAP, la fecha y hora de captura suelen estar en los campos CPUDT y CPUTM
  de la cabecera del documento, y el usuario en USNAM. Valida en tu entorno.)

Formatos aceptados: fecha AAAA-MM-DD, DD/MM/AAAA, AAAAMMDD o DD.MM.AAAA;
hora HH:MM:SS, HH:MM o HHMMSS.

Pruebas:
  H1. Registro en día no laboral (por defecto sábado y domingo).
  H2. Registro fuera del horario laboral (por defecto 08:00 a 19:00).
  H3. Registro en día festivo (lista indicada con --festivos).

IMPORTANTE: un resultado es un INDICIO. Los cierres contables, los procesos
automáticos y los turnos especiales generan registros fuera de horario
legítimos. Valida cada caso con el área contable.

Uso:
    python detectar_asientos_fuera_horario.py asientos.csv
    python detectar_asientos_fuera_horario.py asientos.csv --inicio 09:00 --fin 18:00 \\
        --festivos 2026-03-16,2026-05-01

Sin dependencias externas (solo biblioteca estándar, Python 3.8+).
"""
import argparse
import csv
import sys
from collections import Counter
from datetime import datetime

FORMATOS_FECHA = ["%Y-%m-%d", "%d/%m/%Y", "%Y%m%d", "%d.%m.%Y"]
FORMATOS_HORA = ["%H:%M:%S", "%H:%M", "%H%M%S"]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def parsear(texto, formatos, convertir):
    for formato in formatos:
        try:
            return convertir(datetime.strptime(texto.strip(), formato))
        except ValueError:
            continue
    return None


def a_fecha(texto):
    return parsear(texto, FORMATOS_FECHA, lambda d: d.date())


def a_hora(texto):
    return parsear(texto, FORMATOS_HORA, lambda d: d.time())


def main():
    p = argparse.ArgumentParser(description="Asientos fuera de horario.")
    p.add_argument("archivo", help="CSV con los registros")
    p.add_argument("--inicio", default="08:00", help="Inicio del horario laboral (HH:MM)")
    p.add_argument("--fin", default="19:00", help="Fin del horario laboral (HH:MM)")
    p.add_argument("--dias-no-laborales", default="5,6",
                   help="Días no laborales: 0=lunes ... 6=domingo (por defecto 5,6)")
    p.add_argument("--festivos", default="",
                   help="Fechas festivas separadas por coma (AAAA-MM-DD)")
    p.add_argument("--delimitador", default=",")
    p.add_argument("--codificacion", default="utf-8-sig")
    p.add_argument("--salida", default="reporte_asientos_fuera_horario.csv")
    p.add_argument("--salida-resumen", default="reporte_fuera_horario_resumen.csv")
    args = p.parse_args()

    inicio, fin = a_hora(args.inicio), a_hora(args.fin)
    if not inicio or not fin:
        sys.exit("Formato de --inicio o --fin no válido. Usa HH:MM.")
    no_laborales = {int(x) for x in args.dias_no_laborales.split(",") if x.strip() != ""}
    festivos = set()
    for texto in [x for x in args.festivos.split(",") if x.strip()]:
        fecha = a_fecha(texto)
        if not fecha:
            sys.exit(f"Fecha festiva no válida: {texto}")
        festivos.add(fecha)

    with open(args.archivo, newline="", encoding=args.codificacion) as f:
        lector = csv.DictReader(f, delimiter=args.delimitador)
        columnas = [c.strip() for c in (lector.fieldnames or [])]
        for requerida in ("fecha_registro", "hora_registro"):
            if requerida not in columnas:
                sys.exit(f"Falta la columna obligatoria '{requerida}'. Columnas: {columnas}")
        filas = [{(k or "").strip(): (v or "").strip() for k, v in r.items()} for r in lector]

    hallazgos, invalidos = [], 0
    totales, marcados = Counter(), Counter()
    for fila in filas:
        fecha = a_fecha(fila["fecha_registro"])
        hora = a_hora(fila["hora_registro"])
        if fecha is None or hora is None:
            invalidos += 1
            continue
        usuario = fila.get("usuario_registro", "(sin usuario)") or "(sin usuario)"
        totales[usuario] += 1
        motivos = []
        if fecha.weekday() in no_laborales:
            motivos.append("día no laboral")
        if fecha in festivos:
            motivos.append("día festivo")
        if not (inicio <= hora < fin):
            motivos.append("fuera de horario")
        if motivos:
            marcados[usuario] += 1
            hallazgos.append({
                "num_documento": fila.get("num_documento", ""),
                "usuario_registro": usuario,
                "fecha_registro": fecha.isoformat(),
                "dia_semana": DIAS[fecha.weekday()],
                "hora_registro": hora.strftime("%H:%M:%S"),
                "importe": fila.get("importe", ""),
                "motivos": "; ".join(motivos),
            })
    if invalidos:
        print(f"[aviso] {invalidos} fila(s) con fecha u hora no válida fueron omitidas.")

    campos = ["num_documento", "usuario_registro", "fecha_registro", "dia_semana",
              "hora_registro", "importe", "motivos"]
    with open(args.salida, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(hallazgos)

    resumen = [{"usuario_registro": u, "registros": totales[u], "marcados": marcados[u],
                "porcentaje_marcado": round(100 * marcados[u] / totales[u], 1)}
               for u in totales if marcados[u] > 0]
    resumen.sort(key=lambda r: (r["marcados"], r["porcentaje_marcado"]), reverse=True)
    with open(args.salida_resumen, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.DictWriter(
            f, fieldnames=["usuario_registro", "registros", "marcados", "porcentaje_marcado"])
        escritor.writeheader()
        escritor.writerows(resumen)

    print(f"Registros analizados: {sum(totales.values())}")
    print(f"Registros marcados: {len(hallazgos)}")
    for r in resumen:
        print(f"  {r['usuario_registro']:<14} {r['marcados']} de {r['registros']} "
              f"({r['porcentaje_marcado']}%)")
    print(f"Reporte: {args.salida}")
    print(f"Resumen por usuario: {args.salida_resumen}")


if __name__ == "__main__":
    main()
