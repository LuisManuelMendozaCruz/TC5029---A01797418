# Bitácora de Revisión y Validación Técnica del SRS
**Proyecto:** Marco de Seguridad para protección de Integraciones API REST en Cadenas de Tiendas de Conveniencia  
**Materia:** TC5029 - Proyecto de ciberseguridad empresarial  
**Estudiante:** Luis Manuel Mendoza Cruz (Matrícula: A01797418)  
**Documento Auditado:** `docs/SRS_final.md` (Versión 1.0.0-Final)  
**Rol del Revisor:** Auditor Técnico de Seguridad de Software & Arquitecto de Requerimientos  
**Fecha de Auditoría:** Septiembre 2026  
**Resultado de Validación:** APROBADO CON MODIFICACIONES INCORPORADAS  

---

## 1. Resumen Ejecutivo de la Revisión

Se ha ejecutado una auditoría exhaustiva sobre la Especificación de Requerimientos de Software (SRS) siguiendo las pautas de control de calidad de software y ciberseguridad industrial. 

El objetivo primordial fue asegurar que el documento cumpla con los principios rectores de:
1. **Verificabilidad:** Todo criterio de aceptación debe ser medible mediante pruebas unitarias, de integración o scripts automatizados.
2. **No Ambigüedad:** Los términos deben tener una interpretación técnica única, sin dejar márgenes de duda entre el comportamiento de la interfaz y la API.
3. **Consistencia Lógica:** No deben existir colisiones entre las reglas de negocio (ej. descuentos) y los vectores de prueba de seguridad (ej. Mass Assignment).
4. **Completitud y Cobertura (Threat Modeling):** Ningún vector planteado (BOLA, BFLA, SQLi, Mass Assignment, PII Harvesting, DoS y PCI-DSS) debe carecer de requerimiento o criterio trazable.

---

## 2. Hallazgos: Requerimientos Ambiguos o Contradictorios

### Hallazgo H-01: Ambigüedad en la Restricción de Cobros con Carrito Vacío
* **Estado Inicial:** En las primeras notas de diseño se mencionaba que *"no se debe permitir cobrar sin productos"*, pero no se especificaba en qué capa de la arquitectura residía la validación.
* **Impacto en Seguridad:** Falla de integridad de datos y posible desincronización en inventario/arqueos.
* **Acción Correctiva:**  
  * Se formalizó el requerimiento **RF-12** y el criterio **RF-03-AC-1**.
  * Se definió doble barrera: la interfaz deshabilita visualmente el botón (`btn-disabled`), y el backend de FastAPI rechaza la petición con código de estado `HTTP 400 Bad Request` o `HTTP 422 Unprocessable Entity` si la lista de ítems tiene longitud cero (`len(items) == 0`).

### Hallazgo H-02: Contradicción Funcional en el Manejo de Descuentos
* **Estado Inicial:** Se planteaba que el cajero pudiera ingresar descuentos en caja y, simultáneamente, se diseñaba el ataque de Mass Assignment para forzar un descuento del 100%. Si el sistema de negocio permitiese que el cajero aplique libremente cualquier porcentaje de descuento en la llamada legítima, el vector de ataque de Mass Assignment carecería de valor de explotación demostrable.
* **Impacto en el Negocio:** Inconsistencia en la política de segregación de funciones (RBAC) y pérdida de control sobre mermas financieras.
* **Acción Correctiva:**  
  * Se separaron las responsabilidades: el cajero opera por defecto con `discount_pct = 0.0` obligatorio.
  * Los descuentos discrecionales quedan clasificados como excepción supervisada mediante el scope `sales:discount_override`, mientras que cualquier inyección externa no autorizada de `discount_pct` en la terminal del cajero es interceptada por el esquema DTO (`extra="forbid"`) con código `HTTP 422`.

---

## 3. Hallazgos: Criterios de Aceptación No Verificables

### Hallazgo H-03: Imprecisión Métrica ante Ataques de Denegación de Servicio (DoS)
* **Estado Inicial:** La redacción preliminar indicaba que *"el sistema debe ser rápido, tolerar carga y no caerse ante ataques masivos"*. Esta redacción es subjetiva y no permite escribir una aserción binaria (*Pass/Fail*) en una suite de pruebas automatizadas con `pytest`.
* **Impacto:** Imposibilidad de evaluar objetivamente la resiliencia y el comportamiento del middleware en CI/CD.
* **Acción Correctiva:**  
  * Se reformuló el requerimiento **RNF-04** y se creó el criterio **RNF-04-AC-1**.
  * Se definieron variables empíricas cuantitativas: umbral de control de tasa de **10 req/s** por cliente/IP y validación explícita del código de retorno **`HTTP 429 Too Many Requests`** con encabezado `Retry-After`.

### Hallazgo H-04: Falta de Criterio Cuantificable en la Protección de Tarjetas Bancarias
* **Estado Inicial:** Se establecía que *"las tarjetas bancarias deben ser seguras y no ser robadas por APIs"*. 
* **Impacto:** Carencia de alineación con marcos normativos auditables de la industria financiera.
* **Acción Correctiva:**  
  * Se vinculó directamente con la norma **PCI-DSS v4.0 (Req. 3.2 y 4.1)** en los requerimientos **RD-01** y **RF-07**.
  * Se formalizó el criterio verificable **RF-07-AC-1**: comprobación en base de datos de ausencia total del atributo `cvv`, y validación mediante expresión regular del enmascaramiento estricto: `^\d{4}-XXXX-XXXX-\d{4}$`.

---

## 4. Gaps Detectados (Necesidades Faltantes y Omisiones Resueltas)

### Gap G-01: Ausencia de Trazabilidad Cruzada Cliente-Servidor (Observabilidad)
* **Descripción de la Omisión:** El sistema ejecutaba logs locales independientes, pero no existía un mecanismo para correlacionar una acción ejecutada en el navegador web con la traza de base de datos y la alerta en el panel de seguridad.
* **Solución Incorporada:**  
  * Se integró el requerimiento **RF-11** y **RF-10**.
  * Se implementó un middleware que inyecta en cada ciclo de vida HTTP el encabezado estándar **`X-Correlation-ID`** (UUIDv4), propagándolo hacia el stream de eventos del `🛡️ API Sec Inspector`.

### Gap G-02: Falta de Distinción Formal entre BOLA y BFLA
* **Descripción de la Omisión:** Se contaba con la vulnerabilidad BOLA (acceso indebido a datos de otra tienda), pero no se abordaba la autorización a nivel de función crítica (BFLA), lo cual dejaba un vacío en la cobertura del **OWASP API Security Top 10**.
* **Solución Incorporada:**  
  * Se definió el flujo de **Devoluciones y Cancelaciones (Refunds)** en el requerimiento **RF-08**.
  * Se diseñaron los criterios de aceptación **RF-08-AC-1** (bloqueo `HTTP 403` a cajero no facultado) y **RF-08-AC-2** (autorización legítima con token de supervisor firmado con scope `sales:supervisor_override`).

### Gap G-03: Exposición de Datos Personales (PII Harvesting)
* **Descripción de la Omisión:** El módulo de recargas telefónicas registraba los números en texto plano sin controles de privacidad, exponiendo a los clientes a recolección masiva para campañas de extorsión o spam.
* **Solución Incorporada:**  
  * Se incorporó el requerimiento **RF-06** y el criterio **RF-06-AC-1**, estableciendo la ofuscación irreversible en las salidas de la API (`55-****-1234`).

---

## 5. Matriz de Trazabilidad de Requerimientos vs. Pruebas de Aceptación

| Requerimiento | ID de Criterio de Aceptación | Endpoint Involucrado | Vector / Caso de Prueba | Archivo de Prueba Asociado |
| :--- | :--- | :--- | :--- | :--- |
| **RF-01** | `RF-01-AC-1` | `POST /api/v1/auth/login` | Emisión y firma válida de JWT | `tests/test_api_security.py::test_rf_01_ac_1_login_jwt` |
| **RF-01** | `RF-01-AC-2` | `POST /api/v1/auth/login` | Fuerza bruta (Rate Limiting HTTP 429) | `tests/test_api_security.py::test_rf_01_ac_2_bruteforce` |
| **RF-02** | `RF-02-AC-1` | `POST /api/v1/users` | Rechazo de contraseña débil (NIST) | `tests/test_api_security.py::test_rf_02_ac_1_weak_password` |
| **RF-02** | `RF-02-AC-2` | `POST /api/v1/users` | Creación exitosa con expiración 90d | `tests/test_api_security.py::test_rf_02_ac_2_valid_user` |
| **RF-03** | `RF-03-AC-1` | `POST /api/v1/pos/transactions` | Bloqueo de cobro con carrito vacío | `tests/test_api_security.py::test_rf_03_ac_1_empty_cart` |
| **RF-04** | `RF-04-AC-1` | `POST /api/v1/pos/transactions` | Integridad de cálculo en ticket | `tests/test_api_security.py::test_rf_04_ac_1_receipt_math` |
| **RF-05** | `RF-05-AC-1` | `GET /` (UI Frontend) | Aislamiento de módulo admin de logo | `tests/test_api_security.py::test_rf_05_ac_1_logo_rbac` |
| **RF-06** | `RF-06-AC-1` | `GET /api/v1/pos/recharges` | Ofuscación de PII telefónica | `tests/test_api_security.py::test_rf_06_ac_1_pii_masking` |
| **RF-07** | `RF-07-AC-1` | `POST /api/v1/payments/card` | Tokenización y ausencia de CVV | `tests/test_api_security.py::test_rf_07_ac_1_pci_tokenization` |
| **RF-08** | `RF-08-AC-1` | `POST /api/v1/pos/transactions/{id}/refund` | Bloqueo BFLA (Cajero sin scope) | `tests/test_api_security.py::test_rf_08_ac_1_bfla_block` |
| **RF-08** | `RF-08-AC-2` | `POST /api/v1/pos/transactions/{id}/refund` | Autorización con token Supervisor | `tests/test_api_security.py::test_rf_08_ac_2_supervisor_refund` |
| **RNF-01** | `RNF-01-AC-1` | `POST /api/v1/pos/inject-discount` | Rechazo Mass Assignment (`extra="forbid"`) | `tests/test_api_security.py::test_rnf_01_ac_1_mass_assignment` |
| **RNF-02** | `RNF-02-AC-1` | `GET /api/v1/pos/products` | Sanitización de consultas SQLi | `tests/test_api_security.py::test_rnf_02_ac_1_sqli_neutralized` |
| **RNF-03** | `RNF-03-AC-1` | `GET /api/v1/stores/{id}/sales` | Aislamiento BOLA de sucursales | `tests/test_api_security.py::test_rnf_03_ac_1_bola_isolation` |
| **RNF-04** | `RNF-04-AC-1` | `GET /api/v1/pos/products` | Resiliencia y mitigación DoS | `tests/test_api_security.py::test_rnf_04_ac_1_dos_rate_limit` |

---

## 6. Dictamen de Aprobación

Una vez contrastadas las modificaciones sobre el documento maestro `SRS_final.md`, se dictamina que:
1. Todos los hallazgos y debilidades identificadas han sido mitigados a nivel documental.
2. Los requerimientos presentan una redacción formal y libre de ambigüedades.
3. Se garantiza la correspondencia unívoca entre las amenazas MITRE ATT&CK, los requerimientos IEEE 830 y los casos de prueba de aceptación.

**Estado del entregable:** APROBADO para publicación en repositorio Git y avance a fases de construcción de pruebas automatizadas.
