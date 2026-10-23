import os
import json
import uuid
import urllib.parse
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, Request, HTTPException, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests

from database import (
    init_db, get_connection, get_settings, update_setting
)

app = FastAPI(title="Tienda Online Dropshipping", version="1.0.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Inicializar Base de Datos al arrancar
@app.on_event("startup")
def startup_event():
    init_db()

# ==========================================
# MODELOS Pydantic
# ==========================================
class CartItem(BaseModel):
    product_id: int
    quantity: int

class CheckoutRequest(BaseModel):
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = ""
    shipping_address: Optional[str] = ""
    shipping_city: Optional[str] = ""
    shipping_province: Optional[str] = ""
    shipping_postal_code: Optional[str] = ""
    payment_method: str # 'mercadopago', 'transferencia', 'whatsapp'
    notes: Optional[str] = ""
    items: List[CartItem]

class ProductCreateUpdate(BaseModel):
    title: str
    description: Optional[str] = ""
    category: Optional[str] = "General"
    image_url: Optional[str] = ""
    cost_price: float = 0.0
    sale_price: float
    discount_price: Optional[float] = 0.0
    stock: int = 10
    supplier_sku: Optional[str] = ""
    supplier_url: Optional[str] = ""
    supplier_name: Optional[str] = "Dropsheable Mayorista"
    shipping_origin: Optional[str] = "CABA / GBA"
    dispatch_time: Optional[str] = "24-48 hs hábiles"
    featured: int = 0
    active: int = 1

# ==========================================
# RUTAS PÚBLICAS (TIENDA STOREFRONT)
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    settings = get_settings()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE active=1 ORDER BY featured DESC, id DESC")
    products = [dict(row) for row in c.fetchall()]
    
    # Categorías únicas
    c.execute("SELECT DISTINCT category FROM products WHERE active=1")
    categories = [row["category"] for row in c.fetchall() if row["category"]]
    conn.close()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "settings": settings,
        "products": products,
        "categories": categories
    })

@app.get("/api/products")
async def get_products(category: Optional[str] = None):
    conn = get_connection()
    c = conn.cursor()
    if category and category != "Todos":
        c.execute("SELECT id, title, description, category, image_url, sale_price, discount_price, stock, featured FROM products WHERE active=1 AND category=? ORDER BY id DESC", (category,))
    else:
        c.execute("SELECT id, title, description, category, image_url, sale_price, discount_price, stock, featured FROM products WHERE active=1 ORDER BY featured DESC, id DESC")
    products = [dict(row) for row in c.fetchall()]
    conn.close()
    return products

@app.post("/api/checkout")
async def create_checkout(data: CheckoutRequest):
    settings = get_settings()
    conn = get_connection()
    c = conn.cursor()
    
    # Validar productos y calcular totales
    items_detail = []
    subtotal = 0.0
    estimated_profit = 0.0
    
    origins = set()
    for item in data.items:
        c.execute("""
        SELECT id, title, sale_price, cost_price, image_url, supplier_sku,
               supplier_name, shipping_origin, dispatch_time
        FROM products WHERE id=? AND active=1
        """, (item.product_id,))
        prod = c.fetchone()
        if not prod:
            continue
        
        line_total = prod["sale_price"] * item.quantity
        line_cost = prod["cost_price"] * item.quantity
        line_profit = line_total - line_cost
        
        origin = prod["shipping_origin"] or "CABA / GBA"
        origins.add(origin)
        
        subtotal += line_total
        estimated_profit += line_profit
        
        items_detail.append({
            "product_id": prod["id"],
            "title": prod["title"],
            "unit_price": prod["sale_price"],
            "cost_price": prod["cost_price"],
            "quantity": item.quantity,
            "line_total": line_total,
            "supplier_sku": prod["supplier_sku"],
            "supplier_name": prod["supplier_name"] or "Dropsheable Mayorista",
            "shipping_origin": origin,
            "dispatch_time": prod["dispatch_time"] or "24-48 hs hábiles",
            "image_url": prod["image_url"]
        })
        
    if not items_detail:
        conn.close()
        raise HTTPException(status_code=400, detail="El carrito está vacío o los productos no existen.")
        
    flat_rate = float(settings.get("shipping_flat_rate", 0))
    free_min = float(settings.get("free_shipping_min", 0))
    package_count = max(1, len(origins))
    
    if flat_rate > 0:
        if free_min > 0 and subtotal >= (free_min * package_count):
            shipping_cost = 0.0
        else:
            shipping_cost = flat_rate * package_count
    else:
        shipping_cost = 0.0
        
    total = subtotal + shipping_cost
    
    order_code = f"PED-{uuid.uuid4().hex[:6].upper()}"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    c.execute("""
    INSERT INTO orders (
        order_code, customer_name, customer_email, customer_phone,
        shipping_address, shipping_city, shipping_province, shipping_postal_code,
        payment_method, payment_status, order_status, tracking_code,
        items_json, subtotal, shipping_cost, total, estimated_profit, notes, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        order_code, data.customer_name, data.customer_email, data.customer_phone,
        data.shipping_address, data.shipping_city, data.shipping_province, data.shipping_postal_code,
        data.payment_method, "pending", "nuevo", "",
        json.dumps(items_detail), subtotal, shipping_cost, total, estimated_profit, data.notes, now_str
    ))
    order_id = c.lastrowid
    conn.commit()
    conn.close()
    
    # Procesar según método de pago
    response_payload = {
        "order_code": order_code,
        "total": total,
        "payment_method": data.payment_method
    }
    
    # 1. MERCADO PAGO CHECKOUT
    if data.payment_method == "mercadopago":
        access_token = settings.get("mp_access_token")
        if access_token and access_token.strip():
            # Crear Preferencia real en Mercado Pago
            try:
                mp_items = [{
                    "title": it["title"],
                    "quantity": it["quantity"],
                    "unit_price": float(it["unit_price"]),
                    "currency_id": "ARS"
                } for it in items_detail]
                
                if shipping_cost > 0:
                    mp_items.append({
                        "title": "Costo de Envío",
                        "quantity": 1,
                        "unit_price": shipping_cost,
                        "currency_id": "ARS"
                    })
                    
                mp_body = {
                    "items": mp_items,
                    "payer": {
                        "name": data.customer_name,
                        "phone": {"number": data.customer_phone},
                        "email": data.customer_email or "cliente@tienda.com"
                    },
                    "external_reference": order_code,
                    "back_urls": {
                        "success": f"/?order_success={order_code}",
                        "failure": f"/?order_failed={order_code}",
                        "pending": f"/?order_pending={order_code}"
                    },
                    "auto_return": "approved"
                }
                
                mp_res = requests.post(
                    "https://api.mercadopago.com/checkout/preferences",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json=mp_body,
                    timeout=10
                )
                if mp_res.status_code == 201:
                    pref_data = mp_res.json()
                    response_payload["mp_init_point"] = pref_data.get("init_point")
            except Exception as e:
                response_payload["mp_error"] = str(e)
                
    # 2. WHATSAPP LINK
    elif data.payment_method == "whatsapp":
        wp_phone = settings.get("whatsapp_phone", "")
        clean_phone = "".join(filter(str.isdigit, wp_phone))
        lines = [f"👋 ¡Hola! Acabo de hacer el pedido *{order_code}* en la tienda:"]
        for it in items_detail:
            lines.append(f"• {it['quantity']}x {it['title']} (${it['line_total']:,.0f})")
        lines.append(f"\n*Total:* ${total:,.0f}")
        lines.append(f"*Cliente:* {data.customer_name}")
        lines.append(f"*Teléfono:* {data.customer_phone}")
        if data.shipping_address:
            lines.append(f"*Dirección:* {data.shipping_address}, {data.shipping_city} ({data.shipping_province})")
        lines.append("\n¿Cómo coordinamos el pago y envío?")
        
        msg_encoded = urllib.parse.quote("\n".join(lines))
        response_payload["whatsapp_url"] = f"https://wa.me/{clean_phone}?text={msg_encoded}"
        
    # 3. TRANSFERENCIA
    elif data.payment_method == "transferencia":
        response_payload["bank_info"] = {
            "bank_name": settings.get("bank_name"),
            "bank_holder": settings.get("bank_holder"),
            "bank_cbu": settings.get("bank_cbu"),
            "bank_alias": settings.get("bank_alias")
        }
        
    return response_payload

# ==========================================
# RUTAS DE ADMINISTRACIÓN (/admin)
# ==========================================
@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {
        "request": request
    })

@app.post("/api/admin/login")
async def admin_login(pin: str = Form(...)):
    settings = get_settings()
    configured_pin = settings.get("admin_pin", "1234")
    if pin == configured_pin:
        return {"success": True, "token": "admin-authenticated"}
    raise HTTPException(status_code=401, detail="PIN incorrecto")

@app.get("/api/admin/stats")
async def admin_stats():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM orders")
    total_orders = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM orders WHERE order_status='nuevo'")
    pending_orders = c.fetchone()[0]
    
    c.execute("SELECT COALESCE(SUM(total), 0) FROM orders WHERE payment_status='approved' OR order_status='pagado'")
    total_revenue = c.fetchone()[0]
    
    c.execute("SELECT COALESCE(SUM(estimated_profit), 0) FROM orders WHERE payment_status='approved' OR order_status='pagado'")
    total_profit = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM products WHERE stock <= 3 AND active=1")
    low_stock = c.fetchone()[0]
    
    conn.close()
    return {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "low_stock": low_stock
    }

@app.get("/api/admin/products")
async def admin_get_products():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM products ORDER BY id DESC")
    products = [dict(row) for row in c.fetchall()]
    conn.close()
    return products

@app.post("/api/admin/products")
async def admin_create_product(prod: ProductCreateUpdate):
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
    INSERT INTO products (
        title, description, category, image_url, cost_price, sale_price,
        discount_price, stock, supplier_sku, supplier_url, supplier_name,
        shipping_origin, dispatch_time, featured, active, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        prod.title, prod.description, prod.category, prod.image_url,
        prod.cost_price, prod.sale_price, prod.discount_price, prod.stock,
        prod.supplier_sku, prod.supplier_url, prod.supplier_name,
        prod.shipping_origin, prod.dispatch_time, prod.featured, prod.active, now_str
    ))
    conn.commit()
    prod_id = c.lastrowid
    conn.close()
    return {"success": True, "id": prod_id}

@app.put("/api/admin/products/{prod_id}")
async def admin_update_product(prod_id: int, prod: ProductCreateUpdate):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    UPDATE products SET
        title=?, description=?, category=?, image_url=?, cost_price=?, sale_price=?,
        discount_price=?, stock=?, supplier_sku=?, supplier_url=?, supplier_name=?,
        shipping_origin=?, dispatch_time=?, featured=?, active=?
    WHERE id=?
    """, (
        prod.title, prod.description, prod.category, prod.image_url,
        prod.cost_price, prod.sale_price, prod.discount_price, prod.stock,
        prod.supplier_sku, prod.supplier_url, prod.supplier_name,
        prod.shipping_origin, prod.dispatch_time, prod.featured, prod.active, prod_id
    ))
    conn.commit()
    conn.close()
    return {"success": True}

@app.delete("/api/admin/products/{prod_id}")
async def admin_delete_product(prod_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id=?", (prod_id,))
    conn.commit()
    conn.close()
    return {"success": True}

@app.get("/api/admin/orders")
async def admin_get_orders():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = []
    for row in c.fetchall():
        d = dict(row)
        try:
            d["items"] = json.loads(d["items_json"])
        except Exception:
            d["items"] = []
        orders.append(d)
    conn.close()
    return orders

@app.put("/api/admin/orders/{order_id}/status")
async def admin_update_order_status(order_id: int, payload: dict):
    new_status = payload.get("order_status")
    payment_status = payload.get("payment_status")
    tracking_code = payload.get("tracking_code")
    
    conn = get_connection()
    c = conn.cursor()
    
    updates = []
    params = []
    if new_status:
        updates.append("order_status=?")
        params.append(new_status)
    if payment_status:
        updates.append("payment_status=?")
        params.append(payment_status)
    if tracking_code is not None:
        updates.append("tracking_code=?")
        params.append(tracking_code)
        
    if updates:
        params.append(order_id)
        c.execute(f"UPDATE orders SET {', '.join(updates)} WHERE id=?", tuple(params))
        conn.commit()
        
    conn.close()
    return {"success": True}

@app.get("/api/admin/settings")
async def admin_get_settings():
    return get_settings()

@app.post("/api/admin/settings")
async def admin_save_settings(payload: dict):
    for k, v in payload.items():
        update_setting(k, str(v))
    return {"success": True}

from ai_service import (
    generate_social_content, generate_whatsapp_reply, ask_dropshipping_advisor
)

@app.post("/api/admin/generate-content")
async def admin_generate_content(payload: dict):
    product_id = payload.get("product_id")
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id=?", (product_id,))
    prod = c.fetchone()
    settings = get_settings()
    conn.close()
    
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    try:
        return generate_social_content(dict(prod), settings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/ai/whatsapp-reply")
async def admin_ai_whatsapp(payload: dict):
    message = payload.get("customer_message", "").strip()
    product_title = payload.get("product_title", "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="El mensaje del cliente no puede estar vacío.")
    
    settings = get_settings()
    try:
        return generate_whatsapp_reply(message, product_title, settings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/ai/advisor")
async def admin_ai_advisor(payload: dict):
    question = payload.get("question", "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="La consulta no puede estar vacía.")
        
    settings = get_settings()
    try:
        return ask_dropshipping_advisor(question, settings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/dropsheable/analyze")
async def admin_dropsheable_analyze(payload: dict):
    mode = payload.get("mode", "producto").strip()
    query = payload.get("query", "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="Ingresa el producto o proveedor que deseas analizar.")
        
    settings = get_settings()
    try:
        from ai_service import analyze_dropsheable_query
        return analyze_dropsheable_query(mode, query, settings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# GESTIÓN DE BOT WHATSAPP WEB (BAILEYS BRIDGE)
# ==========================================
@app.get("/api/admin/whatsapp/status")
async def admin_whatsapp_status():
    try:
        r = requests.get("http://127.0.0.1:3001/status", timeout=2.0)
        return r.json()
    except Exception:
        return {"connected": False, "has_qr": False, "phone": None, "detail": "Servicio de WhatsApp en espera"}

@app.get("/api/admin/whatsapp/qr")
async def admin_whatsapp_qr():
    try:
        r = requests.get("http://127.0.0.1:3001/qr", timeout=3.0)
        return r.json()
    except Exception:
        return {"connected": False, "qr": None, "detail": "Generando QR en el servidor..."}

@app.post("/api/admin/whatsapp/disconnect")
async def admin_whatsapp_disconnect():
    try:
        r = requests.post("http://127.0.0.1:3001/disconnect", timeout=3.0)
        return r.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


