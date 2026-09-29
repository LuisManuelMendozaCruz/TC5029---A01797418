# Calendario de Actividades, Plan de Trabajo y Gestión de SLAs
**Proyecto:** Marco de Seguridad para protección de Integraciones API REST en Cadenas de Tiendas de Conveniencia  
**Materia:** TC5029 - Proyecto de ciberseguridad empresarial  
**Estudiante:** Luis Manuel Mendoza Cruz (Matrícula: A01797418)  
**Periodo Trimestral:** 07 de septiembre de 2026 al 04 de diciembre de 2026  
**Fecha de Corte de Avance:** 25 de septiembre de 2026  

---

## 1. Desglose Semanal de Fases y Actividades

| Semana | Fecha Inicio | Fecha Fin | Fase del Proyecto | Actividad Principal y Entregable | Avance Planeado | Avance Real | Estatus (Semáforo) |
| :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: |
| **S01** | 07-Sep-2026 | 11-Sep-2026 | **Fase 1: Elicitación y Alcance** | Definición del problema, alcance Zero Trust e identificación de actores y activos críticos en tiendas de conveniencia. | 100% | 100% | 🟢 En tiempo |
| **S02** | 14-Sep-2026 | 18-Sep-2026 | **Fase 1: Requerimientos IEEE 830** | Especificación formal SRS (`SRS_final.md`), casos de uso PlantUML y bitácora técnica de validación (`revision_SRS.md`). | 100% | 100% | 🟢 En tiempo |
| **S03** | 21-Sep-2026 | 25-Sep-2026 | **Fase 1: Threat Modeling & Baseline** | Mapeo de vectores MITRE ATT&CK (`mitre_layer.json`), arquitectura base Flask As-Is y entrega inicial en GitHub. *(Corte de evaluación)* | 100% | 100% | 🟢 En tiempo |
| **S04** | 28-Sep-2026 | 02-Oct-2026 | **Fase 2: Arquitectura Base As-Is** | Despliegue de endpoints de caja vulnerables (SQLite no parametrizado, sin tipado de datos ni rate limiting). | 0% | 0% | 🟡 En Proceso |
| **S05** | 05-Oct-2026 | 09-Oct-2026 | **Fase 2: Arquitectura Protegida To-Be** | Inicialización del entorno FastAPI, definición de contratos OpenAPI (`openapi.yaml`) y pipeline criptográfico JWT. | 0% | 0% | ⚪ Programado |
| **S06** | 12-Oct-2026 | 16-Oct-2026 | **Fase 3: Controles Antifraude** | Implementación de esquemas DTO estrictos en Pydantic (`extra="forbid"`) para mitigación de Mass Assignment y parámetros de descuento. | 0% | 0% | ⚪ Programado |
| **S07** | 19-Oct-2026 | 23-Oct-2026 | **Fase 3: Aislamiento Multi-Tenant & SQLi** | Controles RBAC basados en scopes JWT y validación estricta de `store_id` (anti-BOLA) y consultas parametrizadas. | 0% | 0% | ⚪ Programado |
| **S08** | 26-Oct-2026 | 30-Oct-2026 | **Fase 4: Módulo PCI-DSS y Pagos** | Tokenización de transacciones con tarjeta bancaria, aislamiento de PAN (`XXXX-XXXX-XXXX-1234`) y eliminación de persistencia de CVV. | 0% | 0% | ⚪ Programado |
| **S09** | 02-Nov-2026 | 06-Nov-2026 | **Fase 4: Protección PII y Antidopaje DoS** | Enmascaramiento irreversible de números telefónicos en recargas y middleware de limitación de tasa (10 req/s con HTTP 429). | 0% | 0% | ⚪ Programado |
| **S10** | 09-Nov-2026 | 13-Nov-2026 | **Fase 4: Autorización Funcional BFLA** | Módulo de reembolsos, cancelaciones y arqueo de caja registradora restringidos exclusivamente al rol de Supervisor. | 0% | 0% | ⚪ Programado |
| **S11** | 16-Nov-2026 | 20-Nov-2026 | **Fase 5: Observabilidad y Telemetría** | Middleware de inyección de `X-Correlation-ID` y construcción del Dashboard forense `API Sec Inspector` con indicadores Datadog-like. | 0% | 0% | ⚪ Programado |
| **S12** | 23-Nov-2026 | 27-Nov-2026 | **Fase 5: Automatización de Pruebas** | Suite integral en pytest (`test_api_security.py`) validando cada criterio Given-When-Then contra la matriz MITRE. | 0% | 0% | ⚪ Programado |
| **S13** | 30-Nov-2026 | 04-Dic-2026 | **Fase 6: Memoria Técnica y Defensa** | Consolidación de documentación final, video-demostración técnica ejecutiva y presentación de defensa ante el jurado evaluador. | 0% | 0% | ⚪ Programado |

---

## 2. Métricas de Rendimiento y SLAs de Entrega

### Semáforo de Gestión de Entregables
* 🟢 **En tiempo:** Actividad finalizada o en curso dentro de la ventana de tiempo pactada (Desviación <= 0 días).
* 🟡 **En proceso:** Actividad iniciada en el sprint activo con recursos asignados.
* 🟠 **Por vencer:** Actividad con fecha compromiso en los próximos 3 días hábiles sin alcanzar el 80% de avance.
* 🔴 **Atrasado / Con demora:** Actividad cuya fecha de cierre fue rebasada respecto al cronograma inicial (Desviación > 0 días).
* ⚪ **Programado:** Actividad de sprints futuros sin arranque programado.

### Resumen de Avance al Corte del 25-Septiembre-2026
* **Avance Planeado Acumulado:** 23.08% (3 de 13 semanas concluidas).
* **Avance Real Acumulado:** 23.08% (Cumplimiento estricto del 100% de los entregables de Fase 1).
* **SLA de Resolución de Hallazgos Documentales:** < 48 horas (100% de cumplimiento).
* **SLA de Disponibilidad de Repositorio Público:** 100% (Sincronizado en GitHub).

---

## 3. Diagrama de Gantt del Plan de Trabajo (Mermaid)

```mermaid
gantt
    title Plan de Trabajo: Marco de Seguridad para APIs de Retail POS (TC5029)
    dateFormat  YYYY-MM-DD
    axisFormat  %d-%b
    todayMarker stroke-width:2px,stroke:#0284c7,opacity:0.8

    section Fase 1: Requerimientos & Threat Modeling
    Elicitación y Alcance (S01)            :done, s01, 2026-09-07, 2026-09-11
    SRS IEEE 830 y Casos de Uso (S02)      :done, s02, 2026-09-14, 2026-09-18
    Matriz MITRE & Baseline As-Is (S03)    :done, s03, 2026-09-21, 2026-09-25

    section Fase 2: Arquitectura Base
    Despliegue As-Is Vulnerable (S04)      :active, s04, 2026-09-28, 2026-10-02
    Baseline To-Be FastAPI & JWT (S05)     :s05, 2026-10-05, 2026-10-09

    section Fase 3: Controles Críticos
    DTO Whitelisting Anti-Mass Assignment (S06) :s06, 2026-10-12, 2026-10-16
    Aislamiento Multi-Tenant & Anti-SQLi (S07)  :s07, 2026-10-19, 2026-10-23

    section Fase 4: Módulos de Seguridad & Dominio
    Tokenización PCI-DSS Tarjetas (S08)    :s08, 2026-10-26, 2026-10-30
    Ofuscación PII & Anti-DoS (S09)        :s09, 2026-11-02, 2026-11-06
    Control de Acceso Funcional BFLA (S10) :s10, 2026-11-09, 2026-11-13

    section Fase 5: Observabilidad & QA
    Dashboard Telemetría Datadog (S11)     :s11, 2026-11-16, 2026-11-20
    Suite de Pruebas Pytest (S12)          :s12, 2026-11-23, 2026-11-27

    section Fase 6: Cierre & Defensa
    Memoria Técnica y Defensa Oral (S13)   :crit, s13, 2026-11-30, 2026-12-04
