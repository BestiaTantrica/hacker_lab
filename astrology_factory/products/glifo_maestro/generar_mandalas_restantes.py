#!/usr/bin/env python3
"""
generar_mandalas_restantes.py
Genera los 3 Mandalas canónicos restantes para cerrar al 100% la biblioteca El Glifo Maestro.
Utiliza el pool de tokens Hugging Face con FLUX.1-dev.
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv("/home/LAB/astrology_factory/.env")

VAULT_MANDALAS = Path("/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/Imagenes/Glifo_Maestro/03_Geometria_y_Sigilos/02_Mandalas_y_Rueda_Zodiacal")
VAULT_MANDALAS.mkdir(parents=True, exist_ok=True)

MANDALAS = {
    "mandala_03_septenario_caldeo_alquimico": {
        "width": 1024,
        "height": 1024,
        "seed": 7771,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, 1:1 square composition. "
            "Sacred monumental mandala study of the Chaldean Order of the Seven Classical Planetary Spheres, strictly no human figures. "
            "A massive dark black basalt stone disk carved with seven concentric geometric orbital rings. "
            "Inlaid along each ring in sunken relief are seven glowing astronomical emblems: Saturn in aged lead, Jupiter in antique gold leaf, "
            "Mars in oxidized iron, the Sun in blinding solar electrum, Venus in polished verdigris copper, Mercury in liquid quicksilver inlay, "
            "and the Moon in reflective silver leaf. Delicate radial engraved rays and geometric degree ticks connect the seven rings to a dark hollow center with an alchemical septagram. "
            "LIGHTING: Raking golden and silver chiaroscuro light grazing the stone relief against 90% flat pitch-black bitumen darkness (#000000). "
            "Heavy oil impasto, cracked varnish on rough linen canvas, authentic museum masterpiece, 8k"
        )
    },
    "mandala_04_carta_natal_con_aspectos_y_casas": {
        "width": 768,
        "height": 1376,
        "seed": 7772,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred cosmological mandala study of the Complete Natal Chart Matrix, strictly no human figures. "
            "An ancient monumental astrometric disk of dark green porphyry and black slate. "
            "The twelve astrological house divisions radiate outward with chiseled Roman numerals in aged gold leaf. "
            "The four cardinal angles (Ascendant, Descendant, Midheaven, Imum Coeli) are forged of heavy raised bronze bars with fine astronomical verniers. "
            "Crossing through the center of the wheel is an intricate geometric web of glowing aspect lines: harmonious trines and sextiles in incandescent gold filigree, "
            "and tense squares and oppositions in glowing vermilion thread. "
            "LIGHTING: Piercing diagonal ray of warm chiaroscuro sunlight striking the central geometry surrounded by 88% pitch-black bitumen darkness (#000000). "
            "Heavy oil impasto, tactile brushstrokes on linen, authentic Roberto Ferri, 8k"
        )
    },
    "mandala_05_reloj_astronomico_astrolabio_eterno": {
        "width": 768,
        "height": 1376,
        "seed": 7773,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred monumental horological study of the Eternal Astrological Clock and Spherical Astrolabe, strictly no human figures. "
            "A colossal astronomical clock mechanism sculpted of dark weathered bronze, blackened iron, and carved black basalt. "
            "Nested concentric armillary rings rotate in perpetual calibration, displaying zodiacal coordinates, planetary hands, and lunar phases in gold and silver leaf. "
            "Deep shadow-filled gear teeth and mechanical counterweights hang suspended in the void, while a single sharp shaft of golden raking light illuminates the exact ticking hand at the zenith. "
            "LIGHTING: Extreme theatrical tenebrism with warm candlelight reflections on burnished bronze against 90% flat pitch-black bitumen void (#000000). "
            "Heavy oil impasto, cracked glaze, museum masterpiece, 8k"
        )
    }
}

def get_tokens():
    tokens = [os.getenv(f"HF_TOKEN_{i}") for i in range(1, 7)]
    return [t for t in tokens if t]

def convert_to_webp(src_path, dst_path):
    cmd = [
        "/usr/bin/ffmpeg", "-y", "-i", str(src_path),
        "-c:v", "libwebp", "-quality", "95", str(dst_path)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def main():
    try:
        from gradio_client import Client
    except ImportError:
        print("❌ gradio_client no está disponible en este entorno.")
        sys.exit(1)

    tokens = get_tokens()
    if not tokens:
        print("❌ No se encontraron tokens en .env")
        sys.exit(1)

    # Iniciar directamente en token 2 (índice 1) que sabemos que tiene cuota activa
    token_idx = 1
    client = Client("black-forest-labs/FLUX.1-dev", token=tokens[token_idx])
    print(f"🔑 Conectado a FLUX.1-dev con Token #{token_idx+1}")

    for name, item in MANDALAS.items():
        dst_webp = VAULT_MANDALAS / f"{name}.webp"
        if dst_webp.exists() and dst_webp.stat().st_size > 1000:
            print(f"⏩ [YA EXISTE] {name}.webp")
            continue

        print(f"\n🎨 Generando {name}...")
        success = False
        attempts = 0

        while not success and attempts < len(tokens):
            try:
                res = client.predict(
                    prompt=item["prompt"],
                    seed=item["seed"],
                    randomize_seed=False,
                    width=item["width"],
                    height=item["height"],
                    guidance_scale=3.5,
                    num_inference_steps=28,
                    api_name="/infer"
                )
                raw_img = Path(res[0])
                print(f"  ✓ Imagen generada por FLUX: {raw_img}")
                convert_to_webp(raw_img, dst_webp)
                print(f"  ✅ Guardado en Vault: {dst_webp.name} ({dst_webp.stat().st_size // 1024} KB)")
                success = True
            except Exception as e:
                err = str(e)
                print(f"  ⚠️ Error: {err[:120]}")
                token_idx = (token_idx + 1) % len(tokens)
                attempts += 1
                print(f"  🔄 Rotando a Token #{token_idx+1}...")
                client = Client("black-forest-labs/FLUX.1-dev", token=tokens[token_idx])

        if not success:
            print(f"❌ No se pudo generar {name} con ningún token.")

if __name__ == "__main__":
    main()
