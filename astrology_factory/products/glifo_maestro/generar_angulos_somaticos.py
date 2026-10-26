#!/usr/bin/env python3
"""
generar_angulos_somaticos.py
Script de automatización para generar las variables somáticas / figuras humanas al óleo
estilo Roberto Ferri para los Ángulos Cardinales: Descendente (DSC), Medio Cielo (MC) y Fondo de Cielo (IC).
Astrology Factory · El Glifo Maestro.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv("/home/LAB/astrology_factory/.env")

VAULT_BASE = Path("/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/Imagenes/Glifo_Maestro/05_Angulos_Cardinales")

CATALOG_SOMATICOS = {
    # -------------------------------------------------------------
    # 1. DESCENDENTE (DSC · El Encuentro con el Otro / Ocaso / Alianza)
    # -------------------------------------------------------------
    "dsc_v3_persona_manos_pacto_alianza": {
        "folder": "02_Descendente_DSC",
        "width": 768, "height": 1376, "seed": 8001,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Somatic anatomical human study of the Astrological Descendant (DSC, The Sacred Encounter with the Other). "
            "Two classical human hands sculpted with visceral anatomical precision in heavy oil impasto, fingers gently interlocking in a solemn sacred pact over a fractured slab of dark antique marble. "
            "Pale waxy skin tones with translucent veins, delicate alabaster dust on knuckles, and taut tendons. "
            "LIGHTING: Ruthless chiaroscuro. A single warm golden-amber and dusk-violet beam of setting sun light striking across the joined hands, "
            "emerging from 90% absolute pitch-black bitumen oil darkness (#000000). "
            "Tactile paint strokes, cracked varnish, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "dsc_v4_persona_rostro_penumbra_espejo": {
        "folder": "02_Descendente_DSC",
        "width": 768, "height": 1376, "seed": 8002,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Somatic figurative study of the Astrological Descendant (DSC, The Mirror of the Self in the Other). "
            "A classical male torso and profile in deep contemplative shadow, gazing intently into an antique dark bronze circular mirror. "
            "The expressive face is heavy with sacred melancholy and self-recognition; half of the face is carved by cold dusk light, while the other half dissolves completely into pure black void. "
            "LIGHTING: Extreme Caravaggesque tenebrism with rose-gold dusk rim light highlighting the jawline and brow against 90% impenetrable pitch-black bitumen darkness (#000000). "
            "Heavy impasto on rough linen canvas, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "dsc_v5_persona_descorrer_velo_crepusculo": {
        "folder": "02_Descendente_DSC",
        "width": 768, "height": 1376, "seed": 8003,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Somatic anatomical study of the Astrological Descendant (DSC, Crossing the Horizon of the Ego). "
            "A powerful classical human back seen from three-quarters perspective, sculpted musculature of the scapula and spine in dynamic tension as the raised arm pulls aside a heavy mantle of dark olive and crimson velvet. "
            "Beyond the curtain lies the nocturnal unknown. "
            "LIGHTING: Spectacular low-angle raking dusk light carving the dorsal muscles and vertebrae, surrounded by 90% flat pitch-black bitumen oil darkness (#000000). "
            "Tactile oil on rough linen, heavy impasto brushstrokes, authentic Roberto Ferri, 8k"
        )
    },
    "dsc_v6_persona_abrazo_polaridad_silencio": {
        "folder": "02_Descendente_DSC",
        "width": 768, "height": 1376, "seed": 8004,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Somatic anatomical study of the Astrological Descendant (DSC, Unification of the Dual Polarity). "
            "Two classical human figures locked in a sculptural, sacred embrace in the shadows, representing the sacred union of opposites. "
            "Tense, exquisitely sculpted anatomy of shoulders, arms, and collarbones with classical Greco-Roman gravitas, devoid of commercial beauty, pure fine art tragedy and grace. "
            "LIGHTING: Violent chiaroscuro with warm candlelight and dusk-violet grazing lights carving flesh against 90% absolute pitch-black bitumen darkness (#000000). "
            "Heavy impasto, cracked oil glaze, museum masterpiece, 8k"
        )
    },

    # -------------------------------------------------------------
    # 2. MEDIO CIELO (MC · El Cénit / La Soberanía / La Maestría Vocacional)
    # -------------------------------------------------------------
    "mc_v3_persona_espalda_cenit_soberania": {
        "folder": "03_Medio_Cielo_MC",
        "width": 768, "height": 1376, "seed": 8005,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Somatic anatomical study of the Astrological Midheaven (MC, Medium Coeli, The Sovereign Peak and Culmination of Destiny). "
            "A monumental, muscular classical male back standing completely erect and victorious at the summit of a cyclopean basalt peak. "
            "Trapezius, latissimus dorsi, and spinal musculature sculpted with divine tension and anatomical mastery. "
            "LIGHTING: Blinding, pure zenith chiaroscuro striking straight down from directly overhead like a shaft of divine lightning, carving the shoulders and back against 90% absolute pitch-black bitumen oil darkness (#000000). "
            "Tactile raw oil on rough linen canvas, heavy impasto, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "mc_v4_persona_manos_peso_corona": {
        "folder": "03_Medio_Cielo_MC",
        "width": 768, "height": 1376, "seed": 8006,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Somatic figurative study of the Astrological Midheaven (MC, The Gravitas and Sacred Duty of the Crown). "
            "A classical male torso and solemn head, muscular arms raised as noble hands lower a heavy crown of forged black iron and burnished gold leaf onto his own brow. "
            "Facial expression is austere, fearless, and weighed down with supreme responsibility. "
            "LIGHTING: Dramatic high-contrast theatrical chiaroscuro highlighting the raised arms, pectoral muscles, and glittering gold crown against 90% pitch-black bitumen darkness (#000000). "
            "Heavy impasto brushstrokes, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "mc_v5_persona_mirada_vertice_maestria": {
        "folder": "03_Medio_Cielo_MC",
        "width": 768, "height": 1376, "seed": 8007,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Somatic portrait study of the Astrological Midheaven (MC, The Zenith Vision of Mastery). "
            "A virile classical human bust with head tilted sharply upward toward the cosmic apex, jawline clenched in unyielding focus, pale skin glowing like polished ivory. "
            "Draped across one sculpted shoulder is a heavy ceremonial sash of antique dark crimson velvet. "
            "LIGHTING: Pure overhead vertical shaft of incandescent white-gold light illuminating forehead, nose, and collarbones against 90% flat pitch-black bitumen void (#000000). "
            "Heavy impasto, cracked oil glaze on linen, authentic Roberto Ferri, 8k"
        )
    },
    "mc_v6_persona_mano_apoyo_monolito": {
        "folder": "03_Medio_Cielo_MC",
        "width": 768, "height": 1376, "seed": 8008,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Somatic anatomical detail study of the Astrological Midheaven (MC, The Grip of Mastery at the Pinnacle). "
            "A powerful classical human arm and hand gripping the sharp upper edge of a black polished obsidian obelisk. "
            "Taut tendons in the forearm, flexing biceps, and vascular detail sculpted with hyper-realistic classical anatomy in raw oil paint. "
            "LIGHTING: Blinding directional golden raking light catching the edge of the stone and arm muscles against 90% absolute pitch-black bitumen darkness (#000000). "
            "Tactile oil on rough linen canvas, heavy impasto, authentic Roberto Ferri, 8k"
        )
    },

    # -------------------------------------------------------------
    # 3. FONDO DE CIELO (IC · El Vientre Ancestral / La Raíz / La Cripta Interior)
    # -------------------------------------------------------------
    "ic_v3_persona_vientre_origen_latido": {
        "folder": "04_Fondo_Cielo_IC",
        "width": 768, "height": 1376, "seed": 8009,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Somatic anatomical study of the Astrological Imum Coeli (IC, The Sacred Womb and Primordial Origin). "
            "An intimate classical torso in quiet repose within an underground stone crypt; two serene hands rest protectively over the lower abdomen and navel, guarding the sacred ancestral pulse. "
            "Soft alabaster flesh with subtle warm undertones and delicate vein tracings. "
            "LIGHTING: Low-key protective chiaroscuro with warm glowing ember light rising from a subterranean hearth below, illuminating hands and abdomen against 90% pitch-black bitumen darkness (#000000). "
            "Heavy oil impasto, cracked varnish, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "ic_v4_persona_postura_fetal_cripta": {
        "folder": "04_Fondo_Cielo_IC",
        "width": 768, "height": 1376, "seed": 8010,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Somatic figurative study of the Astrological Imum Coeli (IC, The Primordial Sleep of the Soul). "
            "A classical human figure curled in a sacred fetal position resting upon a cold limestone slab inside an ancient crypt. "
            "Curved spine, shoulder blades, and folded knees sculpted with exquisite classical Caravaggesque anatomical tenderness and power. "
            "LIGHTING: Deep subterranean tenebrism; a faint thread of amber flame from an oil lamp carves the contour of the back against 90% absolute pitch-black bitumen oil darkness (#000000). "
            "Tactile rough linen texture, heavy impasto, authentic Roberto Ferri, 8k"
        )
    },
    "ic_v5_persona_manos_tierra_ancestral": {
        "folder": "04_Fondo_Cielo_IC",
        "width": 768, "height": 1376, "seed": 8011,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Somatic anatomical study of the Astrological Imum Coeli (IC, Grounding into Ancestral Earth). "
            "Two noble, weathered hands scooping rich dark loam and primordial soil mixed with flakes of ancient gold dust, letting the substance spill slowly through the fingers. "
            "Intricate skin textures, fingernails, and wrinkles rendered with sacred classical realism. "
            "LIGHTING: Warm ember-lit chiaroscuro grazing across the hands and falling earth against 90% flat pitch-black bitumen darkness (#000000). "
            "Heavy impasto on linen canvas, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "ic_v6_persona_descanso_hombro_ancestro": {
        "folder": "04_Fondo_Cielo_IC",
        "width": 768, "height": 1376, "seed": 8012,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Somatic figurative study of the Astrological Imum Coeli (IC, Communion with the Forebears). "
            "A living classical youth resting their forehead with deep emotional reverence against the weathered marble shoulder of an ancient ancestral statue covered in pale patina. "
            "The stark contrast between living breathing warm flesh and cold cracked antique stone. "
            "LIGHTING: Poignant, melancholic low-key chiaroscuro with warm candlelight glancing off the cheek and marble drapery against 90% pitch-black bitumen void (#000000). "
            "Tactile raw oil, heavy impasto brushstrokes, authentic Roberto Ferri museum masterpiece, 8k"
        )
    }
}

def convert_to_webp(src_file, dst_file):
    cmd = [
        "/usr/bin/ffmpeg", "-y", "-i", str(src_file),
        "-c:v", "libwebp", "-quality", "95", str(dst_file)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def get_tokens_pool():
    tokens = []
    for i in range(1, 7):
        t = os.getenv(f"HF_TOKEN_{i}")
        if t and t not in tokens:
            tokens.append(t)
    main_t = os.getenv("HF_TOKEN")
    if main_t and main_t not in tokens:
        tokens.append(main_t)
    return tokens

def run_batch(catalog):
    try:
        from gradio_client import Client
    except ImportError:
        print("❌ Error: gradio_client no está disponible.")
        return

    tokens = get_tokens_pool()
    if not tokens:
        print("❌ Error: No se encontraron tokens HF_TOKEN.")
        return

    token_idx = 0
    client = None

    def get_client(idx):
        t = tokens[idx % len(tokens)]
        print(f"🔑 Conectando con token #{idx % len(tokens) + 1} ({t[:10]}...)...")
        return Client("black-forest-labs/FLUX.1-dev", token=t)

    client = get_client(token_idx)

    for name, item in catalog.items():
        dst_folder = VAULT_BASE / item["folder"]
        dst_folder.mkdir(parents=True, exist_ok=True)
        final_webp = dst_folder / f"{name}.webp"

        if final_webp.exists() and final_webp.stat().st_size > 1000:
            print(f"⏩ [YA EXISTE] {name}.webp en {dst_folder}")
            continue

        print(f"\n🎨 Generando {name} (FLUX.1-dev)...")
        success = False
        attempts = 0

        while not success and attempts < len(tokens):
            try:
                result = client.predict(
                    prompt=item["prompt"],
                    seed=item["seed"],
                    randomize_seed=False,
                    width=item["width"],
                    height=item["height"],
                    guidance_scale=3.5,
                    num_inference_steps=28,
                    api_name="/infer"
                )
                raw_img = Path(result[0])
                print(f"  ✓ Imagen generada: {raw_img}")
                convert_to_webp(raw_img, final_webp)
                print(f"  ✅ WebP guardado con éxito: {final_webp} ({final_webp.stat().st_size // 1024} KB)")
                success = True
            except Exception as e:
                err_str = str(e)
                print(f"  ⚠️ Error con token actual: {err_str}")
                if "ZeroGPU runs limit" in err_str or "exceeded" in err_str.lower() or "quota" in err_str.lower():
                    token_idx += 1
                    attempts += 1
                    if attempts < len(tokens):
                        print(f"  🔄 Rotando a siguiente token ({token_idx % len(tokens) + 1}/{len(tokens)})...")
                        client = get_client(token_idx)
                    else:
                        print("  ❌ Todos los tokens disponibles han agotado su cuota de ZeroGPU.")
                        return
                else:
                    print(f"  ❌ Error en {name}: {e}")
                    # Reintento con siguiente token
                    token_idx += 1
                    attempts += 1
                    if attempts < len(tokens):
                        print(f"  🔄 Probando con token #{token_idx % len(tokens) + 1}...")
                        client = get_client(token_idx)
                    else:
                        break

def main():
    parser = argparse.ArgumentParser(description="Generador de variables somáticas para Ángulos Cardinales.")
    parser.add_argument("--dry-run", action="store_true", help="Solo listar inventario")
    args = parser.parse_args()

    if args.dry_run:
        print(f"📋 DRY-RUN: {len(CATALOG_SOMATICOS)} activos listados:")
        for k, v in CATALOG_SOMATICOS.items():
            print(f" - [{k}] -> {v['folder']}/{k}.webp")
        return

    run_batch(CATALOG_SOMATICOS)

if __name__ == "__main__":
    main()
