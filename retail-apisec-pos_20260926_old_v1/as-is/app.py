from flask import Flask, request, jsonify, render_template_string
import sqlite3

app = Flask(__name__)
DB_NAME = "pos_legacy.db"

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
    cursor.execute("INSERT OR IGNORE INTO transactions VALUES (1, 'STORE-101', 'cajero_1', 'SKU-001', 25.50, 0, 1)")
    cursor.execute("INSERT OR IGNORE INTO transactions VALUES (2, 'STORE-102', 'cajero_2', 'SKU-002', 45.00, 0, 1)")
    conn.commit()
    conn.close()

init_db()

HTML_AS_IS = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>POS Terminal - As-Is Legacy</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #121218; color: #f0f0f0; padding: 25px; }
        .card { background: #1e1e2d; padding: 20px; border-radius: 6px; margin-bottom: 20px; border-left: 4px solid #e74c3c; }
        input, button { padding: 9px; border-radius: 4px; border: 1px solid #444; background: #2a2a3d; color: #fff; margin: 5px 0; }
        button { background: #e74c3c; font-weight: 600; cursor: pointer; border: none; }
        button:hover { background: #c0392b; }
        pre { background: #0a0a0f; padding: 12px; border-radius: 4px; color: #2ecc71; overflow-x: auto; }
        .alert { color: #e74c3c; font-weight: bold; }
    </style>
</head>
<body>
    <h2>POS Terminal #04 (As-Is Legacy) - <span class="alert">Vulnerable</span></h2>
    
    <div class="card">
        <h4>1. Búsqueda de Catálogo (OWASP API8 - Injection)</h4>
        <input type="text" id="sqli_in" value="Cafe' UNION SELECT id, store_id, amount FROM transactions--" style="width: 60%;">
        <button onclick="runSqli()">Ejecutar Query Directo</button>
        <pre id="sqli_out">// Respuesta de SQLite...</pre>
    </div>

    <div class="card">
        <h4>2. Extracción de Ventas por Sucursal (OWASP API1 - BOLA)</h4>
        <input type="text" id="bola_in" value="STORE-102">
        <button onclick="runBola()">Consultar Ventas</button>
        <pre id="bola_out">// Datos expuestos...</pre>
    </div>

    <div class="card">
        <h4>3. Registro de Transacción (OWASP API6 - Mass Assignment)</h4>
        <button onclick="runMass()">Inyectar discount_pct=100</button>
        <pre id="mass_out">// Respuesta backend...</pre>
    </div>

    <script>
        async function runSqli() {
            const q = document.getElementById('sqli_in').value;
            const res = await fetch(`/api/v1/pos/products?q=${encodeURIComponent(q)}`);
            document.getElementById('sqli_out').innerText = JSON.stringify(await res.json(), null, 2);
        }
        async function runBola() {
            const store = document.getElementById('bola_in').value;
            const res = await fetch(`/api/v1/stores/${store}/sales`);
            document.getElementById('bola_out').innerText = JSON.stringify(await res.json(), null, 2);
        }
        async function runMass() {
            const payload = {
                store_id: "STORE-101",
                cashier_id: "cajero_inseguro",
                product_id: "SKU-001",
                amount: 25.50,
                discount_pct: 100,
                is_approved: 1
            };
            const res = await fetch('/api/v1/pos/transactions', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            document.getElementById('mass_out').innerText = JSON.stringify(await res.json(), null, 2);
        }
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def gui():
    return render_template_string(HTML_AS_IS)

@app.route("/api/v1/pos/products", methods=["GET"])
def search_products():
    query_param = request.args.get("q", "")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    raw_query = f"SELECT id, name, price FROM products WHERE name LIKE '%{query_param}%'"
    try:
        cursor.execute(raw_query)
        rows = cursor.fetchall()
        data = [{"id": r[0], "name": r[1], "price": r[2]} for r in rows]
        return jsonify({"status": "success", "data": data}), 200
    except Exception as e:
        return jsonify({"error": str(e), "debug_query": raw_query}), 500
    finally:
        conn.close()

@app.route("/api/v1/stores/<store_id>/sales", methods=["GET"])
def get_store_sales(store_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, store_id, amount, discount_pct FROM transactions WHERE store_id = '{store_id}'")
    sales = [{"id": r[0], "store_id": r[1], "amount": r[2], "discount": r[3]} for r in cursor.fetchall()]
    conn.close()
    return jsonify({"store": store_id, "sales": sales}), 200

@app.route("/api/v1/pos/transactions", methods=["POST"])
def create_transaction():
    data = request.get_json(force=True)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (store_id, cashier_id, product_id, amount, discount_pct, is_approved)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data.get("store_id"),
        data.get("cashier_id"),
        data.get("product_id"),
        data.get("amount"),
        data.get("discount_pct", 0.0),
        data.get("is_approved", 0)
    ))
    conn.commit()
    conn.close()
    return jsonify({"status": "created", "transaction": data}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)