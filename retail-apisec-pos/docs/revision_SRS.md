# BitÃ¡cora de RevisiÃ³n y ValidaciÃ³n TÃ©cnica del SRS
**Proyecto:** Marco de Seguridad para protecciÃ³n de Integraciones API REST en Cadenas de Tiendas de Conveniencia  
**Materia:** TC5029 - Proyecto de ciberseguridad empresarial  
**Estudiante:** Luis Manuel Mendoza Cruz (MatrÃ­cula: A01797418)  
**Documento Auditado:** `docs/SRS_final.md` (VersiÃ³n 1.0.0-Final)  
**Rol del Revisor:** Auditor TÃ©cnico de Seguridad de Software & Arquitecto de Requerimientos  
**Fecha de AuditorÃ­a:** Septiembre 2026  
**Resultado de ValidaciÃ³n:** APROBADO CON MODIFICACIONES INCORPORADAS  

---

## 1. Resumen Ejecutivo de la RevisiÃ³n

Se ha ejecutado una auditorÃ­a exhaustiva sobre la EspecificaciÃ³n de Requerimientos de Software (SRS) siguiendo las pautas de control de calidad de software y ciberseguridad industrial. 

El objetivo primordial fue asegurar que el documento cumpla con los principios rectores de:
1. **Verificabilidad:** Todo criterio de aceptaciÃ³n debe ser medible mediante pruebas unitarias, de integraciÃ³n o scripts automatizados.
2. **No AmbigÃ¼edad:** Los tÃ©rminos deben tener una interpretaciÃ³n tÃ©cnica Ãºnica, sin dejar mÃ¡rgenes de duda entre el comportamiento de la interfaz y la API.
3. **Consistencia LÃ³gica:** No deben existir colisiones entre las reglas de negocio (ej. descuentos) y los vectores de prueba de seguridad (ej. Mass Assignment).
4. **Completitud y Cobertura (Threat Modeling):** NingÃºn vector planteado (BOLA, BFLA, SQLi, Mass Assignment, PII Harvesting, DoS y PCI-DSS) debe carecer de requerimiento o criterio trazable.

---

## 2. Hallazgos: Requerimientos Ambiguos o Contradictorios

### Hallazgo H-01: AmbigÃ¼edad en la RestricciÃ³n de Cobros con Carrito VacÃ­o
* **Estado Inicial:** En las primeras notas de diseÃ±o se mencionaba que *"no se debe permitir cobrar sin productos"*, pero no se especificaba en quÃ© capa de la arquitectura residÃ­a la validaciÃ³n.
* **Impacto en Seguridad:** Falla de integridad de datos y posible desincronizaciÃ³n en inventario/arqueos.
* **AcciÃ³n Correctiva:**  
  * Se formalizÃ³ el requerimiento **RF-12** y el criterio **RF-03-AC-1**.
  * Se definiÃ³ doble barrera: la interfaz deshabilita visualmente el botÃ³n (`btn-disabled`), y el backend de FastAPI rechaza la peticiÃ³n con cÃ³digo de estado `HTTP 400 Bad Request` o `HTTP 422 Unprocessable Entity` si la lista de Ã­tems tiene longitud cero (`len(items) == 0`).

### Hallazgo H-02: ContradicciÃ³n Funcional en el Manejo de Descuentos
* **Estado Inicial:** Se planteaba que el cajero pudiera ingresar descuentos en caja y, simultÃ¡neamente, se diseÃ±aba el ataque de Mass Assignment para forzar un descuento del 100%. Si el sistema de negocio permitiese que el cajero aplique libremente cualquier porcentaje de descuento en la llamada legÃ­tima, el vector de ataque de Mass Assignment carecerÃ­a de valor de explotaciÃ³n demostrable.
* **Impacto en el Negocio:** Inconsistencia en la polÃ­tica de segregaciÃ³n de funciones (RBAC) y pÃ©rdida de control sobre mermas financieras.
* **AcciÃ³n Correctiva:**  
  * Se separaron las responsabilidades: el cajero opera por defecto con `discount_pct = 0.0` obligatorio.
  * Los descuentos discrecionales quedan clasificados como excepciÃ³n supervisada mediante el scope `sales:discount_override`, mientras que cualquier inyecciÃ³n externa no autorizada de `discount_pct` en la terminal del cajero es interceptada por el esquema DTO (`extra="forbid"`) con cÃ³digo `HTTP 422`.

---

## 3. Hallazgos: Criterios de AceptaciÃ³n No Verificables

### Hallazgo H-03: ImprecisiÃ³n MÃ©trica ante Ataques de DenegaciÃ³n de Servicio (DoS)
* **Estado Inicial:** La redacciÃ³n preliminar indicaba que *"el sistema debe ser rÃ¡pido, tolerar carga y no caerse ante ataques masivos"*. Esta redacciÃ³n es subjetiva y no permite escribir una aserciÃ³n binaria (*Pass/Fail*) en una suite de pruebas automatizadas con `pytest`.
* **Impacto:** Imposibilidad de evaluar objetivamente la resiliencia y el comportamiento del middleware en CI/CD.
* **AcciÃ³n Correctiva:**  
  * Se reformulÃ³ el requerimiento **RNF-04** y se creÃ³ el criterio **RNF-04-AC-1**.
  * Se definieron variables empÃ­ricas cuantitativas: umbral de control de tasa de **10 req/s** por cliente/IP y validaciÃ³n explÃ­cita del cÃ³digo de retorno **`HTTP 429 Too Many Requests`** con encabezado `Retry-After`.

### Hallazgo H-04: Falta de Criterio Cuantificable en la ProtecciÃ³n de Tarjetas Bancarias
* **Estado Inicial:** Se establecÃ­a que *"las tarjetas bancarias deben ser seguras y no ser robadas por APIs"*. 
* **Impacto:** Carencia de alineaciÃ³n con marcos normativos auditables de la industria financiera.
* **AcciÃ³n Correctiva:**  
  * Se vinculÃ³ directamente con la norma **PCI-DSS v4.0 (Req. 3.2 y 4.1)** en los requerimientos **RD-01** y **RF-07**.
  * Se formalizÃ³ el criterio verificable **RF-07-AC-1**: comprobaciÃ³n en base de datos de ausencia total del atributo `cvv`, y validaciÃ³n mediante expresiÃ³n regular del enmascaramiento estricto: `^\d{4}-XXXX-XXXX-\d{4}$`.

---

## 4. Gaps Detectados (Necesidades Faltantes y Omisiones Resueltas)

### Gap G-01: Ausencia de Trazabilidad Cruzada Cliente-Servidor (Observabilidad)
* **DescripciÃ³n de la OmisiÃ³n:** El sistema ejecutaba logs locales independientes, pero no existÃ­a un mecanismo para correlacionar una acciÃ³n ejecutada en el navegador web con la traza de base de datos y la alerta en el panel de seguridad.
* **SoluciÃ³n Incorporada:**  
  * Se integrÃ³ el requerimiento **RF-11** y **RF-10**.
  * Se implementÃ³ un middleware que inyecta en cada ciclo de vida HTTP el encabezado estÃ¡ndar **`X-Correlation-ID`** (UUIDv4), propagÃ¡ndolo hacia el stream de eventos del `ðŸ›¡ï¸ API Sec Inspector`.

### Gap G-02: Falta de DistinciÃ³n Formal entre BOLA y BFLA
* **DescripciÃ³n de la OmisiÃ³n:** Se contaba con la vulnerabilidad BOLA (acceso indebido a datos de otra tienda), pero no se abordaba la autorizaciÃ³n a nivel de funciÃ³n crÃ­tica (BFLA), lo cual dejaba un vacÃ­o en la cobertura del **OWASP API Security Top 10**.
* **SoluciÃ³n Incorporada:**  
  * Se definiÃ³ el flujo de **Devoluciones y Cancelaciones (Refunds)** en el requerimiento **RF-08**.
  * Se diseÃ±aron los criterios de aceptaciÃ³n **RF-08-AC-1** (bloqueo `HTTP 403` a cajero no facultado) y **RF-08-AC-2** (autorizaciÃ³n legÃ­tima con token de supervisor firmado con scope `sales:supervisor_override`).

### Gap G-03: ExposiciÃ³n de Datos Personales (PII Harvesting)
* **DescripciÃ³n de la OmisiÃ³n:** El mÃ³dulo de recargas telefÃ³nicas registraba los nÃºmeros en texto plano sin controles de privacidad, exponiendo a los clientes a recolecciÃ³n masiva para campaÃ±as de extorsiÃ³n o spam.
* **SoluciÃ³n Incorporada:**  
  * Se incorporÃ³ el requerimiento **RF-06** y el criterio **RF-06-AC-1**, estableciendo la ofuscaciÃ³n irreversible en las salidas de la API (`55-****-1234`).

---

## 5. Matriz de Trazabilidad de Requerimientos vs. Pruebas de AceptaciÃ³n

| Requerimiento | ID de Criterio de AceptaciÃ³n | Endpoint Involucrado | Vector / Caso de Prueba | Archivo de Prueba Asociado |
| :--- | :--- | :--- | :--- | :--- |
| **RF-01** | `RF-01-AC-1` | `POST /api/v1/auth/login` | EmisiÃ³n y firma vÃ¡lida de JWT | `tests/test_api_security.py::test_rf_01_ac_1_login_jwt` |
| **RF-01** | `RF-01-AC-2` | `POST /api/v1/auth/login` | Fuerza bruta (Rate Limiting HTTP 429) | `tests/test_api_security.py::test_rf_01_ac_2_bruteforce` |
| **RF-02** | `RF-02-AC-1` | `POST /api/v1/users` | Rechazo de contraseÃ±a dÃ©bil (NIST) | `tests/test_api_security.py::test_rf_02_ac_1_weak_password` |
| **RF-02** | `RF-02-AC-2` | `POST /api/v1/users` | CreaciÃ³n exitosa con expiraciÃ³n 90d | `tests/test_api_security.py::test_rf_02_ac_2_valid_user` |
| **RF-03** | `RF-03-AC-1` | `POST /api/v1/pos/transactions` | Bloqueo de cobro con carrito vacÃ­o | `tests/test_api_security.py::test_rf_03_ac_1_empty_cart` |
| **RF-04** | `RF-04-AC-1` | `POST /api/v1/pos/transactions` | Integridad de cÃ¡lculo en ticket | `tests/test_api_security.py::test_rf_04_ac_1_receipt_math` |
| **RF-05** | `RF-05-AC-1` | `GET /` (UI Frontend) | Aislamiento de mÃ³dulo admin de logo | `tests/test_api_security.py::test_rf_05_ac_1_logo_rbac` |
| **RF-06** | `RF-06-AC-1` | `GET /api/v1/pos/recharges` | OfuscaciÃ³n de PII telefÃ³nica | `tests/test_api_security.py::test_rf_06_ac_1_pii_masking` |
| **RF-07** | `RF-07-AC-1` | `POST /api/v1/payments/card` | TokenizaciÃ³n y ausencia de CVV | `tests/test_api_security.py::test_rf_07_ac_1_pci_tokenization` |
| **RF-08** | `RF-08-AC-1` | `POST /api/v1/pos/transactions/{id}/refund` | Bloqueo BFLA (Cajero sin scope) | `tests/test_api_security.py::test_rf_08_ac_1_bfla_block` |
| **RF-08** | `RF-08-AC-2` | `POST /api/v1/pos/transactions/{id}/refund` | AutorizaciÃ³n con token Supervisor | `tests/test_api_security.py::test_rf_08_ac_2_supervisor_refund` |
| **RNF-01** | `RNF-01-AC-1` | `POST /api/v1/pos/inject-discount` | Rechazo Mass Assignment (`extra="forbid"`) | `tests/test_api_security.py::test_rnf_01_ac_1_mass_assignment` |
| **RNF-02** | `RNF-02-AC-1` | `GET /api/v1/pos/products` | SanitizaciÃ³n de consultas SQLi | `tests/test_api_security.py::test_rnf_02_ac_1_sqli_neutralized` |
| **RNF-03** | `RNF-03-AC-1` | `GET /api/v1/stores/{id}/sales` | Aislamiento BOLA de sucursales | `tests/test_api_security.py::test_rnf_03_ac_1_bola_isolation` |
| **RNF-04** | `RNF-04-AC-1` | `GET /api/v1/pos/products` | Resiliencia y mitigaciÃ³n DoS | `tests/test_api_security.py::test_rnf_04_ac_1_dos_rate_limit` |

---

## 6. Dictamen de AprobaciÃ³n

Una vez contrastadas las modificaciones sobre el documento maestro `SRS_final.md`, se dictamina que:
1. Todos los hallazgos y debilidades identificadas han sido mitigados a nivel documental.
2. Los requerimientos presentan una redacciÃ³n formal y libre de ambigÃ¼edades.
3. Se garantiza la correspondencia unÃ­voca entre las amenazas MITRE ATT&CK, los requerimientos IEEE 830 y los casos de prueba de aceptaciÃ³n.

**Estado del entregable:** APROBADO para publicaciÃ³n en repositorio Git y avance a fases de construcciÃ³n de pruebas automatizadas.