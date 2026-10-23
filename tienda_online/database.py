import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "tienda.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Tabla de Productos
    c.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT DEFAULT 'General',
        image_url TEXT,
        cost_price REAL DEFAULT 0.0,
        sale_price REAL NOT NULL,
        discount_price REAL DEFAULT 0.0,
        stock INTEGER DEFAULT 10,
        supplier_sku TEXT,
        supplier_url TEXT,
        supplier_name TEXT DEFAULT 'Dropsheable Mayorista',
        shipping_origin TEXT DEFAULT 'CABA / GBA',
        dispatch_time TEXT DEFAULT '24-48 hs hábiles',
        featured INTEGER DEFAULT 0,
        active INTEGER DEFAULT 1,
        created_at TEXT
    )
    """)
    
    # Migraciones seguras para productos
    for col, col_def in [
        ("supplier_name", "TEXT DEFAULT 'Dropsheable Mayorista'"),
        ("shipping_origin", "TEXT DEFAULT 'CABA / GBA'"),
        ("dispatch_time", "TEXT DEFAULT '24-48 hs hábiles'")
    ]:
        try:
            c.execute(f"ALTER TABLE products ADD COLUMN {col} {col_def}")
        except Exception:
            pass
    
    # Tabla de Pedidos
    c.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_code TEXT UNIQUE NOT NULL,
        customer_name TEXT NOT NULL,
        customer_email TEXT,
        customer_phone TEXT NOT NULL,
        shipping_address TEXT,
        shipping_city TEXT,
        shipping_province TEXT,
        shipping_postal_code TEXT,
        payment_method TEXT DEFAULT 'mercadopago',
        payment_status TEXT DEFAULT 'pending',
        order_status TEXT DEFAULT 'nuevo',
        tracking_code TEXT,
        items_json TEXT NOT NULL,
        subtotal REAL NOT NULL,
        shipping_cost REAL DEFAULT 0.0,
        total REAL NOT NULL,
        estimated_profit REAL DEFAULT 0.0,
        notes TEXT,
        created_at TEXT
    )
    """)
    
    # Tabla de Configuraciones del Comercio
    c.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)
    
    # Valores por defecto de configuración si no existen
    defaults = {
        "store_name": "EcoMarvex",
        "store_description": "Tu tienda online de confianza. Envíos directos a todo el país.",
        "admin_pin": "1234",
        "whatsapp_phone": "5491100000000",
        "mp_public_key": "",
        "mp_access_token": "",
        "bank_cbu": "",
        "bank_alias": "",
        "bank_holder": "",
        "bank_name": "Mercado Pago / Banco",
        "shipping_flat_rate": "0",
        "free_shipping_min": "0",
        "shipping_policy_text": "Envío a convenir / a cargo del comprador (Andreani o Correo Argentino a domicilio o sucursal)",
        "currency_symbol": "$",
        "gemini_api_key": os.getenv("GEMINI_API_KEY", ""),
        "gemini_api_key_backup": "",
        "dropsheable_api_token": "",
        "dropsheable_api_key": "",
        "dropsheable_api_secret": "",
        "whatsapp_auto_reply": "1"
    }
    
    for k, v in defaults.items():
        c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))
        
    # Si no hay productos, inyectar un par de productos de demostración
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        demo_products = [
            (
                "Auriculares Inalámbricos Bluetooth Pro",
                "Sonido Hi-Fi con cancelación pasiva de ruido, batería de 24 horas y estuche de carga rápida. Compatible con Android y iPhone.",
                "Tecnología",
                "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=80",
                12500.0, 24999.0, 29999.0, 15, "DROP-AUR-01", "https://dropsheable.com.ar", 1, 1, datetime.now().isoformat()
            ),
            (
                "Smartwatch Deportivo Ultra Fit",
                "Medición de ritmo cardíaco, oxígeno en sangre, podómetro, notificaciones de WhatsApp y llamadas. Resistente a salpicaduras IP68.",
                "Tecnología",
                "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=600&auto=format&fit=crop&q=80",
                18000.0, 36500.0, 42000.0, 10, "DROP-SMART-02", "https://dropsheable.com.ar", 1, 1, datetime.now().isoformat()
            ),
            (
                "Botella Térmica Acero Inoxidable 750ml",
                "Mantiene 24hs frío y 12hs calor. Doble capa de vacío de acero inoxidable 304 libre de BPA. Pico deportivo a prueba de fugas.",
                "Hogar",
                "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600&auto=format&fit=crop&q=80",
                8200.0, 18900.0, 0.0, 25, "DROP-BOT-03", "https://dropsheable.com.ar", 1, 1, datetime.now().isoformat()
            )
        ]
        c.executemany("""
        INSERT INTO products (title, description, category, image_url, cost_price, sale_price, discount_price, stock, supplier_sku, supplier_url, featured, active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, demo_products)
        
    conn.commit()
    conn.close()

def get_settings():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT key, value FROM settings")
    rows = c.fetchall()
    conn.close()
    return {r["key"]: r["value"] for r in rows}

def update_setting(key, value):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Base de datos inicializada correctamente.")
