# Bitacora de Revision y Validacion Tecnica del SRS
**Proyecto:** Marco de Seguridad para protección de Integraciones API REST en Cadenas de Tiendas de Conveniencia  
**Materia:** TC5029 - Proyecto de ciberseguridad empresarial  
**Estudiante:** Luis Manuel Mendoza Cruz (A01797418)  
**Documento Auditado:** `docs/SRS_final.md` (Version 1.0.0-Final)  
**Rol del Revisor:** Auditor Tecnico de Seguridad de Software & Arquitecto de Requerimientos  
**Fecha de Auditoria:** Septiembre 2026  
**Resultado de Validacion:** APROBADO CON MODIFICACIONES INCORPORADAS  

---

## 1. Resumen Ejecutivo de la Revision

Se ha ejecutado una auditoria exhaustiva sobre la Especificacion de Requerimientos de Software (SRS) siguiendo las pautas de control de calidad de software y ciberseguridad industrial. 

El objetivo primordial fue asegurar que el documento cumpla con los principios rectores de:
1. **Verificabilidad:** Todo criterio de aceptacion debe ser medible mediante pruebas unitarias, de integracion o scripts automatizados.
2. **No Ambiguedad:** Los terminos deben tener una interpretacion tecnica unica, sin dejar margenes de duda entre el comportamiento de la interfaz y la API.
3. **Consistencia Logica:** No deben existir colisiones entre las reglas de negocio (ej. descuentos) y los vectores de prueba de seguridad (ej. Mass Assignment).
4. **Completitud y Cobertura (Threat Modeling):** Ningun vector planteado (BOLA, BFLA, SQLi, Mass Assignment, PII Harvesting, DoS y PCI-DSS) debe carecer de requerimiento o criterio trazable.

---

## 2. Hallazgos: Requerimientos Ambiguos o Contradictorios

### Hallazgo H-01: Ambiguedad en la Restriccion de Cobros con Carrito Vacio
* **Estado Inicial:** En las primeras notas de diseno se mencionaba que *"no se debe permitir cobrar sin productos"*, pero no se especificaba en que capa de la arquitectura residia la validacion.
* **Impacto en Seguridad:** Falla de integridad de datos y posible desincronizacion en inventario/arqueos.
* **Accion Correctiva:**  
  * Se formalizo el requerimiento **RF-12** y el criterio **RF-03-AC-1**.
  * Se definio doble barrera: la interfaz deshabilita visualmente el boton (`btn-disabled`), y el backend de FastAPI rechaza la peticion con codigo de estado `HTTP 400 Bad Request` o `HTTP 422 Unprocessable Entity` si la lista de items tiene longitud cero (`len(items) == 0`).

### Hallazgo H-02: Contradiccion Funcional en el Manejo de Descuentos
* **Estado Inicial:** Se planteaba que el cajero pudiera ingresar descuentos en caja y, simultaneamente, se disenaba el ataque de Mass Assignment para forzar un descuento del 100%. Si el sistema de negocio permitiese que el cajero aplique libremente cualquier porcentaje de descuento en la llamada legitima, el vector de ataque de Mass Assignment careceria de valor de explotacion demostrable.
* **Impacto en el Negocio:** Inconsistencia en la politica de segregacion de funciones (RBAC) y perdida de control sobre mermas financieras.
* **Accion Correctiva:**  
  * Se separaron las responsabilidades: el cajero opera por defecto con `discount_pct = 0.0` obligatorio.
  * Los descuentos discrecionales quedan clasificados como excepcion supervisada mediante el scope `sales:discount_override`, mientras que cualquier inyeccion externa no autorizada de `discount_pct` en la terminal del cajero es interceptada por el esquema DTO (`extra="forbid"`) con codigo `HTTP 422`.

---

## 3. Hallazgos: Criterios de Aceptacion No Verificables

### Hallazgo H-03: Imprecision Metrica ante Ataques de Denegacion de Servicio (DoS)
* **Estado Inicial:** La redaccion preliminar indicaba que *"el sistema debe ser rapido, tolerar carga y no caerse ante ataques masivos"*. Esta redaccion es subjetiva y no permite escribir una asercion binaria (*Pass/Fail*) en una suite de pruebas automatizadas con `pytest`.
* **Impacto:** Imposibilidad de evaluar objetivamente la resiliencia y el comportamiento del middleware en CI/CD.
* **Accion Correctiva:**  
  * Se reformulo el requerimiento **RNF-04** y se creo el criterio **RNF-04-AC-1**.
  * Se definieron variables empiricas cuantitativas: umbral de control de tasa de **10 req/s** por cliente/IP y validacion explicita del codigo de retorno **`HTTP 429 Too Many Requests`** con encabezado `Retry-After`.

### Hallazgo H-04: Falta de Criterio Cuantificable en la Proteccion de Tarjetas Bancarias
* **Estado Inicial:** Se establecia que *"las tarjetas bancarias deben ser seguras y no ser robadas por APIs"*. 
* **Impacto:** Carencia de alineacion con marcos normativos auditables de la industria financiera.
* **Accion Correctiva:**  
  * Se vinculo directamente con la norma **PCI-DSS v4.0 (Req. 3.2 y 4.1)** en los requerimientos **RD-01** y **RF-07**.
  * Se formalizo el criterio verificable **RF-07-AC-1**: comprobacion en base de datos de ausencia total del atributo `cvv`, y validacion mediante expresion regular del enmascaramiento estricto: `^\d{4}-XXXX-XXXX-\d{4}$`.

---

## 4. Gaps Detectados (Necesidades Faltantes y Omisiones Resueltas)

### Gap G-01: Ausencia de Trazabilidad Cruzada Cliente-Servidor (Observabilidad)
* **Descripcion de la Omision:** El sistema ejecutaba logs locales independientes, pero no existia un mecanismo para correlacionar una accion ejecutada en el navegador web con la traza de base de datos y la alerta en el panel de seguridad.
* **Solucion Incorporada:**  
  * Se integro el requerimiento **RF-11** y **RF-10**.
  * Se implemento un middleware que inyecta en cada ciclo de vida HTTP el encabezado estandar **`X-Correlation-ID`** (UUIDv4), propagandolo hacia el stream de eventos del `🛡️ API Sec Inspector`.

### Gap G-02: Falta de Distincion Formal entre BOLA y BFLA
* **Descripcion de la Omision:** Se contaba con la vulnerabilidad BOLA (acceso indebido a datos de otra tienda), pero no se abordaba la autorizacion a nivel de funcion critica (BFLA), lo cual dejaba un vacio en la cobertura del **OWASP API Security Top 10**.
* **Solucion Incorporada:**  
  * Se definio el flujo de **Devoluciones y Cancelaciones (Refunds)** en el requerimiento **RF-08**.
  * Se disenaron los criterios de aceptacion **RF-08-AC-1** (bloqueo `HTTP 403` a cajero no facultado) y **RF-08-AC-2** (autorizacion legitima con token de supervisor firmado con scope `sales:supervisor_override`).

### Gap G-03: Exposicion de Datos Personales (PII Harvesting)
* **Descripcion de la Omision:** El modulo de recargas telefonicas registraba los numeros en texto plano sin controles de privacidad, exponiendo a los clientes a recoleccion masiva para campanas de extorsion o spam.
* **Solucion Incorporada:**  
  * Se incorporo el requerimiento **RF-06** y el criterio **RF-06-AC-1**, estableciendo la ofuscacion irreversible en las salidas de la API (`55-****-1234`).

---

## 5. Matriz de Trazabilidad de Requerimientos vs. Pruebas de Aceptacion

| Requerimiento | ID de Criterio de Aceptacion | Endpoint Involucrado | Vector / Caso de Prueba | Archivo de Prueba Asociado |
| :--- | :--- | :--- | :--- | :--- |
| **RF-01** | `RF-01-AC-1` | `POST /api/v1/auth/login` | Emision y firma valida de JWT | `tests/test_api_security.py::test_rf_01_ac_1_login_jwt` |
| **RF-01** | `RF-01-AC-2` | `POST /api/v1/auth/login` | Fuerza bruta (Rate Limiting HTTP 429) | `tests/test_api_security.py::test_rf_01_ac_2_bruteforce` |
| **RF-02** | `RF-02-AC-1` | `POST /api/v1/users` | Rechazo de contrasena debil (NIST) | `tests/test_api_security.py::test_rf_02_ac_1_weak_password` |
| **RF-02** | `RF-02-AC-2` | `POST /api/v1/users` | Creacion exitosa con expiracion 90d | `tests/test_api_security.py::test_rf_02_ac_2_valid_user` |
| **RF-03** | `RF-03-AC-1` | `POST /api/v1/pos/transactions` | Bloqueo de cobro con carrito vacio | `tests/test_api_security.py::test_rf_03_ac_1_empty_cart` |
| **RF-04** | `RF-04-AC-1` | `POST /api/v1/pos/transactions` | Integridad de calculo en ticket | `tests/test_api_security.py::test_rf_04_ac_1_receipt_math` |
| **RF-05** | `RF-05-AC-1` | `GET /` (UI Frontend) | Aislamiento de modulo admin de logo | `tests/test_api_security.py::test_rf_05_ac_1_logo_rbac` |
| **RF-06** | `RF-06-AC-1` | `GET /api/v1/pos/recharges` | Ofuscacion de PII telefonica | `tests/test_api_security.py::test_rf_06_ac_1_pii_masking` |
| **RF-07** | `RF-07-AC-1` | `POST /api/v1/payments/card` | Tokenizacion y ausencia de CVV | `tests/test_api_security.py::test_rf_07_ac_1_pci_tokenization` |
| **RF-08** | `RF-08-AC-1` | `POST /api/v1/pos/transactions/{id}/refund` | Bloqueo BFLA (Cajero sin scope) | `tests/test_api_security.py::test_rf_08_ac_1_bfla_block` |
| **RF-08** | `RF-08-AC-2` | `POST /api/v1/pos/transactions/{id}/refund` | Autorizacion con token Supervisor | `tests/test_api_security.py::test_rf_08_ac_2_supervisor_refund` |
| **RNF-01** | `RNF-01-AC-1` | `POST /api/v1/pos/inject-discount` | Rechazo Mass Assignment (`extra="forbid"`) | `tests/test_api_security.py::test_rnf_01_ac_1_mass_assignment` |
| **RNF-02** | `RNF-02-AC-1` | `GET /api/v1/pos/products` | Sanitizacion de consultas SQLi | `tests/test_api_security.py::test_rnf_02_ac_1_sqli_neutralized` |
| **RNF-03** | `RNF-03-AC-1` | `GET /api/v1/stores/{id}/sales` | Aislamiento BOLA de sucursales | `tests/test_api_security.py::test_rnf_03_ac_1_bola_isolation` |
| **RNF-04** | `RNF-04-AC-1` | `GET /api/v1/pos/products` | Resiliencia y mitigacion DoS | `tests/test_api_security.py::test_rnf_04_ac_1_dos_rate_limit` |

---

## 6. Dictamen de Aprobacion

Una vez contrastadas las modificaciones sobre el documento maestro `SRS_final.md`, se dictamina que:
1. Todos los hallazgos y debilidades identificadas han sido mitigados a nivel documental.
2. Los requerimientos presentan una redaccion formal y libre de ambiguedades.
3. Se garantiza la correspondencia univoca entre las amenazas MITRE ATT&CK, los requerimientos IEEE 830 y los casos de prueba de aceptacion.

**Estado del entregable:** APROBADO para publicacion en repositorio Git y avance a fases de construccion de pruebas automatizadas.
