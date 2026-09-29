# Calendario de Actividades y Plan de Trabajo
**Proyecto:** Marco de Seguridad para protección de Integraciones API REST en Cadenas de Tiendas de Conveniencia  
**Materia:** TC5029 - Proyecto de ciberseguridad empresarial  
**Estudiante:** Luis Manuel Mendoza Cruz (A01797418)

| Fase / Sprint | Semanas | Actividad Principal | Entregable Asociado |
| :--- | :--- | :--- | :--- |
| **Fase 1: Requerimientos & Threat Modeling** | S01 - S03 | Definicion de SRS (IEEE 830), matriz MITRE ATT&CK, clasificacion RF/RNF/RD y diseno de UI/UX del POS. | `SRS_final.md`, `revision_SRS.md`, `mitre_layer.json` |
| **Fase 2: Arquitectura Base As-Is / To-Be** | S04 - S06 | Construccion del entorno legado Flask y baseline protegido FastAPI con OpenAPI (`openapi.yaml`). | Codigo base en `/as-is` y `/to-be` |
| **Fase 3: Implementacion de Controles Criticos** | S07 - S09 | Implementacion de DTOs (`extra="forbid"`), aislamiento RBAC/BOLA con JWT Scopes y mitigacion SQLi. | Pruebas de integracion, middleware de correlacion |
| **Fase 4: Expansion de Modulos (IAM, PCI, DoS)** | S10 - S12 | Modulo de pagos con tarjeta (tokenizacion), recargas (PII masking), simulacion DoS y modulo de cancelaciones (BFLA). | Endpoints de pagos, usuarios y supervisor |
| **Fase 5: Observabilidad & Pruebas Automatizadas** | S13 - S14 | Construccion del Dashboard Datadog-like en `🛡️ API Sec Inspector` y suite de pruebas pytest. | `test_api_security.py` ligado a IDs de aceptacion |
| **Fase 6: Entrega Final & Defensa** | S15 - S16 | Integracion de video-demo, reporte forense y defensa ante el jurado evaluador. | Memoria tecnica y repositorio consolidado |
