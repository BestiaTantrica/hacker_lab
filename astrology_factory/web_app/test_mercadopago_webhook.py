"""Tests del webhook de MP: firma, idempotencia, combo, reembolso. Ejecutar: python -m pytest web_app/test_mercadopago_webhook.py"""
import hashlib
import hmac
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mercadopago_webhook as mp  # noqa: E402

SECRET = "s3cr3t"


def sign(data_id, req_id, ts="1704908010"):
    manifest = mp.build_manifest(data_id, req_id, ts)
    return f"ts={ts},v1=" + hmac.new(SECRET.encode(), manifest.encode(), hashlib.sha256).hexdigest()


def test_signature_valid_and_tampered():
    sig = sign("12345", "req-1")
    assert mp.verify_signature(sig, "req-1", "12345", SECRET)
    assert not mp.verify_signature(sig, "req-1", "99999", SECRET)      # id alterado
    assert not mp.verify_signature(sig, "req-2", "12345", SECRET)      # request-id alterado
    assert not mp.verify_signature(sig, "req-1", "12345", "otra")      # secreto distinto
    assert not mp.verify_signature(None, "req-1", "12345", SECRET)
    assert not mp.verify_signature("ts=1,v1=zz", "req-1", "12345", SECRET)


def test_signature_tolerance():
    sig = sign("1", "r", ts="1000")
    assert not mp.verify_signature(sig, "r", "1", SECRET, tolerance_sec=60)


def _payment(pid, status="approved", product="carta_natal", amount=4990, email="A@x.com"):
    return {"id": pid, "status": status, "external_reference": product,
            "transaction_amount": amount, "currency_id": "ARS", "payer": {"email": email}}


def _db():
    path = os.path.join(tempfile.mkdtemp(), "t.sqlite")
    mp.init_mp_tables(path)
    return path


def test_idempotency_and_activation():
    db = _db()
    r1 = mp.process_payment(_payment(1), db)
    assert r1["action"] == "activated" and r1["deliveries"][0]["token"]
    assert mp.process_payment(_payment(1), db)["action"] == "duplicate"
    assert mp.verify_access_token(r1["deliveries"][0]["token"], db)["email"] == "a@x.com"


def test_combo_and_video_queue_once():
    db = _db()
    r = mp.process_payment(_payment(2, product="combo_triada", amount=16990), db)
    assert len(r["deliveries"]) == 3
    mp.process_payment(_payment(2, product="combo_triada", amount=16990), db)
    with mp._connect(db) as c:
        assert c.execute("SELECT COUNT(*) FROM pending_video_tasks WHERE status=?",
                         (mp.VIDEO_QUEUE_STATUS,)).fetchone()[0] == 1
        assert c.execute("SELECT COUNT(*) FROM access_tokens").fetchone()[0] == 2


def test_amount_mismatch_rejected():
    db = _db()
    assert mp.process_payment(_payment(3, amount=1), db)["action"] == "rejected"
    with mp._connect(db) as c:
        assert c.execute("SELECT COUNT(*) FROM access_tokens").fetchone()[0] == 0


def test_pending_then_approved_and_refund():
    db = _db()
    assert mp.process_payment(_payment(4, status="pending"), db)["action"] == "recorded"
    r = mp.process_payment(_payment(4), db)
    assert r["action"] == "activated"
    tok = r["deliveries"][0]["token"]
    assert mp.process_payment(_payment(4, status="pending"), db)["action"] == "duplicate"  # fuera de orden
    assert mp.process_payment(_payment(4, status="refunded"), db)["action"] == "revoked"
    assert mp.verify_access_token(tok, db) is None
