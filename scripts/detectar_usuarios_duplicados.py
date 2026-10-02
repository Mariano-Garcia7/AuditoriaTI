#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
detectar_usuarios_duplicados.py
-------------------------------
Detecta posibles usuarios duplicados a partir de un listado en CSV
(por ejemplo, exportado de SAP, Active Directory o cualquier ERP).

Pruebas que realiza:
  U1. Mismo ID de empleado asignado a varios usuarios.
  U2. Mismo correo electrónico asignado a varios usuarios.
  U3. Mismo nombre completo (normalizado) en varios usuarios.
  U4. IDs de usuario equivalentes al normalizarlos (ej. "J.PEREZ" y "JPEREZ").
  U5. (Opcional) Nombres muy parecidos, mediante similitud de texto.

IMPORTANTE: un resultado es un INDICIO, no un hallazgo. Pueden existir
duplicados legítimos (cuentas administrativas separadas de la cuenta normal,
cuentas de servicio, etc.). Valida cada caso con el responsable del sistema.

Uso:
    python detectar_usuarios_duplicados.py usuarios.csv
    python detectar_usuarios_duplicados.py usuarios.csv --similitud 0.9

Sin dependencias externas (solo biblioteca estándar, Python 3.8+).
"""
import argparse
import csv
import re
import sys
import unicodedata
from collections import defaultdict
from difflib import SequenceMatcher


def normalizar_texto(valor):
    """Minúsculas, sin acentos y sin espacios repetidos."""
    if not valor:
        return ""
    valor = unicodedata.normalize("NFKD", valor)
    valor = "".join(c for c in valor if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", valor).strip().lower()


def normalizar_usuario(valor):
    """Solo letras y números en minúscula: 'J.Perez' y 'JPEREZ' -> 'jperez'."""
    return re.sub(r"[^a-z0-9]", "", normalizar_texto(valor))


def leer_csv(ruta, delimitador, codificacion):
    with open(ruta, newline="", encoding=codificacion) as f:
        lector = csv.DictReader(f, delimiter=delimitador)
        if not lector.fieldnames:
            sys.exit("El archivo está vacío o no tiene encabezados.")
        columnas = [c.strip() for c in lector.fieldnames]
        filas = [
            {(k or "").strip(): (v or "").strip() for k, v in fila.items()}
            for fila in lector
        ]
    return columnas, filas


def agrupar(filas, col_usuario, col_valor, normalizador):
    """Agrupa usuarios que comparten el mismo valor normalizado."""
    grupos = defaultdict(set)
    for fila in filas:
        usuario = fila.get(col_usuario, "")
        clave = normalizador(fila.get(col_valor, ""))
        if usuario and clave:
            grupos[clave].add(usuario)
    return {clave: usr for clave, usr in grupos.items() if len(usr) > 1}


def buscar_similares(filas, col_usuario, col_nombre, umbral):
    """Pares de nombres distintos pero muy parecidos (posibles erratas)."""
    nombres = defaultdict(set)
    for fila in filas:
        nombre = normalizar_texto(fila.get(col_nombre, ""))
        usuario = fila.get(col_usuario, "")
        if nombre and usuario:
            nombres[nombre].add(usuario)
    lista = sorted(nombres)
    if len(lista) > 5000:
        print("[aviso] Más de 5,000 nombres: la prueba U5 puede tardar.")
    resultados = []
    for i, a in enumerate(lista):
        for b in lista[i + 1:]:
            if abs(len(a) - len(b)) > 3:
                continue
            ratio = SequenceMatcher(None, a, b).ratio()
            if ratio >= umbral:
                resultados.append((a, b, ratio, nombres[a] | nombres[b]))
    return resultados


def main():
    p = argparse.ArgumentParser(description="Detección de usuarios duplicados.")
    p.add_argument("archivo", help="CSV con el listado de usuarios")
    p.add_argument("--salida", default="reporte_usuarios_duplicados.csv")
    p.add_argument("--delimitador", default=",")
    p.add_argument("--codificacion", default="utf-8-sig")
    p.add_argument("--col-usuario", default="usuario")
    p.add_argument("--col-nombre", default="nombre_completo")
    p.add_argument("--col-correo", default="correo")
    p.add_argument("--col-empleado", default="id_empleado")
    p.add_argument("--similitud", type=float, default=0.0,
                   help="Umbral 0-1 para nombres parecidos (ej. 0.9). 0 = desactivada")
    args = p.parse_args()

    columnas, filas = leer_csv(args.archivo, args.delimitador, args.codificacion)
    if args.col_usuario not in columnas:
        sys.exit(f"No existe la columna '{args.col_usuario}'. Columnas: {columnas}")

    pruebas = [
        ("U1", "Mismo ID de empleado en varios usuarios", args.col_empleado, normalizar_texto),
        ("U2", "Mismo correo en varios usuarios", args.col_correo, normalizar_texto),
        ("U3", "Mismo nombre completo en varios usuarios", args.col_nombre, normalizar_texto),
        ("U4", "IDs de usuario equivalentes al normalizarlos", args.col_usuario, normalizar_usuario),
    ]

    hallazgos = []
    for codigo, descripcion, columna, normalizador in pruebas:
        if columna not in columnas:
            print(f"[aviso] No se encontró la columna '{columna}'. Se omite {codigo}.")
            continue
        grupos = agrupar(filas, args.col_usuario, columna, normalizador)
        for clave, usuarios in sorted(grupos.items()):
            hallazgos.append({
                "prueba": codigo, "descripcion": descripcion,
                "valor_coincidente": clave,
                "usuarios": "; ".join(sorted(usuarios)),
                "cantidad_usuarios": len(usuarios), "similitud": "",
            })

    if args.similitud > 0:
        if args.col_nombre not in columnas:
            print(f"[aviso] No se encontró '{args.col_nombre}'. Se omite U5.")
        else:
            for a, b, ratio, usuarios in buscar_similares(
                    filas, args.col_usuario, args.col_nombre, args.similitud):
                hallazgos.append({
                    "prueba": "U5", "descripcion": "Nombres muy parecidos",
                    "valor_coincidente": f"{a}  ~  {b}",
                    "usuarios": "; ".join(sorted(usuarios)),
                    "cantidad_usuarios": len(usuarios), "similitud": f"{ratio:.2f}",
                })

    campos = ["prueba", "descripcion", "valor_coincidente", "usuarios",
              "cantidad_usuarios", "similitud"]
    with open(args.salida, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(hallazgos)

    print(f"Usuarios analizados: {len(filas)}")
    for codigo in ("U1", "U2", "U3", "U4", "U5"):
        n = sum(1 for h in hallazgos if h["prueba"] == codigo)
        print(f"  {codigo}: {n} coincidencia(s)")
    print(f"Reporte generado: {args.salida}")


if __name__ == "__main__":
    main()
