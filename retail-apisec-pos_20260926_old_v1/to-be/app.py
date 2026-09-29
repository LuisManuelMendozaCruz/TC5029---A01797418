from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
import sqlite3
from typing import List, Dict, Any

from schemas.transaction_dto import ProductSearchDTO, TransactionCreateDTO, TransactionResponseDTO
from middleware.correlation_middleware import CorrelationMiddleware
from middleware.auth_middleware import check_scope

app = FastAPI(
    title="APISec Retail - POS Protected API (To-Be)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(CorrelationMiddleware)
DB_NAME = "pos_secure.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            price REAL
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO products VALUES ('SKU-001', 'Cafe 12oz', 25.50)")
    cursor.execute("INSERT OR IGNORE INTO products VALUES ('SKU-002', 'Sandwich Jamon', 45.00)")
    cursor.execute("INSERT OR IGNORE INTO transactions VALUES (1, 'STORE-711-MEX', 'pos_user_01', 'SKU-001', 25.50, 0.0, 1)")
    cursor.execute("INSERT OR IGNORE INTO transactions VALUES (2, 'STORE-711-GDA', 'pos_user_02', 'SKU-002', 45.00, 0.0, 1)")
    conn.commit()
    conn.close()

init_db()

HTML_TO_BE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>POS Terminal - To-Be Secure</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #c9d1d9; padding: 25px; }
        .card { background: #161b22; padding: 20px; border-radius: 6px; margin-bottom: 20px; border-left: 4px solid #238636; border: 1px solid #30363d; }
        input, button { padding: 9px; border-radius: 4px; border: 1px solid #30363d; background: #0d1117; color: #c9d1d9; margin: 5px 0; }
        button { background: #238636; font-weight: 600; cursor: pointer; border: none; }
        button:hover { background: #2ea043; }
        pre { background: #010409; padding: 12px; border-radius: 4px; color: #58a6ff; overflow-x: auto; border: 1px solid #21262d; }
        .secure { color: #3fb950; font-weight: bold; }
        .badge { background: #1f6feb; color: white; padding: 2px 7px; border-radius: 10px; font-size: 11px; }
    </style>
</head>
<body>
    <h2>POS Terminal Console (To-Be) - <span class="secure">Zero Trust</span></h2>
    <p>Identidad Token: <span class="badge">pos_user_01 (STORE-711-MEX)</span></p>

    <div class="card">
        <h4>1. Búsqueda Validada (Prevención SQLi)</h4>
        <input type="text" id="query_in" value="Cafe' UNION SELECT--" style="width: 60%;">
        <button onclick="runSafeQuery()">Consultar Catálogo</button>
        <pre id="query_out">// Validación Pydantic...</pre>
    </div>

    <div class="card">
        <h4>2. Aislamiento Multi-Tenant (Prevención BOLA)</h4>
        <input type="text" id="store_target" value="STORE-711-GDA">
        <button onclick="runSafeBola()">Consultar Otra Sucursal</button>
        <pre id="bola_out">// Verificación de Claims...</pre>
    </div>

    <div class="card">
        <h4>3. Whitelisting de Atributos (Prevención Mass Assignment)</h4>
        <button onclick="runSafeMass()">Enviar discount_pct=100</button>
        <pre id="mass_out">// Validación DTO...</pre>
    </div>

    <script>
        let JWT_TOKEN = "";

        async function initToken() {
            if (!JWT_TOKEN) {
                const res = await fetch('/api/v1/auth/token-demo');
                const data = await res.json();
                JWT_TOKEN = data.token;
            }
        }

        async function runSafeQuery() {
            await initToken();
            const q = document.getElementById('query_in').value;
            const res = await fetch(`/api/v1/pos/products?query=${encodeURIComponent(q)}`, {
                headers: { 'Authorization': `Bearer ${JWT_TOKEN}` }
            });
            document.getElementById('query_out').innerText = `HTTP ${res.status}\\n` + JSON.stringify(await res.json(), null, 2);
        }

        async function runSafeBola() {
            await initToken();
            const store = document.getElementById('store_target').value;
            const res = await fetch(`/api/v1/stores/${store}/sales`, {
                headers: { 'Authorization': `Bearer ${JWT_TOKEN}` }
            });
            document.getElementById('bola_out').innerText = `HTTP ${res.status}\\n` + JSON.stringify(await res.json(), null, 2);
        }

        async function runSafeMass() {
            await initToken();
            const payload = {
                product_id: "SKU-001",
                amount: 25.50,
                discount_pct: 100
            };
            const res = await fetch('/api/v1/pos/transactions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${JWT_TOKEN}`
                },
                body: JSON.stringify(payload)
            });
            document.getElementById('mass_out').innerText = `HTTP ${res.status}\\n` + JSON.stringify(await res.json(), null, 2);
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_TO_BE

@app.get("/api/v1/auth/token-demo")
def generate_demo_token():
    import jwt, time
    token = jwt.encode({
        "sub": "pos_user_01",
        "store_id": "STORE-711-MEX",
        "scope": "sales:write inventory:read",
        "exp": int(time.time()) + 86400
    }, "SUPER_SECRET_APITOKEN_KEY_FOR_LOCAL_POC", algorithm="HS256")
    return {"token": token}

@app.get("/api/v1/pos/products", response_model=List[Dict[str, Any]])
def search_products(
    params: ProductSearchDTO = Depends(),
    claims: Dict[str, Any] = Depends(check_scope("inventory:read"))
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price FROM products WHERE name LIKE ?", (f"%{params.query}%",))
    data = [{"id": r[0], "name": r[1], "price": r[2]} for r in cursor.fetchall()]
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
    cursor.execute("SELECT id, store_id, amount, discount_pct FROM transactions WHERE store_id = ?", (store_id,))
    sales = [{"id": r[0], "store_id": r[1], "amount": r[2], "discount": r[3]} for r in cursor.fetchall()]
    conn.close()
    return {"store_id": store_id, "sales": sales}

@app.post("/api/v1/pos/transactions", response_model=TransactionResponseDTO, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreateDTO,
    claims: Dict[str, Any] = Depends(check_scope("sales:write"))
):
    store_id = claims.get("store_id")
    cashier_id = claims.get("sub")
    fixed_discount = 0.0
    is_approved = 1

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (store_id, cashier_id, product_id, amount, discount_pct, is_approved)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (store_id, cashier_id, payload.product_id, payload.amount, fixed_discount, is_approved))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return TransactionResponseDTO(
        transaction_id=new_id,
        store_id=store_id,
        cashier_id=cashier_id,
        product_id=payload.product_id,
        amount=payload.amount,
        discount_pct=fixed_discount,
        status="APPROVED"
    )