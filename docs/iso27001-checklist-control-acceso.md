# Checklist de auditoría ISO/IEC 27001:2022 · Acceso y operación de TI

Lista de verificación para revisar controles del Anexo A relacionados con accesos, registros, cambios y continuidad. La numeración corresponde a ISO/IEC 27001:2022 (Anexo A). **Las descripciones están redactadas con mis propias palabras**; para el texto oficial de la norma, consúltala en su versión autorizada.

**Cómo usarla:** por cada control, solicita la evidencia, aplica la prueba y marca el resultado: Cumple · Parcial · No cumple · No aplica.

| Ref. | Control | Qué verificar | Evidencia a solicitar | Resultado |
|---|---|---|---|---|
| 5.3 | Segregación de funciones | Existen reglas que impiden que una misma persona concentre funciones incompatibles y se revisan los conflictos. | Matriz de segregación, reporte de conflictos, excepciones aprobadas | ☐ |
| 5.15 | Control de acceso | Hay una política de acceso aprobada, comunicada y revisada, basada en necesidad de negocio. | Política vigente, fecha de revisión y aprobación | ☐ |
| 5.16 | Gestión de identidades | Cada persona tiene un ID único, no hay cuentas compartidas y las bajas se ejecutan. | Listado de usuarios contra nómina de RR.HH.; resultados de `detectar_usuarios_duplicados.py` | ☐ |
| 5.17 | Información de autenticación | Existen reglas de contraseñas y se entregan de forma segura. | Configuración de parámetros de contraseña, procedimiento de entrega | ☐ |
| 5.18 | Derechos de acceso | Altas, cambios y bajas se autorizan y se revisan periódicamente. | Muestra de solicitudes de acceso, evidencia de la última revisión de accesos | ☐ |
| 8.2 | Derechos de acceso privilegiado | Los accesos privilegiados son pocos, justificados y el uso de emergencia queda registrado. | Lista de usuarios privilegiados, bitácora de accesos de emergencia | ☐ |
| 8.3 | Restricción de acceso a la información | El acceso a datos sensibles se limita a quien lo necesita. | Roles con acceso a tablas y datos sensibles | ☐ |
| 8.5 | Autenticación segura | Hay controles como autenticación multifactor en accesos remotos o privilegiados y bloqueo por intentos fallidos. | Configuración de MFA y de bloqueos | ☐ |
| 8.8 | Gestión de vulnerabilidades técnicas | Se identifican y corrigen vulnerabilidades y se aplican parches con un proceso definido. | Reportes de escaneo, calendario de parches | ☐ |
| 8.13 | Respaldo de la información | Los respaldos se hacen según lo planeado y se prueba la restauración. | Calendario de respaldos, evidencia de pruebas de restauración | ☐ |
| 8.15 | Registro de eventos | Los registros relevantes están activos, protegidos contra alteración y se conservan. | Configuración del log de auditoría, política de retención | ☐ |
| 8.16 | Actividades de monitoreo | Se revisan registros y alertas y se da seguimiento a las anomalías. | Evidencia de revisiones periódicas, tickets de seguimiento | ☐ |
| 8.31 | Separación de entornos | Desarrollo, pruebas y producción están separados y con accesos distintos. | Diagrama de entornos, accesos por entorno | ☐ |
| 8.32 | Gestión de cambios | Los cambios se solicitan, prueban, aprueban y se pasan a producción de forma controlada. | Muestra de cambios con solicitud, pruebas y aprobación | ☐ |
| 5.19 | Seguridad con proveedores | Los proveedores con acceso a información o sistemas tienen requisitos de seguridad acordados. | Contratos o acuerdos, lista de proveedores críticos | ☐ |
| 5.24 | Planificación de gestión de incidentes | Existe un proceso definido para reportar y atender incidentes de seguridad. | Procedimiento de incidentes, roles, ejemplos recientes | ☐ |
| 5.30 | Preparación de TIC para la continuidad | Hay planes y pruebas para recuperar los sistemas críticos. | Plan de continuidad, resultados de pruebas | ☐ |
| 8.34 | Protección de sistemas durante pruebas de auditoría | Las pruebas del auditor se planean para no afectar la operación (acceso de solo lectura, ventanas acordadas). | Plan de auditoría, accesos otorgados al equipo auditor | ☐ |

## Cómo documentar el resultado

- **Cumple:** la evidencia confirma que el control opera como se describe.
- **Parcial:** el control existe, pero con excepciones o evidencia incompleta.
- **No cumple:** no existe el control o la evidencia muestra que no opera.
- **No aplica:** se justifica por escrito por qué no corresponde.

Registra cada excepción relevante con la plantilla `plantilla-hallazgo.md`.
