-- =====================================================================
-- consultas_sql_duplicados.sql
-- Consultas de ejemplo (PostgreSQL) para detectar usuarios y registros
-- contables duplicados. Equivalen a las pruebas de los scripts en Python.
--
-- Tablas supuestas (todas las columnas de tipo texto, salvo importe):
--   usuarios(usuario, nombre_completo, correo, id_empleado)
--   asientos(sociedad, ejercicio, num_documento, cuenta, referencia,
--            importe NUMERIC(15,2), moneda, fecha_documento, usuario_registro)
--
-- Un resultado es un INDICIO, no un hallazgo: valida cada caso.
-- =====================================================================


-- ---------------------------------------------------------------------
-- U1. Mismo ID de empleado en varios usuarios
-- ---------------------------------------------------------------------
SELECT id_empleado,
       COUNT(DISTINCT usuario)                         AS num_usuarios,
       STRING_AGG(DISTINCT usuario, ', ' ORDER BY usuario) AS usuarios
FROM   usuarios
WHERE  COALESCE(TRIM(id_empleado), '') <> ''
GROUP  BY id_empleado
HAVING COUNT(DISTINCT usuario) > 1;


-- ---------------------------------------------------------------------
-- U2. Mismo correo en varios usuarios (sin distinguir mayúsculas)
-- ---------------------------------------------------------------------
SELECT LOWER(TRIM(correo))                             AS correo,
       COUNT(DISTINCT usuario)                         AS num_usuarios,
       STRING_AGG(DISTINCT usuario, ', ' ORDER BY usuario) AS usuarios
FROM   usuarios
WHERE  COALESCE(TRIM(correo), '') <> ''
GROUP  BY LOWER(TRIM(correo))
HAVING COUNT(DISTINCT usuario) > 1;


-- ---------------------------------------------------------------------
-- U3. Mismo nombre completo en varios usuarios
-- (Para ignorar acentos: CREATE EXTENSION unaccent; y usar unaccent(...))
-- ---------------------------------------------------------------------
SELECT LOWER(TRIM(nombre_completo))                    AS nombre,
       COUNT(DISTINCT usuario)                         AS num_usuarios,
       STRING_AGG(DISTINCT usuario, ', ' ORDER BY usuario) AS usuarios
FROM   usuarios
WHERE  COALESCE(TRIM(nombre_completo), '') <> ''
GROUP  BY LOWER(TRIM(nombre_completo))
HAVING COUNT(DISTINCT usuario) > 1;


-- ---------------------------------------------------------------------
-- U4. IDs de usuario equivalentes ("J.PEREZ" y "JPEREZ")
-- ---------------------------------------------------------------------
SELECT REGEXP_REPLACE(LOWER(usuario), '[^a-z0-9]', '', 'g') AS usuario_normalizado,
       COUNT(DISTINCT usuario)                              AS num_usuarios,
       STRING_AGG(DISTINCT usuario, ', ' ORDER BY usuario)  AS usuarios
FROM   usuarios
GROUP  BY REGEXP_REPLACE(LOWER(usuario), '[^a-z0-9]', '', 'g')
HAVING COUNT(DISTINCT usuario) > 1;


-- ---------------------------------------------------------------------
-- A1. Número de documento repetido
-- ---------------------------------------------------------------------
SELECT sociedad, ejercicio, num_documento, COUNT(*) AS veces
FROM   asientos
GROUP  BY sociedad, ejercicio, num_documento
HAVING COUNT(*) > 1;


-- ---------------------------------------------------------------------
-- A2. Posible factura duplicada: misma sociedad, cuenta, referencia,
--     importe y moneda en documentos distintos
-- ---------------------------------------------------------------------
SELECT sociedad,
       cuenta,
       REGEXP_REPLACE(UPPER(referencia), '[\s\-_/.]', '', 'g') AS referencia_normalizada,
       importe,
       moneda,
       COUNT(DISTINCT ejercicio || '/' || num_documento) AS num_documentos,
       STRING_AGG(DISTINCT ejercicio || '/' || num_documento, ', ') AS documentos
FROM   asientos
WHERE  COALESCE(TRIM(referencia), '') <> ''
GROUP  BY sociedad, cuenta,
          REGEXP_REPLACE(UPPER(referencia), '[\s\-_/.]', '', 'g'),
          importe, moneda
HAVING COUNT(DISTINCT ejercicio || '/' || num_documento) > 1;


-- ---------------------------------------------------------------------
-- A3. Mismo importe, cuenta y fecha del documento (referencias distintas)
-- ---------------------------------------------------------------------
SELECT sociedad, cuenta, importe, moneda, fecha_documento,
       COUNT(DISTINCT ejercicio || '/' || num_documento) AS num_documentos,
       STRING_AGG(DISTINCT ejercicio || '/' || num_documento, ', ') AS documentos,
       STRING_AGG(DISTINCT referencia, ', ') AS referencias
FROM   asientos
GROUP  BY sociedad, cuenta, importe, moneda, fecha_documento
HAVING COUNT(DISTINCT ejercicio || '/' || num_documento) > 1
   AND COUNT(DISTINCT REGEXP_REPLACE(UPPER(COALESCE(referencia, '')), '[\s\-_/.]', '', 'g')) > 1;


-- ---------------------------------------------------------------------
-- Referencia: facturas de proveedor duplicadas sobre tablas estándar de SAP
-- (partidas abiertas BSIK y compensadas BSAK). Es un esquema orientativo:
-- valida nombres de campos y volumen de datos en tu entorno de pruebas.
--   BUKRS = sociedad, LIFNR = acreedor, XBLNR = referencia,
--   WRBTR = importe en moneda del documento, WAERS = moneda,
--   BELNR = nº de documento, GJAHR = ejercicio.
-- ---------------------------------------------------------------------
-- SELECT bukrs, lifnr, xblnr, wrbtr, waers,
--        COUNT(DISTINCT belnr || gjahr) AS num_documentos
-- FROM (
--     SELECT bukrs, lifnr, xblnr, wrbtr, waers, belnr, gjahr FROM bsik
--     UNION ALL
--     SELECT bukrs, lifnr, xblnr, wrbtr, waers, belnr, gjahr FROM bsak
-- ) t
-- WHERE xblnr <> ''
-- GROUP BY bukrs, lifnr, xblnr, wrbtr, waers
-- HAVING COUNT(DISTINCT belnr || gjahr) > 1;


-- =====================================================================
-- PRUEBAS ADICIONALES (PostgreSQL)
-- Suponen en "asientos" las columnas: fecha_registro DATE y hora_registro TIME
-- (en SAP, los campos de captura suelen ser CPUDT y CPUTM de la cabecera).
-- =====================================================================

-- ---------------------------------------------------------------------
-- B1. Ley de Benford: distribución del primer dígito de los importes
-- ---------------------------------------------------------------------
WITH d AS (
    SELECT SUBSTRING(REGEXP_REPLACE(ABS(importe)::text, '^[0.]+', '') FROM 1 FOR 1)::int AS digito
    FROM   asientos
    WHERE  importe <> 0
),
c AS (
    SELECT digito, COUNT(*) AS n FROM d GROUP BY digito
)
SELECT digito,
       n AS observados,
       ROUND(100.0 * n / SUM(n) OVER (), 2)   AS observado_pct,
       ROUND(100 * LOG(1 + 1.0 / digito), 2)  AS esperado_pct
FROM   c
ORDER  BY digito;


-- ---------------------------------------------------------------------
-- H1/H2. Registros en fin de semana o fuera del horario laboral (08:00-19:00)
-- ---------------------------------------------------------------------
SELECT num_documento, usuario_registro, fecha_registro, hora_registro, importe,
       CASE
           WHEN EXTRACT(ISODOW FROM fecha_registro) IN (6, 7)
                AND (hora_registro < TIME '08:00' OR hora_registro >= TIME '19:00')
                THEN 'día no laboral; fuera de horario'
           WHEN EXTRACT(ISODOW FROM fecha_registro) IN (6, 7) THEN 'día no laboral'
           ELSE 'fuera de horario'
       END AS motivo
FROM   asientos
WHERE  EXTRACT(ISODOW FROM fecha_registro) IN (6, 7)
   OR  hora_registro < TIME '08:00'
   OR  hora_registro >= TIME '19:00'
ORDER  BY usuario_registro, fecha_registro, hora_registro;


-- ---------------------------------------------------------------------
-- H4. Resumen por usuario: porcentaje de registros fuera de horario
-- ---------------------------------------------------------------------
SELECT usuario_registro,
       COUNT(*) AS registros,
       COUNT(*) FILTER (WHERE EXTRACT(ISODOW FROM fecha_registro) IN (6, 7)
                           OR hora_registro < TIME '08:00'
                           OR hora_registro >= TIME '19:00') AS marcados,
       ROUND(100.0 * COUNT(*) FILTER (WHERE EXTRACT(ISODOW FROM fecha_registro) IN (6, 7)
                                         OR hora_registro < TIME '08:00'
                                         OR hora_registro >= TIME '19:00') / COUNT(*), 1) AS pct_marcado
FROM   asientos
GROUP  BY usuario_registro
ORDER  BY marcados DESC;
