# Transacciones SAP relevantes para auditoría de TI

Guía de consulta con dos partes:

1. **Transacciones críticas** que deberían estar restringidas a perfiles de administración, seguridad o Basis.
2. **Transacciones contables y de nómina de uso común**, con notas sobre qué revisar.

> **Aviso:** lista orientativa basada en prácticas comunes de auditoría y en la documentación pública de SAP. No es exhaustiva. Los nombres y la disponibilidad de algunas transacciones cambian entre ECC y S/4HANA (por ejemplo, en S/4HANA la gestión de acreedores y deudores se concentra en la transacción **BP**). Valida siempre contra el sistema y el concepto de autorizaciones de la organización auditada.

---

## Parte 1. Transacciones que solo deberían tener usuarios administradores

"Restringidas" no significa que nadie pueda usarlas, sino que se asignan a pocas personas, con justificación, y en producción idealmente solo mediante acceso de emergencia (*firefighter*) con bitácora y revisión posterior.

### Administración de usuarios y autorizaciones

| Transacción | Nombre | Por qué restringirla |
|---|---|---|
| SU01 | Mantenimiento de usuarios | Permite crear usuarios, resetear contraseñas, bloquear/desbloquear y asignar roles. Quien la controla puede darse o dar acceso a cualquiera. |
| SU10 | Mantenimiento masivo de usuarios | Las mismas acciones que SU01, pero en lote: un error o abuso afecta a muchos usuarios a la vez. |
| PFCG | Mantenimiento de roles | Define qué transacciones y datos puede usar cada rol. Quien modifica roles puede ampliar sus propios permisos. |
| SU21 | Mantenimiento de objetos de autorización | Modifica los objetos y campos sobre los que se basan las validaciones de seguridad. |
| SU24 | Valores propuestos de autorización | Cambia los valores que alimentan la generación de roles y puede introducir permisos excesivos. |
| SUIM | Sistema de información de usuarios | Es de consulta, pero revela el mapa completo de usuarios, roles y accesos. Limitar a seguridad y auditoría. |

### Acceso a datos y desarrollo

| Transacción | Nombre | Por qué restringirla |
|---|---|---|
| SE16 / SE16N | Visor de tablas | Lectura directa de cualquier tabla (nómina, datos bancarios, maestros) sin pasar por los controles de las transacciones funcionales. En algunas configuraciones permite editar. |
| SM30 / SM31 | Mantenimiento de vistas de tablas | Modifica tablas de configuración y parámetros sin pasar por el control de cambios. |
| SE38 | Editor ABAP | Crear o modificar programas; un programa propio puede leer o alterar cualquier dato. |
| SA38 | Ejecución de programas ABAP | Ejecuta cualquier reporte directamente, sin pasar por el menú. Se controla con el objeto S_PROGRAM. |
| SE37 | Módulos de función | Ejecutar y modificar módulos con efecto directo sobre datos y procesos. |
| SE80 | Object Navigator | Entorno de desarrollo completo; en producción no debería usarse para modificar objetos. |
| SE11 | Diccionario ABAP | Cambia estructuras de tablas y dominios; riesgo para la integridad de los datos. |
| SE93 | Mantenimiento de códigos de transacción | Permite crear transacciones propias que apunten a programas y eludan los menús. |
| /h | Depurador (comando) | Con autorización de depuración y cambio de valores se pueden alterar datos y saltar validaciones en tiempo de ejecución (objeto S_DEVELOP). |

### Configuración, transportes y sistema

| Transacción | Nombre | Por qué restringirla |
|---|---|---|
| SPRO | Personalización (IMG) | Acceso a la configuración del sistema; un cambio afecta a todos los procesos. |
| SCC4 | Configuración de mandantes | Define si un mandante admite cambios; en producción debe estar protegido contra modificaciones. |
| SCC5 | Borrado de mandantes | Elimina un mandante completo. |
| SE06 | Configuración del Transport Organizer | Permite cambiar la modificabilidad del sistema (abrir o cerrar). |
| SE01 / SE09 / SE10 | Transport Organizer | Crear y liberar órdenes de transporte; base del control de cambios. |
| STMS | Sistema de gestión de transportes | Importa transportes a producción; quien lo controla puede pasar cambios no autorizados. |
| SM01 | Bloquear/desbloquear transacciones | Puede desactivar transacciones que funcionan como control. |
| SM59 | Destinos RFC | Conexiones con otros sistemas; pueden contener credenciales y abrir accesos entre sistemas. |
| SM49 / SM69 | Comandos externos | Ejecutan comandos del sistema operativo desde SAP. |
| RZ10 / RZ11 | Parámetros de perfil | Modifican parámetros de seguridad (longitud y complejidad de contraseñas, bloqueos por intentos, entre otros). |
| SM36 / SM37 | Jobs en segundo plano | Programan y administran procesos que se ejecutan con los permisos de otro usuario. |
| SM19 / SM20 | Registro de auditoría de seguridad | Configurar o desactivar el log oculta rastros; restringir la configuración (SM19) y proteger el análisis (SM20). |
| AL11 | Directorios del servidor | Lectura de archivos del servidor (interfaces, archivos bancarios, nómina). |
| PU00 | Borrado de datos de personal | Elimina datos de personal de forma masiva; muy crítica. |

### Objetos de autorización relacionados

| Objeto | Qué controla |
|---|---|
| S_TCODE | Qué transacciones puede iniciar un usuario |
| S_USER_GRP / S_USER_AGR / S_USER_PRO | Administración de usuarios, roles y perfiles |
| S_TABU_DIS / S_TABU_NAM | Acceso a tablas (por grupo de autorización o por nombre) |
| S_DEVELOP | Desarrollo y depuración |
| S_PROGRAM | Ejecución de programas |
| S_TRANSPRT | Transportes |
| S_BTCH_ADM | Administración de jobs |
| S_LOG_COM | Comandos externos |
| S_RFC | Llamadas RFC |

---

## Parte 2. Transacciones más comunes en contabilidad, finanzas y nómina

La columna de notas indica qué suele revisar un auditor. Las marcadas con **(sensible)** conviene validarlas contra la matriz de segregación de funciones.

### Contabilidad general (FI-GL)

| Transacción | Descripción | Nota para el auditor |
|---|---|---|
| FB50 | Contabilizar asiento de cuenta de mayor (simplificado) | Vía habitual de asientos manuales. Revisar quién puede registrarlos y los límites de aprobación. |
| FB01 | Contabilizar documento (general) | Asientos manuales de cualquier tipo. |
| F-02 | Asiento general (pantalla clásica) | Equivalente funcional a FB01. |
| FBV0 | Contabilizar documento preliminar | Liberación de documentos pre-registrados. Verificar que quien registra no libere sus propios documentos. |
| FB02 | Modificar documento | Solo permite campos no críticos. Revisar el historial de cambios. |
| FB03 | Visualizar documento | Consulta; base para pruebas por muestreo. |
| FB08 | Anular documento | Revisar anulaciones cercanas al cierre y quién las realiza. |
| F.80 | Anulación masiva de documentos | Alto impacto; restringir **(sensible)**. |
| F-03 | Compensar cuenta de mayor | Revisar partidas compensadas manualmente. |
| FBRA | Resetear compensación | Deshace compensaciones; restringir **(sensible)**. |
| FS00 | Mantenimiento de cuentas de mayor | Crear o modificar cuentas del plan contable **(sensible)**. |
| OB52 | Abrir/cerrar periodos contables | Controla en qué periodos se puede contabilizar **(sensible)**. |
| FS10N | Saldos de cuentas de mayor | Consulta; útil para conciliaciones. |
| FAGLL03 / FBL3N | Partidas individuales de cuentas de mayor | Consulta para analítica de datos. |
| F.01 | Estados financieros | Balance y estado de resultados. |

### Cuentas por pagar y compras

| Transacción | Descripción | Nota para el auditor |
|---|---|---|
| FB60 | Registrar factura de acreedor | Probar duplicados (ver `scripts/detectar_asientos_duplicados.py`). |
| MIRO | Verificación de facturas (logística) | Revisar tolerancias y bloqueos de pago. |
| FB65 | Abono de acreedor | Revisar quién lo registra y su aprobación. |
| F-53 | Contabilizar pago saliente | Separar de la creación de acreedores **(sensible)**. |
| F110 | Proceso automático de pagos | Alto riesgo; separar de la administración del maestro de acreedores **(sensible)**. |
| F-44 | Compensar acreedor | Revisar compensaciones manuales. |
| FBL1N | Partidas individuales de acreedor | Base para pruebas de duplicados y antigüedad. |
| XK01 / FK01 | Crear acreedor | Maestro de proveedores **(sensible)**. |
| XK02 / FK02 | Modificar acreedor | Los cambios de cuenta bancaria son de alto riesgo **(sensible)**. |
| ME21N | Crear pedido de compra | Revisar límites de aprobación y liberación. |
| MIGO | Movimientos de mercancías | Separar de pedido y de verificación de factura. |

### Cuentas por cobrar y ventas

| Transacción | Descripción | Nota para el auditor |
|---|---|---|
| FB70 | Registrar factura de deudor | Revisar facturas manuales fuera del flujo de ventas. |
| FB75 | Abono de deudor | Revisar abonos y su aprobación. |
| VF01 | Crear documento de facturación (SD) | Flujo estándar de facturación. |
| F-28 | Contabilizar cobro entrante | Separar de la administración del maestro de deudores. |
| F-32 | Compensar deudor | Revisar compensaciones manuales. |
| FBL5N | Partidas individuales de deudor | Antigüedad de saldos y análisis de cobranza. |
| XD01 / FD01 | Crear deudor | Maestro de clientes **(sensible)**. |
| XD02 / FD02 | Modificar deudor | Límites de crédito y condiciones de pago **(sensible)**. |

### Activos fijos

| Transacción | Descripción | Nota para el auditor |
|---|---|---|
| AS01 | Crear maestro de activo fijo | Revisar altas sin documentación soporte. |
| F-90 | Adquisición de activo con proveedor | Conciliar con compras. |
| ABZON | Alta de activo con contrapartida automática | Altas sin factura de por medio. |
| ABAVN | Baja de activo por desecho | Revisar autorización de bajas. |
| F-92 | Baja de activo con venta a cliente | Revisar resultado por venta. |
| AFAB | Ejecución de amortizaciones | Alto impacto en el cierre; revisar parámetros. |
| AW01N | Consulta de activos (Asset Explorer) | Consulta. |

### Controlling

| Transacción | Descripción | Nota para el auditor |
|---|---|---|
| KS01 | Crear centro de coste | Revisar altas y asignaciones. |
| KSB1 | Partidas individuales de centro de coste | Consulta para análisis de gastos. |
| KO88 | Liquidación de órdenes internas | Traslada costos entre objetos; revisar liquidaciones manuales. |

### Nómina y personal (HCM)

| Transacción | Descripción | Nota para el auditor |
|---|---|---|
| PA30 | Mantener datos maestros de personal | Incluye salario y cuenta bancaria **(sensible)**. |
| PA20 | Visualizar datos maestros de personal | Confidencialidad; restringir por área de personal. |
| PA40 | Medidas de personal (altas, bajas, cambios) | Revisar altas sin documentación y cambios de salario. |
| PC00_Mnn_CALC | Controlador de nómina (nn = agrupación de países; por ejemplo, M37 para México, confirmar) | Separar de la administración de datos maestros **(sensible)**. |
| PU03 | Cambiar estado de control de nómina | Permite reabrir periodos ya calculados **(sensible)**. |
| PC_PAYRESULT | Visualizar resultados de nómina | Consulta; confidencialidad. |
| PC00_M99_CIPE | Contabilización de nómina en FI | Conciliar nómina contra contabilidad. |

---

## Cómo usar esta guía en una revisión

1. Obtén la lista de usuarios con acceso a las transacciones de la Parte 1 (por ejemplo, con SUIM o cruzando las tablas de roles y asignaciones; confirma los nombres según la versión).
2. Compárala con la lista de administradores autorizados y con la justificación de cada acceso.
3. Verifica que en producción el acceso sea de emergencia, con bitácora y revisión posterior.
4. Para la Parte 2, cruza los accesos contra la matriz de segregación de funciones (`matriz-sod-ejemplo.md`).
5. Documenta las excepciones con la plantilla `plantilla-hallazgo.md`.
