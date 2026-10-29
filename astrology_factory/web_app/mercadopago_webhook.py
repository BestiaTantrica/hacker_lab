"""
Webhook de Mercado Pago para Astrology Factory.

Garantías:
  1. Autenticidad: la firma `x-signature` (HMAC-SHA256) se valida en tiempo
     constante ANTES de tocar la base de datos o llamar a la API de MP.
  2. Fuente de verdad: el payload del webhook NUNCA se usa para acreditar.
     Se consulta GET /v1/payments/{id} con el access token del vendedor.
  3. Idempotencia: la transición `* -> approved` ocurre una única vez por
     `payment_id`, dentro de una transacción `BEGIN IMMEDIATE`. Reintentos de MP
     responden 200 sin reprocesar.
  4. Activación atómica: registro de compra + tokens + cola de render se
     confirman en la misma transacción (todo o nada). El email se despacha
     después del commit con BackgroundTasks.

Integración en main.py:

    from web_app.mercadopago_webhook import router as mp_router, init_mp_tables
    app.include_router(mp_router)
    # dentro de startup_event():  init_mp_tables(DB_PATH)

Variables de entorno:
    MERCADOPAGO_WEBHOOK_SECRET   (obligatoria)  clave secreta del panel de webhooks
    MERCADOPAGO_ACCESS_TOKEN     (obligatoria)  access token del vendedor
    PUBLIC_BASE_URL              (opcional)     default https://portaltarotmistico.com
    MP_SIGNATURE_TOLERANCE_SEC   (opcional)     0 = desactivado (default). Ver nota.
    MP_ENFORCE_AMOUNT            (opcional)     "1" (default) valida monto/moneda.

Nota sobre la tolerancia de timestamp: un replay de una notificación válida es
inofensivo porque (a) el estado se re-consulta a la API de MP y (b) la
idempotencia impide una doble acreditación. Por eso queda desactivada por
defecto: evita rechazar reintentos legítimos de MP.
"""

import hashlib
import hmac
import html
import json
import logging
import os
import re
import secrets
import sqlite3
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse

try:
    from email_dispatcher import send_email_with_audio
except ImportError:  # ejecución como paquete
    from web_app.email_dispatcher import send_email_with_audio

log = logging.getLogger("mercadopago_webhook")
router = APIRouter()

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(_BASE_DIR, "database", "users.sqlite")
MP_API_BASE = "https://api.mercadopago.com"

# --------------------------------------------------------------------------
# Catálogo oficial (ARS). `grants` = entitlements que se desbloquean.
# --------------------------------------------------------------------------
PRODUCTS = {
    "carta_natal": {"name": "Carta Natal Profunda + Oráculo", "price": 4990, "grants": ["carta_natal"]},
    "reloj_4k": {"name": "Reloj Astrológico 4K Live Wallpaper", "price": 2990, "grants": ["reloj_4k"]},
    "revolucion_solar": {"name": "Revolución Solar en Video", "price": 14990, "grants": ["revolucion_solar"]},
    "combo_triada": {
        "name": "Combo Tríada Sagrada (3 en 1)",
        "price": 16990,
        "grants": ["carta_natal", "reloj_4k", "revolucion_solar"],
    },
}
CURRENCY = "ARS"
VIDEO_QUEUE_STATUS = "queued_for_render_48h"
REVOKING_STATUSES = {"refunded", "charged_back", "cancelled"}


# --------------------------------------------------------------------------
# Configuración
# --------------------------------------------------------------------------
def _db_path() -> str:
    return os.environ.get("MP_DB_PATH", DEFAULT_DB_PATH)


def _public_base_url() -> str:
    return os.environ.get("PUBLIC_BASE_URL", "https://portaltarotmistico.com").rstrip("/")


# --------------------------------------------------------------------------
# Base de datos
# --------------------------------------------------------------------------
@contextmanager
def _connect(db_path: Optional[str] = None):
    # isolation_level=None => control transaccional manual (BEGIN IMMEDIATE).
    conn = sqlite3.connect(db_path or _db_path(), timeout=15.0, isolation_level=None)
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=15000")
        yield conn
    finally:
        conn.close()


def init_mp_tables(db_path: Optional[str] = None) -> None:
    """Crea las tablas necesarias. Idempotente; llamar en el startup de FastAPI."""
    os.makedirs(os.path.dirname(db_path or _db_path()), exist_ok=True)
    with _connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS processed_payments (
                payment_id   TEXT PRIMARY KEY,
                status       TEXT NOT NULL,
                payer_email  TEXT,
                product_id   TEXT,
                created_at   TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
                updated_at   TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
            );
            CREATE TABLE IF NOT EXISTS access_tokens (
                token       TEXT PRIMARY KEY,
                payment_id  TEXT NOT NULL REFERENCES processed_payments(payment_id),
                product_id  TEXT NOT NULL,
                email       TEXT NOT NULL,
                revoked     INTEGER NOT NULL DEFAULT 0,
                created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
            );
            CREATE INDEX IF NOT EXISTS idx_access_tokens_payment ON access_tokens(payment_id);
            CREATE TABLE IF NOT EXISTS pending_video_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT,
                video_type TEXT,
                status TEXT
            );
            CREATE UNIQUE INDEX IF NOT EXISTS uq_video_task_once
                ON pending_video_tasks(user_email, video_type, status)
                WHERE video_type = 'revolucion_solar';
            """
        )


# --------------------------------------------------------------------------
# Criptografía: validación de x-signature
# --------------------------------------------------------------------------
def parse_signature_header(x_signature: str) -> tuple[Optional[str], Optional[str]]:
    """Extrae (ts, v1) de 'ts=1704908010,v1=abcdef...'."""
    ts = v1 = None
    for part in (x_signature or "").split(","):
        key, sep, value = part.strip().partition("=")
        if not sep:
            continue
        if key == "ts":
            ts = value
        elif key == "v1":
            v1 = value
    return ts, v1


def build_manifest(data_id: Optional[str], request_id: Optional[str], ts: str) -> str:
    """Manifiesto firmado: id:[data.id];request-id:[x-request-id];ts:[ts];
    Los campos ausentes se omiten (según la especificación de MP)."""
    parts = []
    if data_id:
        # MP exige minúsculas cuando el id es alfanumérico.
        parts.append(f"id:{data_id.lower() if data_id.isalnum() else data_id};")
    if request_id:
        parts.append(f"request-id:{request_id};")
    parts.append(f"ts:{ts};")
    return "".join(parts)


def verify_signature(
    x_signature: Optional[str],
    x_request_id: Optional[str],
    data_id: Optional[str],
    secret: str,
    tolerance_sec: int = 0,
) -> bool:
    """True solo si la firma HMAC-SHA256 es válida. Comparación en tiempo constante."""
    if not x_signature or not secret:
        return False
    ts, v1 = parse_signature_header(x_signature)
    if not ts or not v1 or not re.fullmatch(r"[0-9a-fA-F]{64}", v1):
        return False
    if not ts.isdigit():
        return False
    if tolerance_sec > 0:
        ts_num = int(ts)
        # MP envía ts en ms en algunas integraciones y en s en otras.
        ts_sec = ts_num / 1000 if ts_num > 10**11 else ts_num
        if abs(time.time() - ts_sec) > tolerance_sec:
            return False
    manifest = build_manifest(data_id, x_request_id, ts)
    expected = hmac.new(secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, v1.lower())


# --------------------------------------------------------------------------
# API de Mercado Pago
# --------------------------------------------------------------------------
class PaymentNotFound(Exception):
    pass


def fetch_payment(payment_id: str) -> dict:
    """Consulta el pago a la API oficial. Lanza excepción en errores transitorios
    (para que el webhook responda 5xx y MP reintente)."""
    token = os.environ.get("MERCADOPAGO_ACCESS_TOKEN", "")
    if not token:
        raise RuntimeError("MERCADOPAGO_ACCESS_TOKEN no configurado")
    if not re.fullmatch(r"\d{1,20}", payment_id):
        raise PaymentNotFound(payment_id)
    req = urllib.request.Request(
        f"{MP_API_BASE}/v1/payments/{payment_id}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise PaymentNotFound(payment_id) from e
        raise


# --------------------------------------------------------------------------
# Lógica de negocio (transaccional e idempotente)
# --------------------------------------------------------------------------
def resolve_product(payment: dict) -> Optional[str]:
    """product_id se transporta en external_reference (o metadata.product_id)."""
    candidates = [
        str(payment.get("external_reference") or "").strip(),
        str((payment.get("metadata") or {}).get("product_id") or "").strip(),
    ]
    for c in candidates:
        if c in PRODUCTS:
            return c
    return None


def _amount_ok(payment: dict, product_id: str) -> bool:
    if os.environ.get("MP_ENFORCE_AMOUNT", "1") != "1":
        return True
    if (payment.get("currency_id") or CURRENCY) != CURRENCY:
        return False
    try:
        paid = float(payment.get("transaction_amount") or 0)
    except (TypeError, ValueError):
        return False
    return paid + 0.005 >= PRODUCTS[product_id]["price"]


def process_payment(payment: dict, db_path: Optional[str] = None) -> dict:
    """Aplica el pago de forma atómica e idempotente.

    Retorna {"action": ..., "email": ..., "product_id": ..., "deliveries": [...]}.
    action ∈ duplicate | activated | recorded | revoked | rejected
    """
    payment_id = str(payment["id"])
    status = str(payment.get("status") or "unknown")
    email = ((payment.get("payer") or {}).get("email") or "").strip().lower()
    product_id = resolve_product(payment)

    with _connect(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")  # serializa webhooks concurrentes del mismo pago
        try:
            row = conn.execute(
                "SELECT status FROM processed_payments WHERE payment_id=?", (payment_id,)
            ).fetchone()
            previous = row[0] if row else None

            if previous is None:
                conn.execute(
                    "INSERT INTO processed_payments (payment_id, status, payer_email, product_id) "
                    "VALUES (?,?,?,?)",
                    (payment_id, status, email, product_id),
                )
            elif previous == status:
                conn.execute("COMMIT")
                return {"action": "duplicate"}
            else:
                if previous == "approved" and status not in REVOKING_STATUSES:
                    # No degradamos un pago ya acreditado por notificaciones fuera de orden.
                    conn.execute("COMMIT")
                    return {"action": "duplicate"}
                conn.execute(
                    "UPDATE processed_payments SET status=?, updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') "
                    "WHERE payment_id=?",
                    (status, payment_id),
                )

            if status in REVOKING_STATUSES:
                conn.execute("UPDATE access_tokens SET revoked=1 WHERE payment_id=?", (payment_id,))
                conn.execute("COMMIT")
                return {"action": "revoked", "email": email, "product_id": product_id}

            if status != "approved":
                conn.execute("COMMIT")
                return {"action": "recorded", "email": email, "product_id": product_id}

            # ---- status == approved (primera y única vez) ----
            if not product_id or not email or not _amount_ok(payment, product_id):
                conn.execute(
                    "UPDATE processed_payments SET status='approved_needs_review' WHERE payment_id=?",
                    (payment_id,),
                )
                conn.execute("COMMIT")
                log.error(
                    "Pago %s aprobado pero inválido (producto=%r email=%r monto=%r %r): REVISIÓN MANUAL",
                    payment_id, product_id, email,
                    payment.get("transaction_amount"), payment.get("currency_id"),
                )
                return {"action": "rejected"}

            deliveries = []
            for grant in PRODUCTS[product_id]["grants"]:
                if grant == "revolucion_solar":
                    conn.execute(
                        "INSERT OR IGNORE INTO pending_video_tasks (user_email, video_type, status) "
                        "VALUES (?,?,?)",
                        (email, "revolucion_solar", VIDEO_QUEUE_STATUS),
                    )
                    deliveries.append({"product": grant, "token": None})
                else:
                    token = secrets.token_urlsafe(32)
                    conn.execute(
                        "INSERT INTO access_tokens (token, payment_id, product_id, email) VALUES (?,?,?,?)",
                        (token, payment_id, grant, email),
                    )
                    deliveries.append({"product": grant, "token": token})

            conn.execute("COMMIT")
            return {"action": "activated", "email": email, "product_id": product_id, "deliveries": deliveries}
        except BaseException:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise


def verify_access_token(token: str, db_path: Optional[str] = None) -> Optional[dict]:
    """Devuelve {'product_id','email'} si el token es válido y no fue revocado."""
    if not token or len(token) > 128:
        return None
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT product_id, email FROM access_tokens WHERE token=? AND revoked=0", (token,)
        ).fetchone()
    return {"product_id": row[0], "email": row[1]} if row else None


# --------------------------------------------------------------------------
# Email de confirmación (se ejecuta fuera de la transacción)
# --------------------------------------------------------------------------
def send_confirmation_email(result: dict) -> None:
    base = _public_base_url()
    items = []
    for d in result["deliveries"]:
        name = html.escape(PRODUCTS[d["product"]]["name"])
        if d["token"]:
            url = f"{base}/acceso/{d['token']}"
            items.append(f'<li><b>{name}</b>: <a href="{url}">Desbloquear acceso</a></li>')
        else:
            items.append(
                f"<li><b>{name}</b>: tu video está en cola de renderizado; "
                "lo recibirás en un plazo máximo de 48 horas.</li>"
            )
    body = (
        "<h1>🔮 Pago confirmado</h1>"
        "<p>Gracias por tu compra. Estos son tus accesos personales (no los compartas):</p>"
        f"<ul>{''.join(items)}</ul>"
    )
    try:
        ok = send_email_with_audio(result["email"], "Tu acceso está activo — Portal Tarot Místico", body)
        if not ok:
            log.error("Email de confirmación NO enviado a %s (revisar y reenviar)", result["email"])
    except Exception:
        log.exception("Fallo despachando email de confirmación a %s", result["email"])


# --------------------------------------------------------------------------
# Endpoint
# --------------------------------------------------------------------------
@router.post("/api/mercadopago/webhook")
async def mercadopago_webhook(request: Request, background_tasks: BackgroundTasks):
    secret = os.environ.get("MERCADOPAGO_WEBHOOK_SECRET", "")
    if not secret:
        log.critical("MERCADOPAGO_WEBHOOK_SECRET no configurado: webhook deshabilitado")
        return JSONResponse(status_code=503, content={"status": "misconfigured"})

    try:
        body = await request.json()
        if not isinstance(body, dict):
            body = {}
    except Exception:
        body = {}

    q = request.query_params
    data_id = q.get("data.id") or str((body.get("data") or {}).get("id") or "") or None

    # 1) Autenticidad — antes de cualquier otro trabajo.
    tolerance = int(os.environ.get("MP_SIGNATURE_TOLERANCE_SEC", "0") or 0)
    if not verify_signature(
        request.headers.get("x-signature"),
        request.headers.get("x-request-id"),
        data_id,
        secret,
        tolerance,
    ):
        log.warning("Firma inválida en webhook MP (ip=%s)", request.client.host if request.client else "?")
        return JSONResponse(status_code=401, content={"status": "invalid_signature"})

    # 2) Solo nos interesan los eventos de pago.
    topic = q.get("type") or q.get("topic") or body.get("type") or body.get("topic")
    if topic != "payment" or not data_id:
        return JSONResponse(status_code=200, content={"status": "ignored"})

    # 3) Estado real desde la API de MP (nunca confiar en el payload).
    try:
        payment = await run_in_threadpool(fetch_payment, data_id)
    except PaymentNotFound:
        # Típico de las notificaciones de prueba del simulador (id 123456).
        return JSONResponse(status_code=200, content={"status": "payment_not_found"})
    except Exception:
        log.exception("Error consultando pago %s en MP", data_id)
        return JSONResponse(status_code=502, content={"status": "upstream_error"})  # MP reintentará

    # 4) Procesamiento atómico e idempotente.
    try:
        result = await run_in_threadpool(process_payment, payment)
    except Exception:
        log.exception("Error procesando pago %s", data_id)
        return JSONResponse(status_code=500, content={"status": "processing_error"})  # MP reintentará

    if result["action"] == "activated":
        background_tasks.add_task(send_confirmation_email, result)

    return JSONResponse(status_code=200, content={"status": result["action"]})
