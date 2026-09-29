# TC5029 - Proyecto de ciberseguridad empresarial
**Alumno:** Luis Manuel Mendoza Cruz  
**Matrícula:** A01797418  
**Proyecto Final:** Marco de Seguridad para protección de Integraciones API REST en Cadenas de Tiendas de Conveniencia.

---

## Estructura del Repositorio y Entregables
* `retail-apisec-pos/`: Implementación del caso de estudio de Punto de Venta (POS) para tienda de conveniencia con evaluación de vulnerabilidades OWASP API Security Top 10 y arquitectura de mitigación Zero Trust (Dual As-Is vs To-Be).
  * `/as-is`: Microservicio legado vulnerable (Flask / SQLite).
  * `/docs`:
    * `SRS_final.md`: Especificación de Requerimientos de Software bajo la norma IEEE 830.
    * `matriz_mitre.md`: Matriz visual representativa de amenazas MITRE ATT&CK (Enterprise Matrix).
    * `mitre_layer.json`: Capa importable en MITRE ATT&CK Navigator.
    * `cronograma_actividades.md`: Plan de trabajo de 13 semanas, estatus por semáforos, SLAs y gráfica de Gantt (Mermaid).
    * `use_cases.puml`: Diagrama de casos de uso en PlantUML (Cajero, Supervisor y Administrador).
    * `revision_SRS.md`: Bitácora técnica de validación y trazabilidad de pruebas.

---

## Matriz Representativa MITRE ATT&CK (Resumen de TTPs Evaluados)

| Táctica MITRE | ID Técnica | Nombre Técnica | Score | Amenaza en Retail POS (As-Is) | Mitigación Zero Trust (To-Be) |
| :--- | :---: | :--- | :---: | :--- | :--- |
| **Reconnaissance** | `T1592` | Gather Victim Host Info | 🟡 7 | Recolección de números telefónicos en recargas (*PII Harvesting*) | Enmascaramiento irreversible (`55-****-1234`) |
| **Initial Access** | `T1190` | Exploit Public-Facing App | 🔴 9 | Inyección SQL (SQLi) en catálogo para robar credenciales | Sentencias preparadas y validación estricta DTO |
| **Credential Access** | `T1110.001`| Brute Force: Password Guessing | 🟠 8 | Ataque de diccionario contra `/api/v1/auth/login` | Rate Limiting (5 intentos / 30s) y bloqueo temporal |
| **Privilege Escalation**| `T1078.004`| Valid Accounts (BOLA) | 🔴 9 | Acceso a transacciones y arqueos de otra sucursal (`store_id`) | Autorización a nivel de objeto cruzando JWT vs URL |
| **Privilege Escalation**| `T1068` | Exploitation for Privilege (BFLA) | 🟠 8 | Cajero ejecuta cancelaciones y reembolsos no autorizados | Restricción estricta al scope `sales:supervisor_override` |
| **Defense Evasion** | `T1565.001`| Data Manipulation (Mass Assignment)| 🔴 9 | Inyección de descuento no autorizado (`"discount_pct": 100`) | Esquemas Pydantic estrictos con `extra="forbid"` |
| **Collection** | `T1005` | Data from Local System (PCI) | 🔴 9 | Almacenamiento en claro de tarjetas bancarias y CVV | Tokenización, máscara PAN y prohibición de CVV |
| **Impact** | `T1499.002`| Endpoint Denial of Service (DoS) | 🟠 8 | Ráfagas de peticiones que congelan la terminal de cobro | Algoritmo Token Bucket a 10 req/s con `HTTP 429` |
