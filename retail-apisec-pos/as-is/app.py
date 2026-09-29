"""
Punto de Venta 7-Eleven - Escenario As-Is (Vulnerable)
Efecto dinámico de empuje lateral hacia la izquierda (sin sobreposición).
"""

from flask import Flask, request, jsonify, render_template_string
import sqlite3
import time

app = Flask(__name__)
DB_NAME = "pos_legacy.db"

TERMINAL_STATE = {
    "STORE-101": {"injected_discount_pct": 0.0, "is_poisoned": False}
}

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT,
            store_id TEXT
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
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('Administrador', 'ADMON', 'admin', 'STORE-101')")
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('Cajero1', '1234', 'cashier', 'STORE-101')")
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('Cajero2', '1234', 'cashier', 'STORE-102')")

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

HTML_AS_IS = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>7-Eleven POS Terminal (As-Is Legacy)</title>
    <style>
        :root { --p-green: #008060; --p-orange: #EE6A1A; --p-red: #D71920; --bg: #111418; --surface: #1e222b; --text: #f0f3f6; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { background: var(--bg); color: var(--text); padding: 15px; overflow-x: hidden; }
        header { display: flex; justify-content: space-between; align-items: center; background: var(--surface); padding: 15px 20px; border-radius: 8px; border-bottom: 4px solid var(--p-red); margin-bottom: 15px; }
        .brand-box { display: flex; align-items: center; gap: 15px; }
        .logo-img { height: 50px; object-fit: contain; }
        .status-badge { background: #ff334b22; color: #ff5263; border: 1px solid #ff5263; padding: 5px 12px; border-radius: 20px; font-weight: bold; font-size: 13px; }
        .user-badge { background: #334155; color: #fff; padding: 3px 8px; border-radius: 4px; font-size: 12px; }

        #login-overlay, #receipt-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.85); display: flex; justify-content: center; align-items: center; z-index: 9999; }
        #receipt-overlay { display: none; }
        .modal-card { background: var(--surface); padding: 25px; border-radius: 8px; width: 420px; text-align: center; border: 1px solid #363d4e; }
        .modal-card input { width: 100%; padding: 10px; margin: 8px 0; background: #111418; border: 1px solid #363d4e; color: #fff; border-radius: 4px; }
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
        .attacks-section {
            width: 0;
            min-width: 0;
            opacity: 0;
            overflow: hidden;
            background: var(--surface);
            border-radius: 8px;
            transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
            margin-left: 0;
        }
        .attacks-section.active {
            width: 380px;
            min-width: 380px;
            opacity: 1;
            margin-left: 15px;
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

        .card { background: var(--surface); padding: 16px; border-radius: 8px; margin-bottom: 15px; }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid #2d3342; padding-bottom: 6px; font-size: 14px; color: #8fa0b5; font-weight: 600; }
        
        .cat-bar { display: flex; gap: 6px; overflow-x: auto; margin-bottom: 12px; padding-bottom: 4px; }
        .cat-tab { background: #272c38; border: 1px solid #363d4e; color: #cbd5e1; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; cursor: pointer; white-space: nowrap; }
        .cat-tab.active, .cat-tab:hover { background: var(--p-orange); color: #fff; border-color: var(--p-orange); }

        .catalog-scroll { max-height: 310px; overflow-y: auto; padding-right: 5px; margin-bottom: 15px; }
        .catalog-scroll::-webkit-scrollbar { width: 6px; }
        .catalog-scroll::-webkit-scrollbar-track { background: #151820; border-radius: 4px; }
        .catalog-scroll::-webkit-scrollbar-thumb { background: #3a4253; border-radius: 4px; }
        .catalog-scroll::-webkit-scrollbar-thumb:hover { background: var(--p-orange); }

        .grid-products { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 10px; }
        .prod-btn { background: #272c38; border: 1px solid #363d4e; border-radius: 8px; padding: 10px 6px; color: #fff; text-align: center; cursor: pointer; transition: 0.2s; display: flex; flex-direction: column; justify-content: space-between; }
        .prod-btn:hover { background: #32394a; border-color: var(--p-orange); transform: translateY(-2px); }
        .prod-emoji { font-size: 26px; margin-bottom: 4px; }
        .prod-title { font-size: 12px; font-weight: 500; height: 32px; overflow: hidden; line-height: 1.2; }
        .prod-price { color: #4ade80; font-weight: bold; margin-top: 6px; font-size: 13px; }

        table { width: 100%; border-collapse: collapse; margin-bottom: 10px; font-size: 13px; }
        th, td { padding: 6px 8px; text-align: left; border-bottom: 1px solid #2d3342; }
        th { color: #8fa0b5; }
        .total-box { display: flex; justify-content: space-between; font-size: 18px; font-weight: bold; padding: 10px 0; border-top: 2px dashed #444; }
        input, button { padding: 9px 12px; border-radius: 4px; border: 1px solid #363d4e; background: #111418; color: #fff; font-size: 13px; }
        .btn-action { background: var(--p-orange); border: none; font-weight: bold; cursor: pointer; }
        .btn-danger { background: var(--p-red); border: none; font-weight: bold; cursor: pointer; }
        .btn-disabled { opacity: 0.4; cursor: not-allowed !important; }
        pre { background: #0b0d10; border: 1px solid #242933; padding: 10px; border-radius: 4px; color: #38bdf8; font-size: 11px; overflow-x: auto; max-height: 120px; }
    </style>
</head>
<body>

    <!-- Zona sensible invisible de borde (Hot Edge) -->
    <div id="hot-edge-zone"></div>

    <div id="login-overlay">
        <div class="modal-card" style="border-top: 4px solid var(--p-orange);">
            <img id="login-logo" src="https://upload.wikimedia.org/wikipedia/commons/4/40/7-eleven_logo.svg" style="height: 55px; margin-bottom: 10px;">
            <h3>Acceso Terminal POS</h3>
            <p style="font-size: 12px; color: #8fa0b5; margin-bottom: 15px;">Ingrese credenciales de operador o administración</p>
            <input type="text" id="log_user" placeholder="Usuario (Administrador, Cajero1, Cajero2)">
            <input type="password" id="log_pass" placeholder="Contraseña">
            <button onclick="login()">INICIAR TURNO</button>
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
                <h2>Terminal POS #04 — Sucursal Monterrey #101</h2>
                <small style="color: #8fa0b5;">Sesión: <span class="user-badge" id="session-user">Desconectado</span> | Rol: <span class="user-badge" id="session-role">-</span></small>
            </div>
        </div>
        <div>
            <button class="btn-action" style="padding: 6px 12px; background: #334155; margin-right: 10px;" onclick="logout()">Cerrar Turno</button>
            <span class="status-badge">REST API: INSEGURA (AS-IS)</span>
        </div>
    </header>

    <!-- Envoltorio dinámico con empuje hacia la izquierda -->
    <div class="viewport-wrapper">
        <div class="pos-section">
            <div class="card">
                <div class="card-header">
                    <span>CATÁLOGO DE PRODUCTOS EN CAJA</span>
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
                    <span>TICKET DE VENTA ACTUAL</span>
                    <button class="btn-action" style="padding: 4px 8px; font-size: 11px;" onclick="clearCart()">Limpiar Ticket</button>
                </div>
                <table>
                    <thead><tr><th>SKU</th><th>Artículo</th><th>Precio</th><th>Total</th></tr></thead>
                    <tbody id="cart-rows"><tr><td colspan="4" style="text-align: center; color: #666;">Sin artículos en caja</td></tr></tbody>
                </table>
                <div class="total-box">
                    <span>TOTAL A PAGAR:</span>
                    <span id="cart-total" style="color: #4ade80;">$0.00</span>
                </div>
                <button id="btn-checkout" class="btn-action btn-disabled" style="width: 100%; padding: 12px; margin-top: 10px;" onclick="checkoutLegit()">PROCESAR COBRO NORMAL (POST /transactions)</button>
            </div>

            <div class="card" id="admin-logo-box" style="border-left: 3px solid var(--p-green); display: none;">
                <div class="card-header">⚙️ MÓDULO ADMINISTRADOR: LOGOTIPO INSTITUCIONAL 7-ELEVEN</div>
                <p style="font-size: 12px; color: #8fa0b5; margin-bottom: 8px;">Cargue el logotipo corporativo para actualizar la carátula y el ticket impreso en B/N:</p>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <input type="file" id="logo-file" accept="image/*" onchange="uploadLogo(event)" style="font-size: 11px;">
                    <button class="btn-action" onclick="resetLogo()">Restaurar Logo Default</button>
                </div>
            </div>
        </div>

        <!-- Panel de Vectores integrado en el flujo (empuja al activarse) -->
        <div class="attacks-section" id="attacks-panel">
            <div class="card" style="border-left: 3px solid var(--p-red); margin-bottom: 0; height: 100%;">
                <div class="card-header" style="color: #ff5263;">
                    <span>VECTORES DE ATAQUE (OWASP)</span>
                    <button onclick="closeAttacks()" style="background:none; border:none; color:#8fa0b5; cursor:pointer;">✕</button>
                </div>
                
                <div style="margin-bottom: 14px;">
                    <label style="font-size: 12px; font-weight: bold; color: #e2e8f0;">1. Inyección SQL en Catálogo (OWASP API8)</label>
                    <input type="text" id="sqli_in" value="Cafe' UNION SELECT id, store_id, amount, 'x', 'x' FROM transactions--" style="width: 100%; margin: 5px 0;">
                    <button class="btn-danger" style="width: 100%;" onclick="exploitSQLi()">Exfiltrar Base de Datos</button>
                    <pre id="out-sqli">// Respuesta exfiltrada...</pre>
                </div>

                <div style="margin-bottom: 14px;">
                    <label style="font-size: 12px; font-weight: bold; color: #e2e8f0;">2. BOLA Fuga de Ventas (OWASP API1)</label>
                    <div style="display: flex; gap: 5px; margin: 5px 0;">
                        <input type="text" id="bola_store" value="STORE-102" style="width: 50%;">
                        <button class="btn-danger" style="width: 50%;" onclick="exploitBOLA()">Robar Tienda</button>
                    </div>
                    <pre id="out-bola">// Corte de tienda ajena...</pre>
                </div>

                <div>
                    <label style="font-size: 12px; font-weight: bold; color: #e2e8f0;">3. Mass Assignment Fraude (OWASP API6)</label>
                    <p style="font-size: 11px; color: #94a3b8; margin-top: 2px;">Inyecta discount_pct=100 en la sesión de caja vía REST API:</p>
                    <button class="btn-danger" style="width: 100%; margin-top: 5px;" onclick="exploitMass()">Inyectar discount_pct=100 vía REST API</button>
                    <pre id="out-mass">// Esperando inyección...</pre>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentUser = null;
        let cart = [];
        let catalog = [];

        const hotEdge = document.getElementById('hot-edge-zone');
        const attacksPanel = document.getElementById('attacks-panel');

        hotEdge.addEventListener('mouseenter', () => {
            attacksPanel.classList.add('active');
        });
        attacksPanel.addEventListener('mouseleave', () => {
            attacksPanel.classList.remove('active');
        });

        function closeAttacks() {
            attacksPanel.classList.remove('active');
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
            const res = await fetch('/api/v1/pos/products');
            const data = await res.json();
            catalog = data.data;
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
                currentUser = data.user;
                document.getElementById('session-user').innerText = currentUser.username;
                document.getElementById('session-role').innerText = currentUser.role;
                document.getElementById('login-overlay').style.display = 'none';

                if(currentUser.role === 'admin') {
                    document.getElementById('admin-logo-box').style.display = 'block';
                } else {
                    document.getElementById('admin-logo-box').style.display = 'none';
                }
            } else {
                alert('Credenciales incorrectas: ' + data.detail);
            }
        }

        function logout() {
            currentUser = null;
            document.getElementById('login-overlay').style.display = 'flex';
            document.getElementById('log_pass').value = '';
            document.getElementById('admin-logo-box').style.display = 'none';
            document.getElementById('session-user').innerText = 'Desconectado';
            document.getElementById('session-role').innerText = '-';
            closeAttacks();
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
                tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #666;">Sin artículos en caja</td></tr>';
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

        async function checkoutLegit() {
            if(cart.length === 0) {
                return alert('⚠️ ACCIÓN DENEGADA: No hay artículos escaneados en caja para procesar el cobro.');
            }
            const res = await fetch('/api/v1/pos/transactions', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    store_id: currentUser ? currentUser.store_id : 'STORE-101',
                    cashier_id: currentUser ? currentUser.username : 'Cajero1',
                    items: cart
                })
            });
            const data = await res.json();
            if(res.status === 201) {
                const wasPoisoned = data.receipt.discount_pct > 0;
                showReceipt(data.receipt, wasPoisoned);
            } else {
                alert('Error al cobrar: ' + (data.error || 'Fallo transaccional'));
            }
        }

        async function exploitMass() {
            const storeId = currentUser ? currentUser.store_id : 'STORE-101';
            const res = await fetch('/api/v1/pos/inject-discount', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    store_id: storeId,
                    discount_pct: 100,
                    is_approved: 1
                })
            });
            const data = await res.json();
            document.getElementById('out-mass').innerText = `HTTP ${res.status} INYECCIÓN REGISTRADA:\\n` + JSON.stringify(data, null, 2);
            alert('⚠️ PARÁMETRO INYECTADO POR REST API:\\nSe ha inyectado discount_pct=100 en la terminal ' + storeId + '.\\nPase artículos y presione "PROCESAR COBRO NORMAL" para verificar que saldrá en $0.00 pesos.');
        }

        function showReceipt(rcp, isExploit) {
            const container = document.getElementById('receipt-content');
            const logoSrc = getActiveLogo();
            let itemsHtml = rcp.items.map(it => `
                <div class="receipt-item-row">
                    <span>${it.emoji || '📦'} ${it.sku} - ${it.name}</span>
                    <span>$${it.price.toFixed(2)}</span>
                </div>
            `).join('');

            const exploitNotice = isExploit ? `
                <div style="background: #fee2e2; border: 1px solid #ef4444; color: #b91c1c; padding: 6px; border-radius: 4px; font-weight: bold; margin: 8px 0; text-align: center;">
                    🚨 ALERTA: FRAUDE MASS ASSIGNMENT DETECTADO (DESCUENTO 100% APLICADO) 🚨
                </div>
            ` : '';

            container.innerHTML = `
                <img src="${logoSrc}" class="receipt-logo" alt="7-Eleven Logo Monocromo">
                <h3>*** 7-ELEVEN MEXICO ***</h3>
                <center style="font-size: 11px;">TIENDA MONTERREY #${rcp.store_id}<br>TERMINAL #04 - CAJA ACTIVA</center>
                <hr>
                <div><b>FOLIO RECIBO:</b> ${rcp.receipt_id}</div>
                <div><b>FECHA/HORA:</b> ${rcp.timestamp}</div>
                <div><b>CAJERO EN TURNO:</b> ${rcp.cashier_id}</div>
                <hr>
                <div style="font-weight: bold; margin-bottom: 5px;">DESGLOSE DE ARTÍCULOS (${rcp.items.length}):</div>
                ${itemsHtml}
                <hr>
                <div class="receipt-item-row">
                    <span>SUBTOTAL REAL:</span>
                    <span>$${rcp.subtotal.toFixed(2)}</span>
                </div>
                <div class="receipt-item-row" style="color: ${isExploit ? '#dc2626' : '#555'}; font-weight: bold;">
                    <span>DESCUENTO APLICADO:</span>
                    <span>${rcp.discount_pct}% ${isExploit ? '🚨' : ''}</span>
                </div>
                <div class="receipt-item-row" style="font-size: 15px; font-weight: bold; margin-top: 5px; color: ${isExploit ? '#dc2626' : '#111'};">
                    <span>TOTAL A PAGAR:</span>
                    <span>$${rcp.total_amount.toFixed(2)}</span>
                </div>
                ${exploitNotice}
                <hr>
                <center style="font-size: 11px;">*** TRANSACCIÓN COBRADA EN CAJA ***<br>¡GRACIAS POR SU COMPRA!</center>
            `;
            document.getElementById('receipt-overlay').style.display = 'flex';
        }

        function closeReceipt() {
            document.getElementById('receipt-overlay').style.display = 'none';
            clearCart();
        }

        async function exploitSQLi() {
            const q = document.getElementById('sqli_in').value;
            const res = await fetch(`/api/v1/pos/products?q=${encodeURIComponent(q)}`);
            document.getElementById('out-sqli').innerText = JSON.stringify(await res.json(), null, 2);
        }
        async function exploitBOLA() {
            const s = document.getElementById('bola_store').value;
            const res = await fetch(`/api/v1/stores/${s}/sales`);
            document.getElementById('out-bola').innerText = JSON.stringify(await res.json(), null, 2);
        }

        loadSavedLogo();
        fetchProducts();
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def gui():
    return render_template_string(HTML_AS_IS)

@app.route("/api/v1/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json(force=True)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username, role, store_id FROM users WHERE username = ? AND password = ?", (data.get("username"), data.get("password")))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({"status": "ok", "user": {"username": row[0], "role": row[1], "store_id": row[2]}}), 200
    return jsonify({"detail": "Credenciales inválidas"}), 401

@app.route("/api/v1/pos/products", methods=["GET"])
def search_products():
    query_param = request.args.get("q", "")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    raw_query = f"SELECT id, name, price, category, emoji FROM products WHERE name LIKE '%{query_param}%'"
    try:
        cursor.execute(raw_query)
        rows = cursor.fetchall()
        data = [{"id": r[0], "name": r[1], "price": r[2], "category": r[3], "emoji": r[4]} for r in rows]
        return jsonify({"status": "success", "data": data}), 200
    except Exception as e:
        return jsonify({"error": str(e), "debug_query": raw_query}), 500
    finally:
        conn.close()

@app.route("/api/v1/stores/<store_id>/sales", methods=["GET"])
def get_store_sales(store_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, receipt_id, store_id, amount, discount_pct FROM transactions WHERE store_id = '{store_id}'")
    sales = [{"id": r[0], "receipt_id": r[1], "store_id": r[2], "amount": r[3], "discount": r[4]} for r in cursor.fetchall()]
    conn.close()
    return jsonify({"store": store_id, "sales": sales}), 200

@app.route("/api/v1/pos/inject-discount", methods=["POST"])
def inject_discount():
    data = request.get_json(force=True)
    store_id = data.get("store_id", "STORE-101")
    discount = float(data.get("discount_pct", 0.0))
    TERMINAL_STATE[store_id] = {
        "injected_discount_pct": discount,
        "is_poisoned": True
    }
    return jsonify({
        "status": "poisoned",
        "message": f"Terminal {store_id} envenenada con descuento de {discount}%.",
        "payload_received": data
    }), 200

@app.route("/api/v1/pos/transactions", methods=["POST"])
def create_transaction():
    data = request.get_json(force=True)
    items = data.get("items", [])
    
    if not items or len(items) == 0:
        return jsonify({"error": "No se pueden procesar cobros sin artículos en caja"}), 400

    receipt_id = f"REC-711-{int(time.time())}"
    store_id = data.get("store_id", "STORE-101")
    cashier_id = data.get("cashier_id", "Cajero1")
    is_approved = 1

    store_state = TERMINAL_STATE.get(store_id, {"injected_discount_pct": 0.0, "is_poisoned": False})
    discount_pct = store_state["injected_discount_pct"]

    subtotal = sum(float(it.get("price", 0.0)) for it in items)
    total_amount = subtotal * (1.0 - (discount_pct / 100.0)) if discount_pct > 0 else subtotal

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for it in items:
        charged_item_amount = it.get("price") * (1.0 - (discount_pct / 100.0)) if discount_pct > 0 else it.get("price")
        cursor.execute("""
            INSERT INTO transactions (receipt_id, store_id, cashier_id, product_id, amount, discount_pct, is_approved)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (receipt_id, store_id, cashier_id, it.get("sku"), charged_item_amount, discount_pct, is_approved))
    conn.commit()
    conn.close()

    TERMINAL_STATE[store_id] = {"injected_discount_pct": 0.0, "is_poisoned": False}

    receipt_data = {
        "receipt_id": receipt_id,
        "store_id": store_id,
        "cashier_id": cashier_id,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "items": items,
        "subtotal": round(subtotal, 2),
        "total_amount": round(max(0.0, total_amount), 2),
        "discount_pct": discount_pct
    }

    return jsonify({"status": "created", "receipt": receipt_data}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)