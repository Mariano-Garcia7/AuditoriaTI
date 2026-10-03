# Auditoria TI

Scripts, guías y plantillas para auditoría de TI, con enfoque en ISO/IEC 27001 y entornos SAP. Combina mi experiencia en auditoría con programación para automatizar pruebas y documentar controles.

> **Todo el contenido es de elaboración propia y usa datos ficticios.** No incluye información de clientes, de ninguna firma ni material de terceros.

## Contenido

```
it-audit-toolkit/
├── scripts/
│   ├── detectar_usuarios_duplicados.py     Usuarios duplicados
│   ├── detectar_asientos_duplicados.py     Registros contables duplicados
│   ├── detectar_benford.py                 Ley de Benford (global y por usuario/grupo)
│   ├── detectar_asientos_fuera_horario.py  Registros en fin de semana, fuera de horario o festivos
│   └── consultas_sql_duplicados.sql        Las mismas pruebas en SQL (PostgreSQL)
├── datos_ejemplo/                          Datos sintéticos con casos sembrados
│   ├── usuarios_ejemplo.csv
│   ├── asientos_ejemplo.csv
│   ├── asientos_benford_ejemplo.csv
│   └── asientos_horario_ejemplo.csv
└── docs/
    ├── sap-transacciones.md                Transacciones SAP críticas y contables comunes
    ├── iso27001-checklist-control-acceso.md   Checklist de controles del Anexo A (2022)
    ├── matriz-sod-ejemplo.md               Matriz de segregación de funciones
    └── plantilla-hallazgo.md               Plantilla de hallazgo con ejemplo
```

## Requisitos

Python 3.8 o superior. Los scripts usan solo la biblioteca estándar.

## Uso rápido

```bash
# Usuarios duplicados (con detección de nombres parecidos)
python scripts/detectar_usuarios_duplicados.py datos_ejemplo/usuarios_ejemplo.csv --similitud 0.9

# Registros contables duplicados
python scripts/detectar_asientos_duplicados.py datos_ejemplo/asientos_ejemplo.csv

# Ley de Benford, global y por usuario
python scripts/detectar_benford.py datos_ejemplo/asientos_benford_ejemplo.csv --grupo usuario_registro

# Registros fuera de horario (con un festivo de ejemplo)
python scripts/detectar_asientos_fuera_horario.py datos_ejemplo/asientos_horario_ejemplo.csv --festivos 2026-03-16
```

Cada script genera uno o más CSV con los resultados (`reporte_*.csv`).

### Resultado esperado con los datos de ejemplo

| Script | Qué detecta | Resultado |
|---|---|---|
| Usuarios | U1 ID de empleado · U2 correo · U3 nombre · U4 ID equivalente · U5 nombres parecidos | 3 · 2 · 4 · 1 · 1 coincidencias |
| Asientos duplicados | A1 documento repetido · A2 factura duplicada · A3 mismo importe, cuenta y fecha | 1 · 1 · 1 coincidencias |
| Benford | 2,300 importes; el usuario `RTORRES` concentra importes justo por debajo de 5,000 | Global: no conformidad (dígito 4 sobrerrepresentado). Por usuario: `RTORRES` destaca con diferencia |
| Fuera de horario | 23 registros; 7 marcados | `RTORRES` 4 de 8; `ALOPEZ`, `MGARCIA` y `JPEREZ` 1 cada uno |

> En el análisis por usuario de Benford, `MGARCIA` también supera el umbral por la variación natural de una muestra aleatoria: es un ejemplo de **falso positivo** y una razón para validar cada resultado con datos adicionales.

### Formato de los CSV

- **Usuarios:** `usuario`, `nombre_completo`, `correo`, `id_empleado` (los nombres de columna se pueden cambiar con `--col-usuario`, `--col-nombre`, `--col-correo` y `--col-empleado`).
- **Asientos duplicados:** obligatorias `sociedad`, `ejercicio`, `num_documento`, `cuenta`, `importe`, `moneda`; opcionales `referencia`, `fecha_documento`, `usuario_registro`.
- **Benford:** una columna de importes (`importe` por defecto, configurable con `--col-importe`) y, para el análisis por grupo, la columna que indique el grupo (por ejemplo `usuario_registro`).
- **Fuera de horario:** obligatorias `fecha_registro` y `hora_registro`; opcionales `num_documento`, `usuario_registro`, `importe`. Se aceptan los formatos de fecha AAAA-MM-DD, DD/MM/AAAA y AAAAMMDD, y de hora HH:MM:SS, HH:MM y HHMMSS.
- Si tus importes usan coma decimal, agrega `--separador-decimal ","`.

## Limitaciones

- Un resultado es un **indicio**, no un hallazgo: puede haber duplicados legítimos, cierres contables fuera de horario o importes que por naturaleza no siguen Benford (precios fijos, tarifas). Valida cada caso con el responsable.
- Benford requiere muchos datos (idealmente más de 1,000 importes). Con grupos pequeños usa la chi-cuadrada y no solo el MAD.
- Las pruebas son reglas simples y no sustituyen el juicio profesional ni un análisis completo.
- Las consultas SQL son ejemplos para PostgreSQL; adáptalas a tu motor y esquema.

## Uso responsable

Usa estas herramientas solo con datos que tengas autorización para analizar. No subas a este repositorio datos reales de ninguna organización; el `.gitignore` excluye la carpeta `datos_reales/` y los reportes generados como medida de protección.

## Ideas para ampliar

Pruebas de numeración con huecos, detección de montos redondos, importes justo debajo de límites de aprobación y revisión de accesos cruzada con la matriz de segregación de funciones.
