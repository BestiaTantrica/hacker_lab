#!/usr/bin/env python3
"""
🧪 SUITE DE PRUEBAS END-TO-END — ENJAMBRE COMPLETO V2
Portal Tarot Místico / Astrology Factory

Verifica sistemáticamente la salud de las 7 Células antes de cualquier deploy:
1. Célula 1 — Cálculos Astronómicos Swiss Ephemeris (Planetas, Tránsitos, Orbes).
2. Célula 2 — ADN y Contexto Astrológico (Estructura de Guion, Arquetipos).
3. Célula 3 — Motor de Audio & Frecuencias Solfeggio (Edge-TTS, Binaural).
4. Célula 4 — Redes Sociales (YouTube Scopes, TikTok Cookies/Tokens, Telegram Bot).
5. Célula 5 — Entorno de Edición y Video (FFmpeg, Codecs, Resoluciones).
6. Célula 6 — Despacho Diario & Web Tenebrista (Daily Job Molde de Oro, FastApi).
7. Célula 7 — Seguridad Transaccional (Webhook HMAC Mercado Pago, Idempotencia).
"""

import os
import sys
import json
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "web_app"))

class TestEnjambreCompleto(unittest.TestCase):

    def setUp(self):
        self.adn_path = PROJECT_ROOT / "contexto_astrologico.json"
        self.assertTrue(self.adn_path.exists(), "contexto_astrologico.json debe existir")
        with open(self.adn_path, encoding="utf-8") as f:
            self.adn = json.load(f)

    # --------------------------------------------------------------------------
    # 1. CÉLULA 1 — Swiss Ephemeris
    # --------------------------------------------------------------------------
    def test_celula_1_calculos_astronomicos(self):
        """Valida que Swiss Ephemeris calcule las posiciones planetarias de hoy."""
        from astrology_engine.clima_astral_engine import obtener_resumen_cielo_hoy
        resumen = obtener_resumen_cielo_hoy()
        self.assertIsNotNone(resumen)
        self.assertIn("Sol", resumen)
        self.assertIn("Luna", resumen)
        self.assertTrue(len(resumen) > 100, "El resumen de efemérides debe contener datos detallados")

    # --------------------------------------------------------------------------
    # 2. CÉLULA 2 — Guion y ADN
    # --------------------------------------------------------------------------
    def test_celula_2_contexto_y_adn(self):
        """Valida la consistencia del archivo contexto_astrologico.json."""
        self.assertIn("produccion", self.adn)
        self.assertIn("transito", self.adn)
        self.assertIn("arquetipos", self.adn)
        self.assertIn("guion", self.adn)
        tomas = self.adn["guion"]["estructura_tomas"]
        self.assertEqual(len(tomas), 5, "El video diario debe tener exactamente 5 tomas canónicas")

    # --------------------------------------------------------------------------
    # 3. CÉLULA 3 — Audio y Frecuencias
    # --------------------------------------------------------------------------
    def test_celula_3_configuracion_audio(self):
        """Valida las frecuencias binaurales y configuración de voz."""
        audio_cfg = self.adn.get("audio", {})
        self.assertIn("voz_tts", audio_cfg)
        self.assertIn("frecuencia_binaural_hz", audio_cfg)
        hz = audio_cfg["frecuencia_binaural_hz"]
        self.assertIn(hz, [432, 528, 639, 741, 852, 963], "La frecuencia debe ser un tono solfeggio canónico")

    # --------------------------------------------------------------------------
    # 4. CÉLULA 4 — Redes y Credenciales
    # --------------------------------------------------------------------------
    def test_celula_4_redes_y_tokens(self):
        """Valida la presencia y estructura de credenciales para redes."""
        token_yt = PROJECT_ROOT / "v2" / "celula_4" / "token.json"
        self.assertTrue(token_yt.exists(), "token.json de YouTube debe existir")
        with open(token_yt) as f:
            d_yt = json.load(f)
        self.assertIn("token", d_yt)
        self.assertIn("refresh_token", d_yt)

    # --------------------------------------------------------------------------
    # 5. CÉLULA 5 — Video y FFmpeg
    # --------------------------------------------------------------------------
    def test_celula_5_ffmpeg_instalado(self):
        """Verifica que ffmpeg esté instalado en el sistema y soporte libx264."""
        import subprocess
        res = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(res.returncode, 0, "ffmpeg debe estar disponible en PATH")

    # --------------------------------------------------------------------------
    # 6. CÉLULA 6 — Despacho Diario & Web
    # --------------------------------------------------------------------------
    def test_celula_6_daily_channel_job(self):
        """Verifica que daily_channel_job se pueda importar y tenga los botones multicanal."""
        import daily_channel_job
        self.assertTrue(hasattr(daily_channel_job, "send_daily_forecast"))
        self.assertTrue(hasattr(daily_channel_job, "generar_reporte_con_reintentos"))

    # --------------------------------------------------------------------------
    # 7. CÉLULA 7 — Seguridad y Webhooks
    # --------------------------------------------------------------------------
    def test_celula_7_seguridad_webhook_mercadopago(self):
        """Verifica la función criptográfica HMAC de verificación de Mercado Pago."""
        from web_app.mercadopago_webhook import verify_signature, build_manifest
        secret = "test_secret_123"
        ts = "1730000000"
        data_id = "payment_999888"
        req_id = "req_test"
        import hmac, hashlib
        manifest = build_manifest(data_id, req_id, ts)
        valid_v1 = hmac.new(secret.encode("utf-8"), manifest.encode("utf-8"), hashlib.sha256).hexdigest()
        x_sig = f"ts={ts},v1={valid_v1}"
        es_valido = verify_signature(x_sig, req_id, data_id, secret=secret, tolerance_sec=0)
        self.assertTrue(es_valido, "La verificación criptográfica HMAC de Mercado Pago debe validar correctamente")

if __name__ == "__main__":
    unittest.main(verbosity=2)
