#!/usr/bin/env python3
"""
generar_variantes_y_nodos.py
Script de automatización para generar variantes de Casas, Geometría y los Puntos Kármicos
restantes (Nodo Norte, Nodo Sur, Pars Fortunae) en FLUX.1-dev.
Astrology Factory · El Glifo Maestro.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv("/home/LAB/astrology_factory/.env")

VAULT_BASE = Path("/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/Imagenes/Glifo_Maestro")

CATALOG_VARIANTES = {
    # -------------------------------------------------------------
    # 1. PUNTOS KÁRMICOS FALTANTES (Nodos Lunares y Pars Fortunae)
    # -------------------------------------------------------------
    "nodo_norte_cabeza_dragon": {
        "folder": "03_Puntos_Karmicos_y_Sanacion/03_Nodo_Norte",
        "width": 768, "height": 1376, "seed": 7001,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred esoteric study of the North Node of the Moon (Caput Draconis, Dragon's Head, Karmic Destiny and Future Calling), "
            "strictly no human figures, completely pure fine art. An ascending monumental spiral vortex sculpted from black basalt and veined antique gold. "
            "At the apex of the ascending horn of plenty, a luminous incandescent orb of solar-lunar white gold radiates fierce golden rays upward. "
            "Archaic lunar glyphs and dragon scales chiseled into the weathered stone texture. "
            "LIGHTING: Intense ascending chiaroscuro with radiant gold and amber illumination breaking through 90% absolute pitch-black bitumen darkness (#000000). "
            "Tactile raw oil on rough linen canvas, heavy impasto brushstrokes, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "nodo_sur_cola_dragon": {
        "folder": "03_Puntos_Karmicos_y_Sanacion/04_Nodo_Sur",
        "width": 768, "height": 1376, "seed": 7002,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred esoteric study of the South Node of the Moon (Cauda Draconis, Dragon's Tail, Ancestral Memory and Past Karma to Release), "
            "strictly no human figures, completely pure fine art. An ancient subterranean stone well of dark cracked granite with a descending coiling dragon tail relief. "
            "Resting on the rim of the well is a heavy antique terracotta urn partially tipped, spilling ancient golden sands, dried lavender seeds, and smoldering embers of past lives into the dark abyss. "
            "Faint wisps of violet smoke drift upward. "
            "LIGHTING: Deep melancholic tenebrism with warm ember-orange rim light and quiet bronze highlights against 90% flat pitch-black bitumen oil darkness (#000000). "
            "Tactile raw oil on rough linen canvas, heavy impasto, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "rueda_fortuna_pars_fortunae": {
        "folder": "03_Puntos_Karmicos_y_Sanacion/05_Rueda_de_la_Fortuna",
        "width": 768, "height": 1376, "seed": 7003,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural altar study of the Part of Fortune (Pars Fortunae, Sacred Providence and Cosmic Alignment), "
            "strictly no human figures, completely pure fine art. An immense circular disc of polished green malachite and chased antique bronze resting on a carved marble plinth. "
            "Engraved on the disc is the circle containing an equal-armed cross, inlaid with pure beaten gold leaf. Around the base of the plinth overflow ripe pomegranates, golden wheat sheaves, and antique silver coins. "
            "LIGHTING: Glorious golden-amber raking chiaroscuro revealing the deep malachite textures and glistening gold leaf against 90% impenetrable pitch-black bitumen void (#000000). "
            "Tactile raw oil on rough linen canvas, heavy impasto, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },

    # -------------------------------------------------------------
    # 2. VARIANTES v2 DE LAS CASAS ASTROLÓGICAS (Enfoque Altar / Relicario)
    # -------------------------------------------------------------
    "casa_01_v2_altar_relicario_aurora": {
        "folder": "04_Casas_Astrologicas/01_Casa_1_Identidad_Umbral",
        "width": 768, "height": 1376, "seed": 7011,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred altar closeup of the 1st Astrological House (House of Emergence and Dawn of the Self), strictly no human figures, completely pure fine art. "
            "A monolithic pedestal of raw fractured granite holding a hand-forged bronze brazier glowing with violent crimson and gold embers. "
            "A single ceremonial gladius sword of blackened steel with a gold hilt stands vertically impaled into a stone block, catching the first razor-sharp ray of dawn light. "
            "Aries sigil etched in deep relief. "
            "LIGHTING: Blinding directional dawn chiaroscuro cutting across steel, embers, and dark stone against 90% pitch-black bitumen darkness (#000000). "
            "Heavy impasto, cracked oil glaze on rough linen, authentic Roberto Ferri, 8k"
        )
    },
    "casa_02_v2_arca_balanza_subterranea": {
        "folder": "04_Casas_Astrologicas/02_Casa_2_Recursos_Boveda",
        "width": 768, "height": 1376, "seed": 7012,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred relic study of the 2nd Astrological House (House of Wealth, Sustenance and Earthly Gold), strictly no human figures, completely pure fine art. "
            "On a cold slab of dark serpentine stone rests a massive dual-pan apothecary balance forged of blackened iron and brass in perfect balance. "
            "One pan holds an unworked raw emerald geode; the other holds a stack of rough antique gold coins stamped with bull icons. "
            "In the background, thick wax beeswax candles pool golden tallow on the stone. "
            "LIGHTING: Intimate tenebrism with rich warm candle gleam reflecting off metal and crystal against 88% pitch-black bitumen void (#000000). "
            "Tactile oil on rough linen canvas, heavy impasto, authentic Roberto Ferri, 8k"
        )
    },
    "casa_03_v2_relicario_pergaminos_mercurio": {
        "folder": "04_Casas_Astrologicas/03_Casa_3_Mente_Biblioteca",
        "width": 768, "height": 1376, "seed": 7013,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred altar closeup of the 3rd Astrological House (House of Intellect, Inscription, and Fast Thought), strictly no human figures, completely pure fine art. "
            "An angled limestone lectern holding open an illuminated manuscript of thick vellum with geometric celestial charts in vermilion ink. "
            "Beside it lies a quill made of an iridescent raven feather, an open inkpot of deep indigo, and a sealed glass phial filled with luminous liquid quicksilver mercury catching pale silver light. "
            "LIGHTING: Cold silver chiaroscuro glancing off parchment and quicksilver against 90% absolute pitch-black bitumen darkness (#000000). "
            "Heavy impasto, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_04_v2_fuego_cripta_honda": {
        "folder": "04_Casas_Astrologicas/04_Casa_4_Raiz_Santuario",
        "width": 768, "height": 1376, "seed": 7014,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred relic closeup of the 4th Astrological House (House of the Ancestral Hearth and Foundation), strictly no human figures, completely pure fine art. "
            "A cavernous subterranean hearth carved directly out of living limestone, glowing with steady, deep crimson and amber coals. "
            "Beside the hearth sits a classical carved marble urn containing consecrated water reflecting the flame, draped with a rough woven wool heirloom cloth. "
            "Ancient Crab (Cancer) sigils carved above the mantle. "
            "LIGHTING: Warm, protective low-key tenebrism. Deep amber firelight sculpting rustic stone and water reflection against 88% flat pitch-black bitumen void (#000000). "
            "Heavy impasto, authentic Roberto Ferri, 8k"
        )
    },
    "casa_05_v2_corona_oro_teatro": {
        "folder": "04_Casas_Astrologicas/05_Casa_5_Creacion_Teatro",
        "width": 768, "height": 1376, "seed": 7015,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred altar study of the 5th Astrological House (House of Creative Radiance and Sovereignty), strictly no human figures, completely pure fine art. "
            "A pedestal of deep red porphyry stone draped in rich dark crimson velvet. "
            "Resting upon the velvet is an imperial crown of hand-beaten gold laurel leaves and a solid gold ceremonial chalice overflowing with ruby-red wine. "
            "In the background, a classical theatrical bronze tragic mask rests against a fluted column fragment. "
            "LIGHTING: Theatrical golden-amber raking spotlight illuminating the gold crown and red velvet against 90% pitch-black bitumen darkness (#000000). "
            "Tactile raw oil on rough linen canvas, heavy impasto, authentic Roberto Ferri, 8k"
        )
    },
    "casa_06_v2_alambique_botanica_sagrada": {
        "folder": "04_Casas_Astrologicas/06_Casa_6_Alquimia_Taller",
        "width": 768, "height": 1376, "seed": 7016,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred apothecary study of the 6th Astrological House (House of Sacred Botany and Purifying Craft), strictly no human figures, completely pure fine art. "
            "A heavy rustic oak table with a hand-hammered antique copper alembic still with condensation glistening on its curves. "
            "Beside it stands a dark green serpentine stone mortar with a pestle grinding dried aromatic chamomile flowers and sage leaves. "
            "Handmade glass medicine bottles filled with amber herbal tinctures neatly arranged in a row. "
            "LIGHTING: Contemplative amber chiaroscuro coming from a narrow side aperture, highlighting copper and glass against 88% pitch-black bitumen darkness (#000000). "
            "Heavy impasto, authentic Roberto Ferri, 8k"
        )
    },
    "casa_07_v2_espejo_pacto_crepusculo": {
        "folder": "04_Casas_Astrologicas/07_Casa_7_Alianzas_Espejos",
        "width": 768, "height": 1376, "seed": 7017,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred altar study of the 7th Astrological House (House of Sacred Pacts and the Mirror of the Other), strictly no human figures, completely pure fine art. "
            "On a dark polished marble dais stands an ornate circular bronze mirror framed by entwined sculpted vines. "
            "Across the mirror's burnished glass surface reflects a sliver of deep twilight rose-gold sky. "
            "Before the mirror lie two unlit interlocking rings of antique platinum and rose gold resting on a folded square of dark olive silk. "
            "LIGHTING: Romantic and austere dusk chiaroscuro with soft rose, amber, and violet tones rimming the mirror against 90% pitch-black bitumen void (#000000). "
            "Tactile oil on rough linen, heavy impasto, authentic Roberto Ferri, 8k"
        )
    },
    "casa_08_v2_crisol_transmutacion_renacimiento": {
        "folder": "04_Casas_Astrologicas/08_Casa_8_Transmutacion_Cripta",
        "width": 768, "height": 1376, "seed": 7018,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred altar study of the 8th Astrological House (House of Death, Alchemical Crucible, and Rebirth), strictly no human figures, completely pure fine art. "
            "In the center of an underground stone vault sits a heavy cast-iron alchemical crucible filled with bubbling liquid gold and emerald-green flame. "
            "Beside the crucible lies an antique carved raven skull resting on a black volcanic stone slab, with drops of solidified molten wax and Scorpio sigils etched in gold leaf. "
            "LIGHTING: Ominous and hypnotic chiaroscuro with sulfurous emerald and molten gold light carving out the stone against 90% absolute pitch-black bitumen darkness (#000000). "
            "Heavy impasto, cracked glaze, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_09_v2_astrolabio_brujula_navegacion": {
        "folder": "04_Casas_Astrologicas/09_Casa_9_Filosofia_Observatorio",
        "width": 768, "height": 1376, "seed": 7019,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred instruments study of the 9th Astrological House (House of Higher Wisdom, Pilgrimage, and the Cosmic Horizon), strictly no human figures, completely pure fine art. "
            "An elevated marble balustrade overlooking a nocturnal sea. "
            "On a carved stone stand rests an intricate antique brass astrolabe and a sighting quadrant engraved with Arabic astrological degrees. "
            "Beside the astrolabe sits an open nautical map on weathered vellum marked with constellation routes, held down by an uncut sapphire paperweight. "
            "LIGHTING: Celestial chiaroscuro. Cool starlight and warm brass gleam against 88% flat pitch-black bitumen void (#000000). "
            "Heavy impasto, authentic Roberto Ferri, 8k"
        )
    },
    "casa_10_v2_columna_trono_obelisco": {
        "folder": "04_Casas_Astrologicas/10_Casa_10_Vocacion_Cima",
        "width": 768, "height": 1376, "seed": 7020,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred altar study of the 10th Astrological House (House of Zenith, Mastery, and Supreme Standing), strictly no human figures, completely pure fine art. "
            "A monolithic pedestal of dark veined granite at the summit of a mountain of basalt steps. "
            "Upon the pedestal sits a hand-carved stone throne with Capricorn sigils, accompanied by an upright black obsidian obelisk capped with pure electrum gold pyramidion. "
            "LIGHTING: Pure vertical zenith chiaroscuro striking from directly overhead like a shaft of divine order, carving the obelisk against 90% pitch-black bitumen darkness (#000000). "
            "Heavy impasto brushstrokes, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_11_v2_orbe_constelaciones_alianza": {
        "folder": "04_Casas_Astrologicas/11_Casa_11_Comunidad_Estrellas",
        "width": 768, "height": 1376, "seed": 7021,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred altar study of the 11th Astrological House (House of Collective Vision and the Brotherhood of Stars), strictly no human figures, completely pure fine art. "
            "A circular stone table of dark slate upon which rests a hollow brass and silver armillary sphere containing twelve concentric rings aligning in cosmic harmony. "
            "Surrounding the base of the sphere are twelve unlit votive silver chalices placed in a perfect ring on the stone. "
            "LIGHTING: Ethereal silver and pale gold chiaroscuro tracing the delicate rings of the armillary sphere against 90% pitch-black bitumen darkness (#000000). "
            "Heavy impasto, authentic Roberto Ferri, 8k"
        )
    },
    "casa_12_v2_velo_oceano_niebla_eterna": {
        "folder": "04_Casas_Astrologicas/12_Casa_12_Trascendencia_Niebla",
        "width": 768, "height": 1376, "seed": 7022,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred altar study of the 12th Astrological House (House of Transcendence, the Dissolving Veil, and Cosmic Return), strictly no human figures, completely pure fine art. "
            "Submerged stone steps descending into a subterranean pool of motionless black water covered in a blanket of pale luminous mist. "
            "Resting on the highest dry step is a heavy chalice of dark obsidian filled to the brim with clear water, with a gossamer veil of antique translucent silk draped over the rim into the dark pool. "
            "LIGHTING: Dreamlike, mystical low-key tenebrism with faint ghostly luminescence reflecting off the mist and obsidian chalice against 90% absolute pitch-black bitumen void (#000000). "
            "Heavy impasto, authentic Roberto Ferri museum masterpiece, 8k"
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
    # Prioridad: De más nuevo (HF_TOKEN_6) a los anteriores
    for i in [6, 5, 4, 3, 2, 1]:
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
                    print(f"  ❌ Error irrecuperable en {name}: {e}")
                    break

def main():
    parser = argparse.ArgumentParser(description="Generador de variantes y nodos.")
    parser.add_argument("--dry-run", action="store_true", help="Solo listar inventario")
    args = parser.parse_args()

    if args.dry_run:
        print(f"📋 DRY-RUN: {len(CATALOG_VARIANTES)} activos listados:")
        for k, v in CATALOG_VARIANTES.items():
            print(f" - [{k}] -> {v['folder']}/{k}.webp")
        return

    run_batch(CATALOG_VARIANTES)

if __name__ == "__main__":
    main()
