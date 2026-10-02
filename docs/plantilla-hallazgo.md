# Plantilla de hallazgo de auditoría

Estructura de cinco elementos (criterio, condición, causa, efecto y recomendación) para documentar un hallazgo de forma clara y verificable.

---

## Plantilla

| Campo | Contenido |
|---|---|
| **ID** | H-001 |
| **Título** | Frase corta que resume el hallazgo |
| **Área o proceso** | Por ejemplo: gestión de accesos, cambios, respaldos |
| **Referencia** | Control o requisito aplicable (por ejemplo, ISO/IEC 27001:2022, 5.18) |
| **Criterio** | Qué debería cumplirse (política, norma o buena práctica) |
| **Condición** | Qué se encontró, con datos concretos y cantidades |
| **Causa** | Por qué ocurrió |
| **Efecto / riesgo** | Qué puede pasar o ya pasó por esta condición |
| **Evidencia** | Archivos, capturas, reportes o muestras que lo respaldan |
| **Recomendación** | Acción concreta, medible y asignable |
| **Calificación** | Alto · Medio · Bajo (con el criterio usado) |
| **Respuesta de la administración** | Postura del área auditada |
| **Responsable y fecha compromiso** | Nombre del cargo y fecha |
| **Estado** | Abierto · En proceso · Cerrado |

## Criterio de calificación (ejemplo)

| Nivel | Cuándo aplicarlo |
|---|---|
| Alto | Puede generar fraude, pérdida material o incumplimiento regulatorio y no hay control compensatorio. |
| Medio | Debilita un control importante, pero hay controles que mitigan parcialmente. |
| Bajo | Mejora de proceso o documentación sin impacto directo en el riesgo. |

---

## Ejemplo (datos ficticios)

| Campo | Contenido |
|---|---|
| **ID** | H-001 |
| **Título** | Usuarios duplicados asociados a un mismo empleado |
| **Área o proceso** | Gestión de identidades |
| **Referencia** | ISO/IEC 27001:2022, 5.16 y 5.18 |
| **Criterio** | Cada persona debe tener un único ID de usuario, salvo cuentas administrativas autorizadas y documentadas. |
| **Condición** | En el listado de usuarios de ejemplo (12 registros), 3 empleados tienen más de un usuario activo o bloqueado sin justificación documentada. Uno de ellos tiene además un usuario con nombre similar a otro empleado. |
| **Causa** | Las altas se solicitan por correo y no se valida si el empleado ya tiene un usuario. |
| **Efecto / riesgo** | Un empleado puede acumular accesos o eludir controles de segregación de funciones usando varios usuarios. |
| **Evidencia** | Reporte generado con `detectar_usuarios_duplicados.py` sobre `usuarios_ejemplo.csv`. |
| **Recomendación** | Validar contra RR.HH. antes de cada alta, dar de baja los usuarios duplicados no justificados y documentar las cuentas administrativas autorizadas. |
| **Calificación** | Medio |
| **Respuesta de la administración** | Pendiente |
| **Responsable y fecha compromiso** | Responsable de seguridad de la información · fecha por definir |
| **Estado** | Abierto |

> Recuerda que un resultado de los scripts es un indicio. Antes de convertirlo en hallazgo, confirma con el responsable del sistema.
