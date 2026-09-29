# Especificacion de Requerimientos de Software (SRS)
## Sistema de Punto de Venta Retail 7-Eleven con Arquitectura Zero Trust
**Estandar de Referencia:** IEEE Std 830-1998 (Estructura Simplificada)  
**Version:** 1.0.0-Final  
**Fecha:** Septiembre 2026  
**Proyecto:** Marco de Seguridad para protección de Integraciones API REST en Cadenas de Tiendas de Conveniencia  
**Materia:** TC5029 - Proyecto de ciberseguridad empresarial  
**Estudiante:** Luis Manuel Mendoza Cruz (A01797418)

---

## 1. Introduccion

### 1.1 Proposito del documento
El proposito de esta Especificacion de Requerimientos de Software (SRS) es formalizar los requerimientos funcionales, no funcionales y de dominio del sistema de Punto de Venta (POS) para 7-Eleven. El proyecto articula una demostracion tecnica dual:
1. **Entorno As-Is (Vulnerable / Flask):** Expone debilidades criticas comunes en arquitecturas transaccionales heredadas (Inyeccion SQL, BOLA, Mass Assignment, BFLA, almacenamiento de tarjetas sin cifrar y Denegacion de Servicio).
2. **Entorno To-Be (Seguro / FastAPI):** Implementa un modelo de ciberseguridad *Zero Trust* con autenticacion criptografica JWT, control de acceso basado en roles con scopes minimos (RBAC), contratos DTO estrictos con listas blancas (*whitelisting*), observabilidad forense y cumplimiento normativo (PCI-DSS y NIST SP 800-63B).

### 1.2 Alcance del sistema
El sistema abarca el flujo completo de caja registradora en tienda de conveniencia:
* Inicio de sesion de operadores y gobierno de identidades (IAM).
* Escaneo y seleccion de articulos categorizados con calculo de totales.
* Cobro seguro de transacciones en efectivo y tarjetas bancarias.
* Operaciones de servicios (recargas telefonicas de tiempo aire).
* Supervision operativa (reembolsos, cancelaciones y arqueo de caja).
* Inspeccion de telemetria, trazas y metricas de seguridad en tiempo real (*API Sec Inspector*).

### 1.3 Definiciones, acronimos y abreviaturas
* **API:** *Application Programming Interface* (Interfaz de Programacion de Aplicaciones).
* **APM:** *Application Performance Monitoring* (Monitoreo de Rendimiento de Aplicaciones).
* **BFLA:** *Broken Function Level Authorization* (OWASP API5:2023).
* **BOLA:** *Broken Object Level Authorization* (OWASP API1:2023).
* **CVV/CVC:** *Card Verification Value* (Codigo de seguridad de tarjeta bancaria).
* **DTO:** *Data Transfer Object* (Objeto de Transferencia de Datos).
* **IAM:** *Identity and Access Management* (Gestion de Identidades y Accesos).
* **JWT:** *JSON Web Token* (RFC 7519).
* **MFA:** *Multi-Factor Authentication* (Autenticacion Multifactor).
* **PAN:** *Primary Account Number* (Numero de cuenta principal / 16 digitos de tarjeta).
* **PCI-DSS:** *Payment Card Industry Data Security Standard*.
* **PII:** *Personally Identifiable Information* (Informacion de Identificacion Personal).
* **POS:** *Point of Sale* (Punto de Venta / Terminal de Cobro en Caja).
* **RBAC:** *Role-Based Access Control* (Control de Acceso Basado en Roles).
* **SQLi:** *SQL Injection* (OWASP API8:2023).

---

## 2. Descripcion General

### 2.1 Perspectiva del producto
El producto es un microservicio web desacoplado donde la interfaz de usuario de la terminal interactua con una API RESTful sobre HTTP/HTTPS. La solucion contrasta el comportamiento de un monolito backend no tipado con validaciones nulas frente a una arquitectura moderna orientada a contratos (*Schema-First* y *Shift-Left Security*).

Estructuralmente, el sistema se divide en:
* **Capa de Presentacion:** Terminal Web POS 7-Eleven con catalogo categorizado, ticket y panel tecnico retractil (*Hot Edge*).
* **Capa de Servicios As-Is (Puerto 5000):** Backend Flask vulnerable acoplado a consultas directas SQLite sin tipado.
* **Capa de Servicios To-Be (Puerto 8000):** Backend FastAPI protegido con dependencias de seguridad JWT, esquemas DTO Pydantic (`extra="forbid"`) y middleware de telemetria correlacionada.

### 2.2 Funciones del producto
* **Gestion de Sesiones e Identidades:** Autenticacion por roles con emision de tokens seguros.
* **Venta en Mostrador:** Catalogo dinamico con filtros, scroll estilizado y armado de ticket.
* **Procesamiento de Pagos Seguros:** Tokenizacion transaccional y proteccion de datos financieros.
* **Servicios Electronicos:** Registro de recargas moviles con proteccion de numeros telefonicos.
* **Autorizacion Supervisada:** Flujos de aprobacion para excepciones, cancelaciones y arqueos.
* **Observabilidad Centralizada:** Panel de metricas, trazas APM y bitacora de eventos de seguridad.

### 2.3 Caracteristicas de los usuarios
* **Cajero (Operador):** Usuario operativo de mostrador; requiere agilidad de escaneo y cobro; sin permisos para modificar catalogos, conceder descuentos ni cancelar ventas.
* **Supervisor:** Autoridad en tienda; facultado para desbloquear turnos, realizar cortes de caja y aprobar reembolsos mediante elevacion de privilegios.
* **Administrador:** Responsable de infraestructura y ciberseguridad; gestiona credenciales de usuarios, gobierna politicas IAM, audita la telemetria y personaliza el branding corporativo.

### 2.4 Restricciones de diseno e implementacion
* La persistencia de datos utiliza SQLite relacional para asegurar portabilidad en estaciones locales.
* El formato del ticket fisico/digital debe limitarse a estandares de impresion termica en blanco y negro (monocromatico de 1 bit).
* La interfaz tecnica lateral debe operar mediante desacoplamiento visual dinamico (*Hot Edge* con flexbox), evitando bloquear o encimar la pantalla operativa de cobro.

---

## 3. Requerimientos Especificos

### 3.1 Requerimientos Funcionales (RF)

* **RF-01: Autenticacion de Operadores en Terminal**  
  El sistema debe autenticar a los operadores de caja mediante credenciales (usuario y contrasena), generando un token JWT firmado criptograficamente con algoritmo HMAC-SHA256 que contenga identificador de usuario (`sub`), rol (`role`), sucursal (`store_id`) y permisos delegados (`scope`).

* **RF-02: Creacion de Usuarios con Politicas de Contrasena**  
  El sistema debe permitir al Administrador registrar nuevos operadores de caja. En el entorno To-Be, la API debe validar obligatoriamente que la contrasena cumpla con una longitud minima de 9 caracteres, contenga mayusculas, minusculas, numeros y caracteres especiales, asignandole una vigencia de 90 dias naturales.

* **RF-03: Catalogo Dinamico y Seleccion de Articulos**  
  El sistema debe presentar un catalogo clasificado por pestanas de categorias (Bebidas, Comida, Frutas, Snacks, Postres, Farmacia) con barra de desplazamiento estetico, permitiendo agregar productos al carrito con su precio unitario y emoji representativo.

* **RF-04: Emision y Desglose de Ticket de Venta**  
  El sistema debe generar un comprobante formal de venta al procesar el cobro, desplegando folio unico de recibo, sucursal, fecha/hora, cajero en turno, desglose detallado de todos los articulos escaneados, subtotal, porcentaje de descuento aplicado y sumatoria total a pagar.

* **RF-05: Administracion del Logotipo Institucional**  
  El sistema debe permitir exclusivamente al usuario Administrador cargar una nueva imagen para el logotipo corporativo. La caratula principal mostrara la imagen a color, pero dentro del ticket de compra se forzara la impresion en escala de grises termica monocromatica.

* **RF-06: Modulo de Recargas Telefonicas Protegidas**  
  El sistema debe procesar recargas electronicas de tiempo aire registrando compania y monto, ofuscando el numero telefonico receptor en las respuestas publicas de la API (`55-****-1234`) para evitar recoleccion masiva de datos personales (PII).

* **RF-07: Procesamiento de Pagos con Tarjeta (Cumplimiento PCI-DSS)**  
  El sistema debe recibir pagos con tarjeta de debito o credito generando un identificador tokenizado transaccional (`tok_live_...`) y almacenando unicamente los primeros 4 y ultimos 4 digitos del PAN enmascarado (`4152-XXXX-XXXX-5678`), prohibiendo terminantemente la persistencia del codigo de seguridad CVV.

* **RF-08: Autorizacion de Devoluciones y Reembolsos (BFLA)**  
  El sistema debe restringir las solicitudes de reembolso o cancelacion de tickets exclusivamente al rol de Supervisor mediante la validacion del scope `sales:supervisor_override`, bloqueando cualquier intento de ejecucion directa por parte de un cajero.

* **RF-09: Arqueo y Corte de Caja**  
  El sistema debe permitir al Supervisor realizar el arqueo de caja registradora, comparando el monto fisico en efectivo contra el importe registrado en el sistema, generando el resumen fiscal parcial (Corte X) o final (Corte Z).

* **RF-10: Dashboard de Observabilidad y Telemetria Forense**  
  El sistema debe ofrecer al Administrador un panel de control en `🛡️ API Sec Inspector` con indicadores en tiempo real tipo Datadog: Throughput (RPS), tasa de error (4xx/5xx), contador de ataques mitigados y latencia P95.

* **RF-11: Trazabilidad y Correlacion de Peticiones**  
  El sistema debe inyectar un encabezado HTTP estandar `X-Correlation-ID` en cada solicitud y respuesta, vinculandolo a los registros de auditoria y trazas de la base de datos para facilitar la reconstruccion forense de incidentes.

* **RF-12: Validacion Estricta de Carrito No Vacio**  
  El sistema debe bloquear y deshabilitar la accion de cobro tanto en la interfaz de usuario como en el endpoint del backend si el ticket de venta no contiene al menos un articulo escaneado.

---

### 3.2 Requerimientos No Funcionales (RNF)

* **RNF-01 [Seguridad - DTO Whitelisting]:**  
  La API protegida (To-Be) debe validar los contratos de entrada mediante esquemas Pydantic configurados con `extra="forbid"`, rechazando cualquier atributo inyectado no autorizado (ej. `discount_pct: 100`) con codigo `HTTP 422 Unprocessable Entity` para mitigar Mass Assignment (OWASP API6:2023).

* **RNF-02 [Seguridad - Consultas Parametrizadas]:**  
  Todas las interacciones con la base de datos deben utilizar sentencias preparadas (*Prepared Statements*) y sanitizacion de parametros de busqueda, impidiendo la inyeccion de codigo SQL y exfiltracion de tablas (OWASP API8:2023).

* **RNF-03 [Seguridad - Aislamiento Multi-Tenant]:**  
  La API debe aplicar autorizacion a nivel de objeto verificando que el parametro de tienda solicitado en la URL coincida obligatoriamente con el claim `store_id` del token JWT, respondiendo con `HTTP 403 Forbidden` ante intentos de fuga de informacion de otras sucursales (OWASP API1:2023 - BOLA).

* **RNF-04 [Disponibilidad y Resiliencia - Anti-DoS]:**  
  El sistema debe incorporar un middleware de limitacion de tasa (*Rate Limiting*) que restrinja el consumo a un umbral maximo de 10 peticiones por segundo por cliente, retornando `HTTP 429 Too Many Requests` ante rafagas masivas para evitar la denegacion de servicio (OWASP API4:2023).

* **RNF-05 [Rendimiento]:**  
  El tiempo de respuesta del backend para autorizar una transaccion de cobro no debe exceder los 250 milisegundos en el percentil 95 (P95) bajo condiciones nominales de carga.

* **RNF-06 [Usabilidad y Ergonomia Visual]:**  
  La consola lateral de seguridad debe desplegarse mediante un sensor invisible en el borde derecho (*Hot Edge*), empujando el contenido del Punto de Venta hacia la izquierda mediante flexbox sin encimarse ni romper la vista comercial.

---

### 3.3 Requerimientos de Dominio (RD)

* **RD-01 [Normativa PCI-DSS v4.0]:**  
  En cumplimiento del Requisito 3.2 de PCI-DSS, el sistema prohibe explicitamente almacenar el codigo de seguridad (CVV/CVC) despues de que la transaccion haya sido procesada. Todo dato de tarjeta expuesto en reportes debe estar enmascarado mostrando un maximo de los primeros 6 y ultimos 4 digitos.

* **RD-02 [Estandar de Identidad NIST SP 800-63B]:**  
  Las contrasenas de los operadores deben forzar una caducidad periodica de 90 dias naturales, manteniendo un historial que impida reutilizar las ultimas 4 contrasenas registradas.

* **RD-03 [Estandar Fiscal de Impresion POS]:**  
  Los comprobantes de pago generados deben apegarse al formato de impresion termica estandar de 80 columnas, requiriendo tipografia monoespaciada legible y graficos renderizados a 1 bit monocromatico.

---

## 4. Criterios de Aceptacion (Formato Given-When-Then)

### Modulo: Autenticacion y Control de Acceso (RF-01, RF-02)

#### `RF-01-AC-1`: Autenticacion Exitosa con Generacion de JWT
* **Dado que** el operador ingresa credenciales validas en la pantalla de login (ej. `Cajero1` con contrasena `1234`),  
* **cuando** presiona el boton "Iniciar Turno",  
* **entonces** la API responde con codigo `HTTP 200 OK`, entrega un token JWT con los claims `sub`, `role`, `store_id` y `scope`, y la interfaz desbloquea la terminal de cobro.

#### `RF-01-AC-2`: Bloqueo por Fuerza Bruta en Autenticacion
* **Dado que** un atacante ejecuta intentos recurrentes sobre el endpoint `/api/v1/auth/login`,  
* **cuando** supera el umbral de 5 intentos fallidos consecutivos en un lapso menor a 30 segundos,  
* **entonces** la API To-Be responde con codigo `HTTP 429 Too Many Requests` y rechaza nuevas solicitudes durante un periodo de penalizacion de 60 segundos.

#### `RF-02-AC-1`: Validacion de Complejidad de Contrasena (NIST)
* **Dado que** el usuario Administrador intenta crear un nuevo cajero con una contrasena corta o predecible (ej. `cajero123`),  
* **cuando** envia la peticion `POST /api/v1/users`,  
* **entonces** el servicio To-Be rechaza la creacion con codigo `HTTP 422 Unprocessable Entity`, detallando que la contrasena debe contener al menos 9 caracteres, numeros, mayusculas y caracteres especiales.

---

### Modulo: Operacion de Caja y Emision de Tickets (RF-03, RF-04, RF-12)

#### `RF-03-AC-1`: Bloqueo de Cobro con Carrito Vacio
* **Dado que** el cajero no ha agregado ningun producto a la lista de venta (carrito con 0 items),  
* **cuando** intenta presionar el boton de cobro,  
* **entonces** la interfaz mantiene el boton deshabilitado (`opacity: 0.4`) y si se fuerza la peticion via API, el servidor retorna `HTTP 400 Bad Request` o `HTTP 422 Unprocessable Entity` impidiendo registrar la transaccion.

#### `RF-04-AC-1`: Emision Completa de Ticket Impreso
* **Dado que** el cajero tiene registrados en el carrito un Cafe 12oz ($26.50) y un Big Bite ($38.00),  
* **cuando** presiona "Procesar Cobro Normal",  
* **entonces** la API registra la venta con codigo `HTTP 201 Created` y la interfaz despliega una ventana modal con el ticket de compra desglosando ambos SKU, el cajero asignado, el subtotal exacto de $64.50, descuento 0% y el total a pagar de $64.50 con el logotipo impreso en blanco y negro.

---

### Modulo: Branding y Personalizacion Institucional (RF-05)

#### `RF-05-AC-1`: Segregacion de Acceso al Modulo de Logotipo
* **Dado que** el usuario autenticado tiene el rol operativo `cashier` (`Cajero1` o `Cajero2`),  
* **cuando** visualiza la terminal de cobro,  
* **entonces** el modulo de actualizacion de logotipo no aparece visible ni accesible en el arbol DOM de la pagina.

#### `RF-05-AC-2`: Actualizacion y Renderizado Termico Monocromatico
* **Dado que** el usuario autenticado es `Administrador` y carga un logotipo corporativo en formato PNG con colores vivos,  
* **cuando** se emite un nuevo ticket de cobro,  
* **entonces** la caratula superior muestra el logotipo a color pero el ticket de venta aplica un filtro CSS `grayscale(100%) contrast(150%)` garantizando su impresion termica monocromatica.

---

### Modulo: Servicios Financieros y Telefonia (RF-06, RF-07)

#### `RF-06-AC-1`: Ofuscacion de Datos Personales en Recargas (PII)
* **Dado que** se realiza una recarga telefonica al numero `5512345678`,  
* **cuando** la terminal consulta el historial de recargas o emite el comprobante,  
* **entonces** la API To-Be retorna el numero ofuscado bajo el patron `55-****-5678` sin exponer el identificador completo del cliente.

#### `RF-07-AC-1`: Tokenizacion y Enmascaramiento de Tarjeta Bancaria
* **Dado que** el cliente realiza el pago mediante una tarjeta bancaria con numero `4152-3134-1234-5678`,  
* **cuando** la transaccion es enviada a la API To-Be,  
* **entonces** el backend almacena unicamente el token transaccional y el PAN enmascarado `4152-XXXX-XXXX-5678`, descartando el campo CVV de la memoria persistente.

---

### Modulo: Supervision y Control Funcional (RF-08, RF-09)

#### `RF-08-AC-1`: Bloqueo de Reembolso no Autorizado a Cajero (BFLA)
* **Dado que** un operador con rol `cashier` intenta ejecutar un reembolso invocando `POST /api/v1/pos/transactions/{id}/refund`,  
* **cuando** la peticion es evaluada por la API To-Be,  
* **entonces** la API responde con codigo `HTTP 403 Forbidden` (`SEC_BFLA_VIOLATION`) debido a que el token carece del scope `sales:supervisor_override`.

#### `RF-08-AC-2`: Aprobacion de Reembolso por Supervisor
* **Dado que** el usuario autenticado posee el rol `supervisor`,  
* **cuando** ejecuta la solicitud de reembolso sobre un folio existente,  
* **entonces** la API procesa la reversa con codigo `HTTP 200 OK`, actualiza el estado a `REFUNDED` y descuenta el importe del arqueo activo de la sucursal.

---

### Modulo: Pruebas de Mitigacion de Vulnerabilidades (RNF-01, RNF-02, RNF-03, RNF-04)

#### `RNF-01-AC-1`: Mitigacion de Fraude por Mass Assignment
* **Dado que** un atacante altera el payload de la transaccion inyectando el parametro `"discount_pct": 100`,  
* **cuando** la peticion llega al endpoint de cobro del entorno To-Be,  
* **entonces** el validador DTO de Pydantic intercepta la peticion, rechaza el campo no permitido con codigo `HTTP 422 Unprocessable Entity` y no permite emitir tickets con saldo en $0.00 pesos.

#### `RNF-02-AC-1`: Mitigacion de Exfiltracion por SQL Injection
* **Dado que** un atacante introduce la cadena `Cafe' UNION SELECT id, password, 'x', 'x' FROM users--` en el buscador de productos,  
* **cuando** se ejecuta la consulta en el entorno To-Be,  
* **entonces** la API evalua la entrada mediante consultas parametrizadas o la rechaza por regex en el DTO, evitando la exfiltracion de credenciales.

#### `RNF-03-AC-1`: Mitigacion de Fuga de Ventas Multi-Tienda (BOLA)
* **Dado que** un operador autenticado en la sucursal `STORE-711-MEX` intenta consultar las ventas de `STORE-711-GDA` manipulando el path `/api/v1/stores/STORE-711-GDA/sales`,  
* **cuando** la API evalua la solicitud,  
* **entonces** detecta que el `store_id` del token JWT no coincide con el recurso solicitado y responde inmediatamente con `HTTP 403 Forbidden` (`SEC_BOLA_VIOLATION`).

#### `RNF-04-AC-1`: Resiliencia ante Rafagas Masivas (Anti-DoS)
* **Dado que** se dispara un ataque de saturacion enviando una rafaga de 100 peticiones concurrentes en menos de un segundo hacia `/api/v1/pos/products`,  
* **cuando** la tasa supera las 10 req/s,  
* **entonces** el middleware de limitacion de tasa del To-Be responde con codigo `HTTP 429 Too Many Requests` protegiendo la disponibilidad de la caja registradora, a diferencia del As-Is que colapsa con congelamiento del servidor.
