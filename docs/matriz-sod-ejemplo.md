# Matriz de segregación de funciones (SoD) · Ejemplo

Ejemplo ilustrativo de funciones incompatibles en un entorno SAP. Cada organización define su propia matriz según su estructura, tamaño y riesgos; úsala como punto de partida, no como lista definitiva.

**Cómo usarla:** obtén los roles asignados a cada usuario, identifica quién tiene ambas funciones de un conflicto y revisa si existe un control compensatorio aprobado.

| # | Función A | Función B | Riesgo si una misma persona tiene ambas | Transacciones de ejemplo | Severidad |
|---|---|---|---|---|---|
| 1 | Crear/modificar acreedores | Registrar facturas de proveedor | Crear un proveedor ficticio y registrarle facturas | XK01/XK02 · FB60/MIRO | Alta |
| 2 | Crear/modificar acreedores | Ejecutar pagos | Pagar a un proveedor ficticio o cambiar su cuenta bancaria y pagar | XK02 · F110/F-53 | Alta |
| 3 | Registrar facturas de proveedor | Ejecutar pagos | Registrar y pagar sin una segunda revisión | FB60/MIRO · F110/F-53 | Alta |
| 4 | Crear pedidos de compra | Registrar entrada de mercancías | Generar compras ficticias y confirmar su recepción | ME21N · MIGO | Alta |
| 5 | Registrar entrada de mercancías | Verificar facturas | Aprobar pagos sin una recepción independiente | MIGO · MIRO | Media |
| 6 | Crear pedidos de compra | Verificar facturas | Comprar y aprobar la factura sin contrapeso | ME21N · MIRO | Media |
| 7 | Mantener datos maestros de personal | Ejecutar la nómina | Dar de alta empleados ficticios o cambiar salarios y cuentas bancarias y pagar | PA30/PA40 · PC00_Mnn_CALC | Alta |
| 8 | Contabilizar asientos manuales | Abrir/cerrar periodos contables | Registrar asientos en periodos cerrados | FB50/FB01 · OB52 | Alta |
| 9 | Contabilizar asientos manuales | Mantener cuentas de mayor | Crear cuentas a medida para ocultar movimientos | FB50/FB01 · FS00 | Media |
| 10 | Crear/modificar deudores | Registrar abonos o cobros | Ocultar o desviar cobros mediante abonos a clientes propios | XD01/XD02 · FB75/F-28 | Alta |
| 11 | Administrar usuarios | Diseñar roles | Asignarse accesos sin control | SU01 · PFCG | Alta |
| 12 | Desarrollar programas | Importar transportes a producción | Pasar código no autorizado a producción | SE38/SE80 · STMS | Alta |
| 13 | Acceso funcional de negocio | Depurar o editar tablas directamente | Alterar datos eludiendo los controles del proceso | Roles funcionales · SE16N (edición) · /h | Alta |

## Controles compensatorios frecuentes

- Aprobación independiente de las transacciones críticas (flujo de liberación o doble verificación).
- Revisión periódica de reportes de actividad por una persona distinta.
- Límites por importe y alertas por operaciones inusuales.
- Acceso de emergencia (*firefighter*) con bitácora revisada.

> Un conflicto con control compensatorio documentado y operando no es lo mismo que un conflicto sin control. Registra ambos casos de forma distinta.
