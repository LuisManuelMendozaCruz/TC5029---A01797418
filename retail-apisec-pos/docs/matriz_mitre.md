# Matriz Visual de Amenazas MITRE ATT&CK (Enterprise Matrix)
**Proyecto:** Marco de Seguridad para protección de Integraciones API REST en Cadenas de Tiendas de Conveniencia  
**Materia:** TC5029 - Proyecto de ciberseguridad empresarial  
**Estudiante:** Luis Manuel Mendoza Cruz (Matrícula: A01797418)  
**Capa Navigator Asociada:** `docs/mitre_layer.json` (ATT&CK Enterprise v15)

---

## 1. Mapa de Calor y Cobertura de Tácticas vs. Técnicas

| Táctica MITRE | ID Técnica | Nombre de la Técnica | Criticidad (Score) | Vector Evaluado en Retail POS (As-Is) | Control de Mitigación Zero Trust (To-Be) | Requerimiento Trazable |
| :--- | :---: | :--- | :---: | :--- | :--- | :---: |
| **Reconnaissance** *(TA0043)* | **T1592** | Gather Victim Host Info | 🟡 **7 / 10** | Recolección de números telefónicos en recargas en texto plano (*PII Harvesting*). | Ofuscación irreversible en respuestas públicas de la API (`55-****-1234`). | `RF-06` / `RF-06-AC-1` |
| **Initial Access** *(TA0001)* | **T1190** | Exploit Public-Facing Application | 🔴 **9 / 10** | Inyección SQL (SQLi) en el catálogo para extraer credenciales (`' UNION SELECT...`). | Sentencias preparadas (*Prepared Statements*) y sanitización tipada en esquemas DTO. | `RNF-02` / `RNF-02-AC-1` |
| **Credential Access** *(TA0006)* | **T1110.001** | Brute Force: Password Guessing | 🟠 **8 / 10** | Fuerza bruta recurrente contra credenciales en `/api/v1/auth/login`. | Middleware de Rate Limiting (5 intentos / 30s) con `HTTP 429` y bloqueo temporal. | `RF-01` / `RF-01-AC-2` |
| **Privilege Escalation** *(TA0004)* | **T1078.004** | Valid Accounts: Cloud/Web (BOLA) | 🔴 **9 / 10** | Suplantación de `store_id` para ver transacciones de otras tiendas. | Validación criptográfica de coincidencia entre URL y claim `store_id` en JWT (`HTTP 403`). | `RNF-03` / `RNF-03-AC-1` |
| **Privilege Escalation** *(TA0004)* | **T1068** | Exploitation for Privilege (BFLA) | 🟠 **8 / 10** | Cajero ejecuta cancelaciones y reembolsos sin rol de supervisor. | Control de acceso basado en roles exigiendo scope `sales:supervisor_override`. | `RF-08` / `RF-08-AC-1` |
| **Defense Evasion** *(TA0005)* | **T1565.001** | Data Manipulation (Mass Assignment) | 🔴 **9 / 10** | Inyección del parámetro `"discount_pct": 100` en el payload JSON. | Validación estricta con esquemas Pydantic configurados con `extra="forbid"`. | `RNF-01` / `RNF-01-AC-1` |
| **Collection** *(TA0009)* | **T1005** | Data from Local System (PCI) | 🔴 **9 / 10** | Almacenamiento local de tarjetas de crédito en texto plano y código CVV. | Tokenización (`tok_live_...`), máscara PAN y descarte total de CVV (PCI-DSS 3.2). | `RF-07` / `RD-01` |
| **Impact** *(TA0040)* | **T1499.002** | Endpoint DoS: Service Exhaustion | 🟠 **8 / 10** | Ráfagas masivas de consultas que congelan la terminal de cobro. | Algoritmo Token Bucket limitando a 10 req/s con código `HTTP 429` y `Retry-After`. | `RNF-04` / `RNF-04-AC-1` |

---

## 2. Instrucciones de Importación a MITRE ATT&CK Navigator
Para visualizar la capa dinámica interactiva con gradientes de color (#ffffff -> #fef08a -> #ef4444):
1. Ingresar a [MITRE ATT&CK Navigator](https://mitre-attack.github.io/attack-navigator/).
2. Seleccionar **Open Existing Layer** > **Upload from local**.
3. Seleccionar el archivo `docs/mitre_layer.json` incluido en este repositorio.
