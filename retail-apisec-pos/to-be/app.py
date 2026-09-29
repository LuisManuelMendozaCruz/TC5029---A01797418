"""
Punto de Venta 7-Eleven - Escenario To-Be (Seguro Zero Trust)
Efecto dinámico de empuje lateral hacia la izquierda + Módulos exclusivos de Administrador.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3
import jwt
import time
from typing import List, Dict, Any

from schemas.transaction_dto import ProductSearchDTO, TransactionCreateDTO, ReceiptResponseDTO
from middleware.correlation_middleware import CorrelationMiddleware
from middleware.auth_middleware import check_scope, validate_token_claims, JWT_SECRET, JWT_ALGORITHM

app = FastAPI(
    title="APISec Retail - POS Protected API (To-Be)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(CorrelationMiddleware)
DB_NAME = "pos_secure.db"

class LoginRequest(BaseModel):
    username: str
    password: str

class StoreStateUpdateDTO(BaseModel):
    store_id: str

    class Config:
        extra = "forbid"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT,
            store_id TEXT,
            scopes TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_id TEXT,
            store_id TEXT,
            cashier_id TEXT,
            product_id TEXT,
            amount REAL,
            discount_pct REAL,
            is_approved INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name TEXT,
            price REAL,
            category TEXT,
            emoji TEXT
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('Administrador', 'ADMON', 'admin', 'STORE-711-MEX', 'admin:branding sales:write inventory:read')")
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('Cajero1', '1234', 'cashier', 'STORE-711-MEX', 'sales:write inventory:read')")
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('Cajero2', '1234', 'cashier', 'STORE-711-GDA', 'sales:write inventory:read')")

    items = [
        ('SKU-101', 'Cafe 7-Select 12oz', 26.50, 'Bebidas', '☕'),
        ('SKU-102', 'Refresco Gulp 30oz', 22.00, 'Bebidas', '🥤'),
        ('SKU-103', 'Agua Mineral 600ml', 16.00, 'Bebidas', '💧'),
        ('SKU-104', 'Jugo Naranja Natural', 28.00, 'Bebidas', '🧃'),
        ('SKU-105', 'Cerveza Lata 355ml', 24.00, 'Bebidas', '🍺'),
        ('SKU-106', 'Te Helado Limon', 21.50, 'Bebidas', '🧋'),
        ('SKU-201', 'Hot Dog Big Bite', 38.00, 'Comida', '🌭'),
        ('SKU-202', 'Pizza Clasica Rebanada', 32.00, 'Comida', '🍕'),
        ('SKU-203', 'Hamburguesa Res', 52.00, 'Comida', '🍔'),
        ('SKU-204', 'Sandwich Jamon y Queso', 42.00, 'Comida', '🥪'),
        ('SKU-205', 'Tacos Surtidos (3pz)', 48.00, 'Comida', '🌮'),
        ('SKU-206', 'Burrito Norteño Frijol', 35.00, 'Comida', '🌯'),
        ('SKU-301', 'Manzana Roja Fresca', 12.00, 'Frutas', '🍎'),
        ('SKU-302', 'Platano Tabasco', 8.50, 'Frutas', '🍌'),
        ('SKU-303', 'Vaso Sandia Picada', 25.00, 'Frutas', '🍉'),
        ('SKU-304', 'Uvas Verdes Sin Semilla', 34.00, 'Frutas', '🍇'),
        ('SKU-305', 'Vaso Pina con Chile', 25.00, 'Frutas', '🍍'),
        ('SKU-401', 'Papas Fritas Sal 170g', 36.00, 'Snacks', '🥔'),
        ('SKU-402', 'Nachos con Queso', 39.00, 'Snacks', '🧀'),
        ('SKU-403', 'Palomitas Mantequilla', 24.00, 'Snacks', '🍿'),
        ('SKU-404', 'Pretzel Horneado Salado', 19.50, 'Snacks', '🥨'),
        ('SKU-501', 'Dona Glaseada', 18.00, 'Postres', '🍩'),
        ('SKU-502', 'Galleta Chispas Chocolate', 16.50, 'Postres', '🍪'),
        ('SKU-503', 'Helado Vainilla Cono', 25.00, 'Postres', '🍦'),
        ('SKU-504', 'Pastel Chocolate Rebanada', 35.00, 'Postres', '🍰'),
        ('SKU-505', 'Muffin Arandanos', 22.00, 'Postres', '🧁'),
        ('SKU-601', 'Paracetamol 500mg', 30.00, 'Farmacia', '💊'),
        ('SKU-602', 'Curitas Adhesivas Pack', 18.00, 'Farmacia', '🩹'),
        ('SKU-603', 'Pilas Alcalinas AA (2pz)', 45.00, 'Farmacia', '🔋')
    ]
    cursor.executemany("INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?, ?)", items)
    conn.commit()
    conn.close()

init_db()

HTML_TO_BE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>7-Eleven POS Terminal (To-Be Secure)</title>
    <style>
        :root { --p-green: #008060; --p-orange: #EE6A1A; --p-blue: #0284c7; --bg: #0b0f17; --surface: #151d28; --text: #e6edf3; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { background: var(--bg); color: var(--text); padding: 15px; overflow-x: hidden; }
        header { display: flex; justify-content: space-between; align-items: center; background: var(--surface); padding: 15px 20px; border-radius: 8px; border-bottom: 4px solid var(--p-green); margin-bottom: 15px; border: 1px solid #233044; }
        .brand-box { display: flex; align-items: center; gap: 15px; }
        .logo-img { height: 50px; object-fit: contain; }
        .status-badge { background: #00806026; color: #22c55e; border: 1px solid #22c55e; padding: 6px 14px; border-radius: 20px; font-weight: bold; font-size: 13px; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 0 10px rgba(34, 197, 94, 0.15); }
        .jwt-badge { background: #0284c726; color: #38bdf8; border: 1px solid #0284c7; padding: 3px 8px; border-radius: 6px; font-size: 11px; margin-left: 5px; }

        /* Botones exclusivos para Administrador en To-Be */
        .admin-nav-btn {
            background: #1c2636;
            border: 1px solid #28374d;
            color: #e6edf3;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            margin-right: 8px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: 0.2s;
        }
        .admin-nav-btn:hover { background: #24334a; border-color: var(--p-green); }

        #login-overlay, #receipt-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.85); display: flex; justify-content: center; align-items: center; z-index: 9999; }
        #receipt-overlay { display: none; }
        .modal-card { background: var(--surface); padding: 25px; border-radius: 8px; width: 420px; text-align: center; border: 1px solid #233044; }
        .modal-card input { width: 100%; padding: 10px; margin: 8px 0; background: #0b0f17; border: 1px solid #233044; color: #fff; border-radius: 4px; }
        .modal-card button { width: 100%; padding: 10px; background: var(--p-green); color: #fff; border: none; font-weight: bold; cursor: pointer; border-radius: 4px; margin-top: 10px; }

        .receipt-ticket { background: #fff; color: #111; padding: 20px; border-radius: 6px; font-family: 'Courier New', monospace; font-size: 13px; text-align: left; max-height: 480px; overflow-y: auto; }
        .receipt-logo { height: 45px; object-fit: contain; display: block; margin: 0 auto 8px auto; filter: grayscale(100%) contrast(150%); }
        .receipt-ticket h3 { text-align: center; margin-bottom: 2px; }
        .receipt-ticket hr { border: none; border-top: 1px dashed #444; margin: 8px 0; }
        .receipt-item-row { display: flex; justify-content: space-between; margin-bottom: 4px; }

        /* CONTENEDOR FLEXIBLE DINÁMICO (EMPUJE HACIA LA IZQUIERDA) */
        .viewport-wrapper {
            display: flex;
            width: 100%;
            gap: 0;
            transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .pos-section {
            flex: 1 1 auto;
            min-width: 0;
            transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .side-panel {
            width: 0;
            min-width: 0;
            opacity: 0;
            overflow: hidden;
            background: var(--surface);
            border-radius: 8px;
            transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
            margin-left: 0;
            border: 1px solid transparent;
        }
        .side-panel.active {
            width: 380px;
            min-width: 380px;
            opacity: 1;
            margin-left: 15px;
            border-color: #233044;
            overflow-y: auto;
        }

        /* Hot Edge lateral derecho */
        #hot-edge-zone {
            position: fixed;
            top: 0;
            right: 0;
            width: 15px;
            height: 100vh;
            z-index: 9990;
            background: transparent;
        }

        .card { background: var(--surface); padding: 16px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #233044; }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid #233044; padding-bottom: 6px; font-size: 14px; color: #94a3b8; font-weight: 600; }
        
        .cat-bar { display: flex; gap: 6px; overflow-x: auto; margin-bottom: 12px; padding-bottom: 4px; }
        .cat-tab { background: #1c2636; border: 1px solid #28374d; color: #cbd5e1; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; cursor: pointer; white-space: nowrap; }
        .cat-tab.active, .cat-tab:hover { background: var(--p-green); color: #fff; border-color: var(--p-green); }

        .catalog-scroll { max-height: 310px; overflow-y: auto; padding-right: 5px; margin-bottom: 15px; }
        .catalog-scroll::-webkit-scrollbar { width: 6px; }
        .catalog-scroll::-webkit-scrollbar-track { background: #0a0e14; border-radius: 4px; }
        .catalog-scroll::-webkit-scrollbar-thumb { background: #28374d; border-radius: 4px; }
        .catalog-scroll::-webkit-scrollbar-thumb:hover { background: var(--p-green); }

        .grid-products { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 10px; }
        .prod-btn { background: #1c2636; border: 1px solid #28374d; border-radius: 8px; padding: 10px 6px; color: #fff; text-align: center; cursor: pointer; transition: 0.2s; display: flex; flex-direction: column; justify-content: space-between; }
        .prod-btn:hover { background: #24334a; border-color: var(--p-green); transform: translateY(-2px); }
        .prod-emoji { font-size: 26px; margin-bottom: 4px; }
        .prod-title { font-size: 12px; font-weight: 500; height: 32px; overflow: hidden; line-height: 1.2; }
        .prod-price { color: #22c55e; font-weight: bold; margin-top: 6px; font-size: 13px; }

        table { width: 100%; border-collapse: collapse; margin-bottom: 10px; font-size: 13px; }
        th, td { padding: 6px 8px; text-align: left; border-bottom: 1px solid #233044; }
        th { color: #94a3b8; }
        .total-box { display: flex; justify-content: space-between; font-size: 18px; font-weight: bold; padding: 10px 0; border-top: 2px dashed #334155; }
        input, button { padding: 9px 12px; border-radius: 4px; border: 1px solid #233044; background: #0b0f17; color: #fff; font-size: 13px; }
        .btn-action { background: var(--p-green); border: none; font-weight: bold; cursor: pointer; color: white; }
        .btn-action:hover { background: #009973; }
        .btn-disabled { opacity: 0.4; cursor: not-allowed !important; }
        pre { background: #05080c; border: 1px solid #1a2332; padding: 10px; border-radius: 4px; color: #38bdf8; font-size: 11px; overflow-x: auto; max-height: 120px; }
    </style>
</head>
<body>

    <!-- Zona sensible invisible de borde (Hot Edge) -->
    <div id="hot-edge-zone"></div>

    <div id="login-overlay">
        <div class="modal-card" style="border-top: 4px solid var(--p-green);">
            <img id="login-logo" src="https://upload.wikimedia.org/wikipedia/commons/4/40/7-eleven_logo.svg" style="height: 55px; margin-bottom: 10px;">
            <h3>🔒 Punto de Venta Seguro (Zero Trust)</h3>
            <p style="font-size: 12px; color: #94a3b8; margin-bottom: 15px;">Autenticación criptográfica con JWT y Scopes</p>
            <input type="text" id="log_user" placeholder="Usuario (Administrador, Cajero1, Cajero2)">
            <input type="password" id="log_pass" placeholder="Contraseña">
            <button onclick="login()">AUTENTICAR Y FIRMAR TOKEN</button>
            <div style="font-size: 11px; color: #64748b; margin-top: 15px; text-align: left;">
                • Admin: <b>Administrador</b> / <b>ADMON</b><br>
                • Operador: <b>Cajero1</b> / <b>1234</b> | <b>Cajero2</b> / <b>1234</b>
            </div>
        </div>
    </div>

    <div id="receipt-overlay">
        <div class="modal-card" style="width: 420px; padding: 20px;">
            <div class="receipt-ticket" id="receipt-content"></div>
            <button class="btn-action" style="margin-top: 15px; width: 100%;" onclick="closeReceipt()">CERRAR E INICIAR NUEVA VENTA</button>
        </div>
    </div>

    <header>
        <div class="brand-box">
            <img id="store-logo" class="logo-img" src="https://upload.wikimedia.org/wikipedia/commons/4/40/7-eleven_logo.svg">
            <div>
                <h2>🔒 Terminal POS #04 — 7-Eleven Seguro (To-Be)</h2>
                <small style="color: #94a3b8;">Usuario: <span class="jwt-badge" id="session-user">Desconectado</span> | Tenant: <span class="jwt-badge" id="session-store">-</span> | Rol: <span class="jwt-badge" id="session-role">-</span></small>
            </div>
        </div>
        <div style="display: flex; align-items: center;">
            <!-- Módulos EXCLUSIVOS del Administrador en To-Be -->
            <button class="admin-nav-btn" id="btn-sec-console" style="display: none;" onclick="togglePanel('panel-console')">⚡ Security Console</button>
            <button class="admin-nav-btn" id="btn-apisec-insp" style="display: none;" onclick="togglePanel('panel-inspector')">🛡️ API Sec Inspector</button>

            <button class="btn-action" style="padding: 6px 12px; background: #334155; margin-right: 10px;" onclick="logout()">Cerrar Sesión</button>
            <span class="status-badge">🔒 MODO SEGURO ACTIVO ✅</span>
        </div>
    </header>

    <!-- Envoltorio dinámico con empuje hacia la izquierda -->
    <div class="viewport-wrapper">
        <div class="pos-section">
            <div class="card">
                <div class="card-header">
                    <span>CATÁLOGO REGISTRADOR BLINDADO (SHIFT-LEFT)</span>
                    <small>Filtre por categoría o use scroll</small>
                </div>

                <div class="cat-bar">
                    <button class="cat-tab active" onclick="filterCat('TODOS', this)">Todos</button>
                    <button class="cat-tab" onclick="filterCat('Bebidas', this)">☕ Bebidas</button>
                    <button class="cat-tab" onclick="filterCat('Comida', this)">🌭 Comida</button>
                    <button class="cat-tab" onclick="filterCat('Frutas', this)">🍎 Frutas</button>
                    <button class="cat-tab" onclick="filterCat('Snacks', this)">🍿 Snacks</button>
                    <button class="cat-tab" onclick="filterCat('Postres', this)">🍩 Postres</button>
                    <button class="cat-tab" onclick="filterCat('Farmacia', this)">💊 Farmacia</button>
                </div>

                <div class="catalog-scroll">
                    <div class="grid-products" id="products-grid"></div>
                </div>

                <div class="card-header">
                    <span>TICKET DE VENTA PROTEGIDO</span>
                    <button class="btn-action" style="padding: 4px 8px; font-size: 11px; background: #334155;" onclick="clearCart()">Limpiar Carrito</button>
                </div>
                <table>
                    <thead><tr><th>SKU</th><th>Artículo</th><th>Precio</th><th>Total</th></tr></thead>
                    <tbody id="cart-rows"><tr><td colspan="4" style="text-align: center; color: #64748b;">Sin artículos en caja</td></tr></tbody>
                </table>
                <div class="total-box">
                    <span>TOTAL A PAGAR:</span>
                    <span id="cart-total" style="color: #22c55e;">$0.00</span>
                </div>
                <button id="btn-checkout" class="btn-action btn-disabled" style="width: 100%; padding: 12px; margin-top: 10px;" onclick="checkoutSecure()">COBRAR TRANSACCIÓN SEGURA (FASTAPI + DTO)</button>
            </div>

            <div class="card" id="admin-logo-box" style="border-left: 3px solid var(--p-green); display: none;">
                <div class="card-header">⚙️ MÓDULO ADMINISTRADOR: LOGOTIPO INSTITUCIONAL 7-ELEVEN</div>
                <p style="font-size: 12px; color: #94a3b8; margin-bottom: 8px;">Logotipo sincronizado mediante almacenamiento local para ambas terminales:</p>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <input type="file" id="logo-file" accept="image/*" onchange="uploadLogo(event)" style="font-size: 11px;">
                    <button class="btn-action" style="background: #334155;" onclick="resetLogo()">Restaurar Logo Default</button>
                </div>
            </div>
        </div>

        <!-- 1. Panel de Pruebas de Mitigación (Activado por Hot Edge) -->
        <div class="side-panel" id="panel-attacks">
            <div class="card" style="border-left: 3px solid var(--p-green); margin-bottom: 0; height: 100%;">
                <div class="card-header" style="color: #22c55e;">
                    <span>🔒 PRUEBAS DE MITIGACIÓN (ZERO TRUST) ✅</span>
                    <button onclick="closeAllPanels()" style="background:none; border:none; color:#8fa0b5; cursor:pointer;">✕</button>
                </div>
                
                <div style="margin-bottom: 14px;">
                    <label style="font-size: 12px; font-weight: bold; color: #cbd5e1;">1. Intento Inyección SQL en Catálogo</label>
                    <input type="text" id="query_in" value="Cafe' UNION SELECT--" style="width: 100%; margin: 5px 0;">
                    <button class="btn-action" style="width: 100%;" onclick="runSafeQuery()">Comprobar Filtro Shift-Left</button>
                    <pre id="out-query">// Respuesta de bloqueo...</pre>
                </div>

                <div style="margin-bottom: 14px;">
                    <label style="font-size: 12px; font-weight: bold; color: #cbd5e1;">2. Intento de Acceso a Otra Tienda (BOLA)</label>
                    <div style="display: flex; gap: 5px; margin: 5px 0;">
                        <input type="text" id="store_target" value="STORE-711-GDA" style="width: 50%;">
                        <button class="btn-action" style="width: 50%;" onclick="runSafeBola()">Validar Tenant</button>
                    </div>
                    <pre id="out-bola">// Respuesta de autorización...</pre>
                </div>

                <div>
                    <label style="font-size: 12px; font-weight: bold; color: #cbd5e1;">3. Intento Fraude Mass Assignment</label>
                    <p style="font-size: 11px; color: #94a3b8; margin-top: 2px;">Intenta inyectar discount_pct=100 en la API segura:</p>
                    <button class="btn-action" style="width: 100%; margin-top: 5px;" onclick="runSafeMass()">Intentar Inyectar discount_pct=100</button>
                    <pre id="out-mass">// DTO extra=forbid...</pre>
                </div>
            </div>
        </div>

        <!-- 2. Panel Security Console (Exclusivo Administrador) -->
        <div class="side-panel" id="panel-console">
            <div class="card" style="border-left: 3px solid #38bdf8; margin-bottom: 0; height: 100%;">
                <div class="card-header" style="color: #38bdf8;">
                    <span>⚡ Security Console</span>
                    <button onclick="closeAllPanels()" style="background:none; border:none; color:#8fa0b5; cursor:pointer;">✕</button>
                </div>
                <p style="font-size: 12px; color: #94a3b8; margin-bottom: 12px;">Módulo de telemetría y monitoreo de sesiones Zero Trust:</p>
                <div class="card" style="border: 1px solid #233044; background: #0b0f17;">
                    <h4 style="font-size: 13px; color: #38bdf8; margin-bottom: 6px;">Runtime de Seguridad</h4>
                    <p style="font-size: 11px; color: #cbd5e1; line-height: 1.5;">
                        • Framework: FastAPI / ASGI<br>
                        • Tenant ID: STORE-711-MEX<br>
                        • Validación JWT: Activa (HS256)<br>
                        • Políticas DTO: extra='forbid'
                    </p>
                </div>
            </div>
        </div>

        <!-- 3. Panel API Sec Inspector (Exclusivo Administrador) -->
        <div class="side-panel" id="panel-inspector">
            <div class="card" style="border-left: 3px solid #38bdf8; margin-bottom: 0; height: 100%;">
                <div class="card-header" style="color: #38bdf8;">
                    <span>🛡️ API Sec Inspector</span>
                    <button onclick="closeAllPanels()" style="background:none; border:none; color:#8fa0b5; cursor:pointer;">✕</button>
                </div>
                <p style="font-size: 12px; color: #94a3b8; margin-bottom: 12px;">Inspección y gobernanza de contratos OpenAPI:</p>
                <div class="card" style="border: 1px solid #233044; background: #0b0f17;">
                    <h4 style="font-size: 13px; color: #38bdf8; margin-bottom: 6px;">Contratos y Mitigaciones</h4>
                    <p style="font-size: 11px; color: #cbd5e1; line-height: 1.5;">
                        • OWASP API1 (BOLA): Mitigado (403)<br>
                        • OWASP API6 (Mass Assig.): Mitigado (422)<br>
                        • OWASP API8 (SQLi): Mitigado (Parametrizado)<br>
                        • Enlace Swagger: <a href="/docs" target="_blank" style="color: #38bdf8;">Abrir /docs</a>
                    </p>
                </div>
            </div>
        </div>
    </div>

    <script>
        let cart = [];
        let JWT_TOKEN = "";
        let decodedClaims = null;
        let catalog = [];

        const hotEdge = document.getElementById('hot-edge-zone');
        const panelAttacks = document.getElementById('panel-attacks');

        // Borde sensible para pruebas de mitigación
        hotEdge.addEventListener('mouseenter', () => {
            closeAllPanels();
            panelAttacks.classList.add('active');
        });
        panelAttacks.addEventListener('mouseleave', () => {
            panelAttacks.classList.remove('active');
        });

        function closeAllPanels() {
            document.querySelectorAll('.side-panel').forEach(p => p.classList.remove('active'));
        }

        function togglePanel(id) {
            const target = document.getElementById(id);
            const wasActive = target.classList.contains('active');
            closeAllPanels();
            if(!wasActive) {
                target.classList.add('active');
            }
        }

        function getActiveLogo() {
            return localStorage.getItem('7eleven_pos_logo') || "https://upload.wikimedia.org/wikipedia/commons/4/40/7-eleven_logo.svg";
        }

        function loadSavedLogo() {
            const logo = getActiveLogo();
            document.getElementById('store-logo').src = logo;
            document.getElementById('login-logo').src = logo;
        }

        async function fetchProducts() {
            if(!JWT_TOKEN) return;
            const res = await fetch('/api/v1/pos/products?query=all', {
                headers: { 'Authorization': `Bearer ${JWT_TOKEN}` }
            });
            catalog = await res.json();
            renderCatalog(catalog);
        }

        function renderCatalog(items) {
            const grid = document.getElementById('products-grid');
            grid.innerHTML = items.map(p => `
                <div class="prod-btn" onclick="addToCart('${p.id}', '${p.name}', ${p.price}, '${p.emoji}')">
                    <div class="prod-emoji">${p.emoji || '📦'}</div>
                    <div class="prod-title">${p.name}</div>
                    <div class="prod-price">$${p.price.toFixed(2)}</div>
                </div>
            `).join('');
        }

        function filterCat(cat, btn) {
            document.querySelectorAll('.cat-tab').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            if(cat === 'TODOS') {
                renderCatalog(catalog);
            } else {
                renderCatalog(catalog.filter(p => p.category === cat));
            }
        }

        async function login() {
            const user = document.getElementById('log_user').value;
            const pass = document.getElementById('log_pass').value;
            const res = await fetch('/api/v1/auth/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ username: user, password: pass })
            });
            const data = await res.json();
            if(res.status === 200) {
                JWT_TOKEN = data.token;
                decodedClaims = data.claims;

                document.getElementById('session-user').innerText = decodedClaims.sub;
                document.getElementById('session-store').innerText = decodedClaims.store_id;
                document.getElementById('session-role').innerText = decodedClaims.role;
                document.getElementById('login-overlay').style.display = 'none';

                // Mostrar controles exclusivos para Administrador en To-Be
                if(decodedClaims.role === 'admin') {
                    document.getElementById('admin-logo-box').style.display = 'block';
                    document.getElementById('btn-sec-console').style.display = 'inline-flex';
                    document.getElementById('btn-apisec-insp').style.display = 'inline-flex';
                } else {
                    document.getElementById('admin-logo-box').style.display = 'none';
                    document.getElementById('btn-sec-console').style.display = 'none';
                    document.getElementById('btn-apisec-insp').style.display = 'none';
                }

                await fetchProducts();
            } else {
                alert('Credenciales incorrectas: ' + (data.detail || 'Fallo de autenticación'));
            }
        }

        function logout() {
            JWT_TOKEN = "";
            decodedClaims = null;
            document.getElementById('login-overlay').style.display = 'flex';
            document.getElementById('log_pass').value = '';
            document.getElementById('admin-logo-box').style.display = 'none';
            document.getElementById('btn-sec-console').style.display = 'none';
            document.getElementById('btn-apisec-insp').style.display = 'none';
            document.getElementById('session-user').innerText = 'Desconectado';
            document.getElementById('session-store').innerText = '-';
            document.getElementById('session-role').innerText = '-';
            closeAllPanels();
            clearCart();
        }

        function uploadLogo(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(evt) {
                    const dataUrl = evt.target.result;
                    document.getElementById('store-logo').src = dataUrl;
                    document.getElementById('login-logo').src = dataUrl;
                    localStorage.setItem('7eleven_pos_logo', dataUrl);
                };
                reader.readAsDataURL(file);
            }
        }

        function resetLogo() {
            const def = "https://upload.wikimedia.org/wikipedia/commons/4/40/7-eleven_logo.svg";
            document.getElementById('store-logo').src = def;
            document.getElementById('login-logo').src = def;
            localStorage.removeItem('7eleven_pos_logo');
        }

        function addToCart(sku, name, price, emoji) {
            cart.push({ sku, name, price, emoji: emoji || '📦' });
            renderCart();
        }
        function clearCart() { cart = []; renderCart(); }
        function renderCart() {
            const tbody = document.getElementById('cart-rows');
            const btnCheckout = document.getElementById('btn-checkout');
            let total = 0;
            if(cart.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #64748b;">Sin artículos en caja</td></tr>';
                document.getElementById('cart-total').innerText = "$0.00";
                btnCheckout.classList.add('btn-disabled');
                return;
            }
            btnCheckout.classList.remove('btn-disabled');
            tbody.innerHTML = cart.map(item => {
                total += item.price;
                return `<tr><td>${item.sku}</td><td>${item.emoji} ${item.name}</td><td>$${item.price.toFixed(2)}</td><td>$${item.price.toFixed(2)}</td></tr>`;
            }).join('');
            document.getElementById('cart-total').innerText = `$${total.toFixed(2)}`;
        }

        async function checkoutSecure() {
            if(!JWT_TOKEN) return alert('Debe iniciar turno primero');
            if(cart.length === 0) {
                return alert('⚠️ ACCIÓN DENEGADA: No hay artículos escaneados en caja para procesar el cobro.');
            }
            const res = await fetch('/api/v1/pos/transactions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${JWT_TOKEN}` },
                body: JSON.stringify({ items: cart })
            });
            const data = await res.json();
            if(res.status === 201) {
                showReceipt(data);
            } else {
                alert('Cobro rechazado por política de seguridad: ' + JSON.stringify(data.detail));
            }
        }

        async function runSafeMass() {
            if(!JWT_TOKEN) return alert('Debe iniciar sesión primero');
            const payload = {
                store_id: decodedClaims ? decodedClaims.store_id : "STORE-711-MEX",
                discount_pct: 100
            };
            const res = await fetch('/api/v1/pos/inject-discount', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${JWT_TOKEN}` },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            document.getElementById('out-mass').innerText = `HTTP ${res.status} RECHAZADO SHIFT-LEFT:\\n` + JSON.stringify(data, null, 2);
            alert(`🔒 BLOQUEO INMEDIATO POR API (HTTP ${res.status}):\\nEl contrato DTO rechazó el parámetro no autorizado "discount_pct" (extra=forbid).\\nLa terminal queda 100% limpia y protegida contra fraudes.`);
        }

        function showReceipt(rcp) {
            const container = document.getElementById('receipt-content');
            const logoSrc = getActiveLogo();
            let itemsHtml = rcp.items.map(it => `
                <div class="receipt-item-row">
                    <span>${it.emoji || '📦'} ${it.sku} - ${it.name}</span>
                    <span>$${it.price.toFixed(2)}</span>
                </div>
            `).join('');

            container.innerHTML = `
                <img src="${logoSrc}" class="receipt-logo" alt="7-Eleven Logo Monocromo">
                <h3>*** 7-ELEVEN MEXICO ***</h3>
                <center style="font-size: 11px;">TIENDA ZERO TRUST #${rcp.store_id}<br>🔒 TERMINAL #04 - CAJA SEGURA ✅</center>
                <hr>
                <div><b>FOLIO RECIBO:</b> ${rcp.receipt_id}</div>
                <div><b>FECHA/HORA:</b> ${rcp.timestamp}</div>
                <div><b>CAJERO EN TURNO:</b> ${rcp.cashier_id}</div>
                <div><b>ESTADO TRANSACCIÓN:</b> ${rcp.status}</div>
                <hr>
                <div style="font-weight: bold; margin-bottom: 5px;">DESGLOSE DE ARTÍCULOS (${rcp.items.length}):</div>
                ${itemsHtml}
                <hr>
                <div class="receipt-item-row">
                    <span>SUBTOTAL REAL:</span>
                    <span>$${rcp.subtotal.toFixed(2)}</span>
                </div>
                <div class="receipt-item-row" style="font-size: 11px; color: #555;">
                    <span>DESCUENTO AUTORIZADO:</span>
                    <span>${rcp.discount_pct}%</span>
                </div>
                <div class="receipt-item-row" style="font-size: 14px; font-weight: bold; margin-top: 5px;">
                    <span>TOTAL A PAGAR:</span>
                    <span>$${rcp.total_amount.toFixed(2)}</span>
                </div>
                <hr>
                <center style="font-size: 11px;">*** AUTORIZACIÓN CRIPTOGRÁFICA JWT EXITOSA ***<br>¡GRACIAS POR SU COMPRA!</center>
            `;
            document.getElementById('receipt-overlay').style.display = 'flex';
        }

        function closeReceipt() {
            document.getElementById('receipt-overlay').style.display = 'none';
            clearCart();
        }

        async function runSafeQuery() {
            if(!JWT_TOKEN) return alert('Debe iniciar sesión primero');
            const q = document.getElementById('query_in').value;
            const res = await fetch(`/api/v1/pos/products?query=${encodeURIComponent(q)}`, {
                headers: { 'Authorization': `Bearer ${JWT_TOKEN}` }
            });
            document.getElementById('out-query').innerText = `HTTP ${res.status}\\n` + JSON.stringify(await res.json(), null, 2);
        }

        async function runSafeBola() {
            if(!JWT_TOKEN) return alert('Debe iniciar sesión primero');
            const store = document.getElementById('store_target').value;
            const res = await fetch(`/api/v1/stores/${store}/sales`, {
                headers: { 'Authorization': `Bearer ${JWT_TOKEN}` }
            });
            document.getElementById('out-bola').innerText = `HTTP ${res.status} FORBIDDEN\\n` + JSON.stringify(await res.json(), null, 2);
        }

        loadSavedLogo();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_TO_BE

@app.post("/api/v1/auth/login")
def login(request: LoginRequest):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username, role, store_id, scopes FROM users WHERE username = ? AND password = ?", (request.username, request.password))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas.")

    claims = {
        "sub": row[0],
        "role": row[1],
        "store_id": row[2],
        "scope": row[3],
        "exp": int(time.time()) + 86400
    }
    token = jwt.encode(claims, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"token": token, "claims": claims}

@app.get("/api/v1/pos/products", response_model=List[Dict[str, Any]])
def search_products(
    params: ProductSearchDTO = Depends(),
    claims: Dict[str, Any] = Depends(check_scope("inventory:read"))
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if params.query.lower() == "all":
        cursor.execute("SELECT id, name, price, category, emoji FROM products")
    else:
        cursor.execute("SELECT id, name, price, category, emoji FROM products WHERE name LIKE ?", (f"%{params.query}%",))
    data = [{"id": r[0], "name": r[1], "price": r[2], "category": r[3], "emoji": r[4]} for r in cursor.fetchall()]
    conn.close()
    return data

@app.get("/api/v1/stores/{store_id}/sales")
def get_store_sales(
    store_id: str,
    claims: Dict[str, Any] = Depends(check_scope("sales:write"))
):
    token_store = claims.get("store_id")
    if token_store != store_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error_code": "SEC_BOLA_VIOLATION",
                "message": f"Acceso denegado: El token autoriza la tienda {token_store}, no la tienda {store_id}"
            }
        )
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, receipt_id, store_id, amount, discount_pct FROM transactions WHERE store_id = ?", (store_id,))
    sales = [{"id": r[0], "receipt_id": r[1], "store_id": r[2], "amount": r[3], "discount": r[4]} for r in cursor.fetchall()]
    conn.close()
    return {"store_id": store_id, "sales": sales}

@app.post("/api/v1/pos/inject-discount")
def inject_discount(
    payload: StoreStateUpdateDTO,
    claims: Dict[str, Any] = Depends(check_scope("sales:write"))
):
    return {"status": "ok", "message": "Terminal válida."}

@app.post("/api/v1/pos/transactions", response_model=ReceiptResponseDTO, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreateDTO,
    claims: Dict[str, Any] = Depends(check_scope("sales:write"))
):
    store_id = claims.get("store_id")
    cashier_id = claims.get("sub")
    fixed_discount = 0.0
    is_approved = 1
    receipt_id = f"REC-711-{int(time.time())}"
    subtotal = sum(item.price for item in payload.items)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for item in payload.items:
        cursor.execute("""
            INSERT INTO transactions (receipt_id, store_id, cashier_id, product_id, amount, discount_pct, is_approved)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (receipt_id, store_id, cashier_id, item.sku, item.price, fixed_discount, is_approved))
    conn.commit()
    conn.close()

    return ReceiptResponseDTO(
        receipt_id=receipt_id,
        store_id=store_id,
        cashier_id=cashier_id,
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        items=payload.items,
        subtotal=round(subtotal, 2),
        total_amount=round(subtotal, 2),
        discount_pct=fixed_discount,
        status="APPROVED_ZERO_TRUST"
    )