#!/usr/bin/env python3
"""
generar_casas_v3_v4.py
Script de automatización para generar las variables v3 (Reliquia Alquímica) y v4 (Portal y Umbral Ciclópeo)
de las 12 Casas Astrológicas en FLUX.1-dev.
Astrology Factory · El Glifo Maestro.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv("/home/LAB/astrology_factory/.env")

VAULT_BASE = Path("/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/Imagenes/Glifo_Maestro/04_Casas_Astrologicas")

CATALOG_CASAS_V3_V4 = {
    # -------------------------------------------------------------
    # CASA 1 (Aries / ASC · Identidad y Emergencia)
    # -------------------------------------------------------------
    "casa_01_v3_reliquia_espada_fuego": {
        "folder": "01_Casa_1_Identidad_Umbral",
        "width": 768, "height": 1376, "seed": 9101,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred relic study of the 1st Astrological House (House of Emergence and Primeval Will), strictly no human figures. "
            "A monolithic altar of rough cracked dark volcanic basalt upon which a ritual iron gladius sword stands embedded into living rock. "
            "Glowing golden embers and vermilion sparks drift upward from cracks in the stone; the polished steel blade catches a blinding diagonal ray of dawn light. "
            "LIGHTING: Violent dawn chiaroscuro cutting across steel and dark stone against 90% absolute pitch-black bitumen darkness (#000000). "
            "Heavy oil impasto, tactile brushstrokes, cracked glaze on linen canvas, museum masterpiece, 8k"
        )
    },
    "casa_01_v4_portal_grieta_aurora": {
        "folder": "01_Casa_1_Identidad_Umbral",
        "width": 768, "height": 1376, "seed": 9102,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural threshold study of the 1st Astrological House, strictly no human figures. "
            "A colossal cyclopean gateway of dark weathered limestone standing cracked open in the nocturnal void. "
            "Through the vertical fissure between the colossal doors, an incandescent rose-gold dawn beam cuts diagonally across ancient stone steps, casting long raking shadows. "
            "LIGHTING: Intense directional dawn raking chiaroscuro against 90% flat pitch-black bitumen darkness (#000000). "
            "Heavy impasto, cracked varnish on rough linen canvas, authentic Roberto Ferri, 8k"
        )
    },

    # -------------------------------------------------------------
    # CASA 2 (Tauro · Recursos y Materia Sagrada)
    # -------------------------------------------------------------
    "casa_02_v3_lingote_oro_cristal_esmeralda": {
        "folder": "02_Casa_2_Recursos_Boveda",
        "width": 768, "height": 1376, "seed": 9103,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred relic study of the 2nd Astrological House (House of Earthly Substance and Value), strictly no human figures. "
            "On a cold slab of dark green serpentine stone sits a massive raw unworked emerald crystal geode beside thick hand-poured antique gold ingots with centuries of patina. "
            "A heavy bronze oil lamp flickers softly nearby, catching the polished metallic luster and mineral facets. "
            "LIGHTING: Rich, opulent chiaroscuro with warm golden highlights and deep emerald shadows against 88% pitch-black bitumen darkness (#000000). "
            "Heavy impasto, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_02_v4_umbral_cripta_serpentina": {
        "folder": "02_Casa_2_Recursos_Boveda",
        "width": 768, "height": 1376, "seed": 9104,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural study of the 2nd Astrological House, strictly no human figures. "
            "A subterranean treasury corridor built of massive cyclopean dark slate and polished serpentine pillars descending into shadow. "
            "At the threshold stands an immense hand-forged black iron gate chained with heavy bronze links, illuminated by unseen warm tallow torches. "
            "LIGHTING: Low-key subterranean chiaroscuro with warm amber gleams grazing stone textures against 90% pitch-black bitumen darkness (#000000). "
            "Tactile oil on rough linen, authentic Roberto Ferri, 8k"
        )
    },

    # -------------------------------------------------------------
    # CASA 3 (Géminis · Intelecto, Pergaminos y Senderos)
    # -------------------------------------------------------------
    "casa_03_v3_esfera_quicksilver_pluma": {
        "folder": "03_Casa_3_Mente_Biblioteca",
        "width": 768, "height": 1376, "seed": 9105,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred relic study of the 3rd Astrological House (House of Intellect and Inscription), strictly no human figures. "
            "A sculpted limestone console holding an antique glass sphere filled with mirror-like liquid mercury quicksilver reflecting pale light. "
            "Beside it lies an iridescent raven feather quill resting on open vellum covered in hand-drawn geometric constellations and sepia ink notes. "
            "LIGHTING: Cold silver-white chiaroscuro glancing off the reflective mercury sphere against 90% absolute pitch-black bitumen void (#000000). "
            "Heavy oil impasto, cracked glaze, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_03_v4_puente_bifurcacion_abismo": {
        "folder": "03_Casa_3_Mente_Biblioteca",
        "width": 768, "height": 1376, "seed": 9106,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural study of the 3rd Astrological House, strictly no human figures. "
            "A monumental double stone arch and bifurcated bridge carved of pale grey marble suspended over a mist-shrouded dark chasm. "
            "The two narrow stone pathways diverge into the shadows, flanked by slender classical balustrades under a nocturnal sky. "
            "LIGHTING: Dramatic quicksilver and starlight chiaroscuro highlighting stone balustrades against 90% flat pitch-black bitumen darkness (#000000). "
            "Tactile oil on linen, heavy impasto, authentic Roberto Ferri, 8k"
        )
    },

    # -------------------------------------------------------------
    # CASA 4 (Cáncer / IC · Santuario y Raíz Ancestral)
    # -------------------------------------------------------------
    "casa_04_v3_urna_agua_espejo_ancestros": {
        "folder": "04_Casa_4_Raiz_Santuario",
        "width": 768, "height": 1376, "seed": 9107,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred relic study of the 4th Astrological House (House of the Hearth and Ancestral Lineage), strictly no human figures. "
            "A classical carved circular marble basin filled to the brim with clear motionless water reflecting the warm glow of an unseen hearth. "
            "Around the rim rest weathered marble funerary medallions of forgotten forebears and dried sprigs of wild myrtle on rustic stone flagstones. "
            "LIGHTING: Intimate, protective amber chiaroscuro with firelight reflecting off dark water against 88% pitch-black bitumen darkness (#000000). "
            "Heavy impasto, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_04_v4_cripta_subterranea_raices": {
        "folder": "04_Casa_4_Raiz_Santuario",
        "width": 768, "height": 1376, "seed": 9108,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural study of the 4th Astrological House, strictly no human figures. "
            "A cavernous underground vault carved from living limestone bedrock with massive natural tree roots entwined through the ceiling masonry. "
            "In the center of the flagstone floor, an ancient round hearth burns with quiet eternal embers, casting long dancing shadows across curved stone arches. "
            "LIGHTING: Warm, deep subterranean tenebrism with rich amber firelight fading into 90% pitch-black bitumen darkness (#000000). "
            "Tactile oil on linen, authentic Roberto Ferri, 8k"
        )
    },

    # -------------------------------------------------------------
    # CASA 5 (Leo · Fuego Creativo y Teatro Sacro)
    # -------------------------------------------------------------
    "casa_05_v3_caliz_oro_mascara_tragedia": {
        "folder": "05_Casa_5_Creacion_Teatro",
        "width": 768, "height": 1376, "seed": 9109,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred relic study of the 5th Astrological House (House of Creative Sovereignty), strictly no human figures. "
            "On a carved pedestal of crimson Verona marble rests an opulent antique chalice of hammered gold overflowing with dark ruby wine. "
            "Beside it lies an expressive beaten-bronze theatrical tragedy mask with delicate verdigris patina, catching golden embers from a nearby brazier. "
            "LIGHTING: Theatrical high-contrast golden-amber chiaroscuro striking metal and velvet against 90% absolute pitch-black bitumen void (#000000). "
            "Heavy oil impasto, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_05_v4_proscenio_teatro_ruinas": {
        "folder": "05_Casa_5_Creacion_Teatro",
        "width": 768, "height": 1376, "seed": 9110,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural study of the 5th Astrological House, strictly no human figures. "
            "A semicircular Greco-Roman ruined theater stage of red porphyry and veined marble standing in majestic solitary ruins. "
            "In the center of the proscenium, a tripod altar of blackened bronze burns with tall golden-vermilion flames lighting up fluted column fragments. "
            "LIGHTING: Spectacular theatrical spotlight effect from the blazing altar against 90% pitch-black bitumen darkness (#000000). "
            "Tactile raw oil, heavy impasto, authentic Roberto Ferri, 8k"
        )
    },

    # -------------------------------------------------------------
    # CASA 6 (Virgo · Alquimia y Botánica Sagrada)
    # -------------------------------------------------------------
    "casa_06_v3_mortero_serpentina_esencias": {
        "folder": "06_Casa_6_Alquimia_Taller",
        "width": 768, "height": 1376, "seed": 9111,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred apothecary relic study of the 6th Astrological House (House of Sacred Craft and Purifying Botany), strictly no human figures. "
            "A rustic dark oak workbench with an antique dark green serpentine mortar and pestle grinding dried golden calendula and dried sage leaves. "
            "Beside it stand calibrated bronze balance weights and hand-blown glass phials containing amber oils and herbal tinctures. "
            "LIGHTING: Quiet, monastic amber chiaroscuro coming from a narrow stone slit against 88% pitch-black bitumen darkness (#000000). "
            "Heavy impasto, cracked varnish, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_06_v4_portico_monasterio_granito": {
        "folder": "06_Casa_6_Alquimia_Taller",
        "width": 768, "height": 1376, "seed": 9112,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural study of the 6th Astrological House, strictly no human figures. "
            "A severe, austere monastic apothecary arcade of rough grey granite with vaulted arches. "
            "Bundles of drying lavender and medicinal herbs hang from dark wooden crossbeams; along the stone wall stand rows of carved wooden apothecary cabinets with Latin labels. "
            "LIGHTING: Contemplative directional raking chiaroscuro carving the stone arcade against 90% flat pitch-black bitumen darkness (#000000). "
            "Tactile oil on rough linen, authentic Roberto Ferri, 8k"
        )
    },

    # -------------------------------------------------------------
    # CASA 7 (Libra / DSC · Alianzas y el Espejo del Otro)
    # -------------------------------------------------------------
    "casa_07_v3_anillos_pacto_filigrana": {
        "folder": "07_Casa_7_Alianzas_Espejos",
        "width": 768, "height": 1376, "seed": 9113,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred relic study of the 7th Astrological House (House of Sacred Pacts and the Mirror of the Other), strictly no human figures. "
            "On a dark polished marble table reflecting like dark water rests a ceremonial cushion of folded moss-green velvet. "
            "Upon it lie two interlocking rings of heavy antique platinum and rose gold with delicate filigree, beside a small unlit bronze twin-wick oil lamp. "
            "LIGHTING: Dusk chiaroscuro with subtle rose-amber and twilight-violet highlights reflecting off polished stone against 90% pitch-black bitumen void (#000000). "
            "Heavy oil impasto, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_07_v4_portal_gemelo_crepusculo": {
        "folder": "07_Casa_7_Alianzas_Espejos",
        "width": 768, "height": 1376, "seed": 9114,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural study of the 7th Astrological House, strictly no human figures. "
            "A twin symmetrical colonnade of fluted white marble Ionic columns framing an immense bronze circular arch standing at the edge of a nocturnal precipice. "
            "Through the portal, the deep purple-gold glow of an extinguished sunset reflects off polished dark flagstones. "
            "LIGHTING: Austere dusk raking chiaroscuro grazing marble flutes and bronze metalwork against 90% absolute pitch-black bitumen darkness (#000000). "
            "Tactile oil on rough linen, authentic Roberto Ferri, 8k"
        )
    },

    # -------------------------------------------------------------
    # CASA 8 (Escorpio · Cripta y Transmutación)
    # -------------------------------------------------------------
    "casa_08_v3_calavera_cuervo_cera_oro": {
        "folder": "08_Casa_8_Transmutacion_Cripta",
        "width": 768, "height": 1376, "seed": 9115,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred relic study of the 8th Astrological House (House of Death, Alchemical Transmutation and Regeneration), strictly no human figures. "
            "A black volcanic stone pedestal holding an antique carved bone raven skull and an iron crucible bubbling with liquid electrum gold. "
            "Drops of black beeswax and dried nightshade berries surround the crucible, with a single scorpion sigil etched in pure gold leaf into the stone. "
            "LIGHTING: Hypnotic sulfurous emerald and molten gold chiaroscuro emerging from 90% absolute pitch-black bitumen oil darkness (#000000). "
            "Heavy oil impasto, cracked varnish on linen, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_08_v4_pozo_abismo_renacimiento": {
        "folder": "08_Casa_8_Transmutacion_Cripta",
        "width": 768, "height": 1376, "seed": 9116,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural study of the 8th Astrological House, strictly no human figures. "
            "A circular subterranean stone well carved into rough obsidian bedrock descending into the endless abyss. "
            "From the mouth of the deep well radiates a subtle, unearthly emerald and golden luminescence, lighting up moisture droplets on ancient stone arches. "
            "LIGHTING: Deep, sinister yet sacred subterranean chiaroscuro carving wet stone against 90% flat pitch-black bitumen darkness (#000000). "
            "Tactile oil on linen, authentic Roberto Ferri, 8k"
        )
    },

    # -------------------------------------------------------------
    # CASA 9 (Sagitario · Filosofía y Observatorio Cósmico)
    # -------------------------------------------------------------
    "casa_09_v3_cuadrante_optica_astrolabio": {
        "folder": "09_Casa_9_Filosofia_Observatorio",
        "width": 768, "height": 1376, "seed": 9117,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred instruments study of the 9th Astrological House (House of Higher Mind, Pilgrimage and the Cosmic Horizon), strictly no human figures. "
            "On a stone balustrade rests a complex antique brass astrolabe engraved with celestial coordinates, beside an open nautical chart on weathered vellum. "
            "A large raw unpolished sapphire crystal rests on the paper as a weight, refracting faint silver starlight. "
            "LIGHTING: Cold starlight chiaroscuro mixed with warm brass glints against 88% flat pitch-black bitumen darkness (#000000). "
            "Heavy impasto, cracked glaze on linen canvas, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_09_v4_escalinata_cumbre_horizonte": {
        "folder": "09_Casa_9_Filosofia_Observatorio",
        "width": 768, "height": 1376, "seed": 9118,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural study of the 9th Astrological House, strictly no human figures. "
            "A monumental cyclopean open-air stone terrace and high observation rotunda perched atop a dizzying mountain precipice overlooking a nocturnal abyss. "
            "Slender classical columns support a broken dome open to the starry void; an ancient stone sighting-quadrant aims toward the infinite sky. "
            "LIGHTING: Grand, majestic nocturnal chiaroscuro with starlight and amber torchlight grazing marble steps against 90% pitch-black bitumen void (#000000). "
            "Tactile oil on rough linen, authentic Roberto Ferri, 8k"
        )
    },

    # -------------------------------------------------------------
    # CASA 10 (Capricornio / MC · Cénit, Destino y Ciudadela)
    # -------------------------------------------------------------
    "casa_10_v3_cetro_electrum_trono_roca": {
        "folder": "10_Casa_10_Destino_Ciudadela",
        "width": 768, "height": 1376, "seed": 9119,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred relic study of the 10th Astrological House (House of Mastery, Culmination and Sovereign Duty), strictly no human figures. "
            "On a dais of dark veined granite sits a hand-carved stone throne. Resting upon the throne is a heavy ceremonial scepter of electrum and dark horn, "
            "flanked by an iron seal bearing the Capricorn mountain glyph. "
            "LIGHTING: Ruthless perpendicular zenith chiaroscuro striking from straight above, carving metal and granite against 90% absolute pitch-black bitumen darkness (#000000). "
            "Heavy oil impasto, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_10_v4_muralla_basalto_cenit": {
        "folder": "10_Casa_10_Destino_Ciudadela",
        "width": 768, "height": 1376, "seed": 9120,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural study of the 10th Astrological House, strictly no human figures. "
            "A monumental cyclopean citadel wall of massive interlocking black basalt blocks rising toward the sky like an impregnable mountain fortress. "
            "At the highest parapet stands a sharp obsidian obelisk capped in beaten gold, illuminated by a fierce vertical beam of divine sunlight. "
            "LIGHTING: Extreme vertical zenith light carving the stone ramparts against 90% pitch-black bitumen oil void (#000000). "
            "Tactile raw oil on rough linen canvas, heavy impasto, authentic Roberto Ferri, 8k"
        )
    },

    # -------------------------------------------------------------
    # CASA 11 (Acuario · Visión Colectiva y Ágora Estelar)
    # -------------------------------------------------------------
    "casa_11_v3_anillos_armilar_plata": {
        "folder": "11_Casa_11_Vision_Agora",
        "width": 768, "height": 1376, "seed": 9121,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred relic study of the 11th Astrological House (House of the Collective Vision and Star Alliance), strictly no human figures. "
            "On a circular dark slate plinth rests a complex hollow armillary sphere forged of polished silver and tarnished brass, its concentric rings perfectly aligned. "
            "Surrounding the base are twelve silver chalices arranged in a sacred circle, reflecting pale starlight. "
            "LIGHTING: Ethereal silver and pale gold chiaroscuro tracing metallic arcs against 90% pitch-black bitumen darkness (#000000). "
            "Heavy oil impasto, cracked varnish, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_11_v4_templo_circular_estrellas": {
        "folder": "11_Casa_11_Vision_Agora",
        "width": 768, "height": 1376, "seed": 9122,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural study of the 11th Astrological House, strictly no human figures. "
            "A roofless classical circular agora and peristyle of pale stone columns standing suspended in the void under a dense canopy of stars. "
            "In the center of the geometric pavement stands a monumental bronze astrometric device with delicate planetary pointers. "
            "LIGHTING: Cold celestial starlight with silver rim lighting carving the circular columns against 90% absolute pitch-black bitumen void (#000000). "
            "Tactile rough linen, authentic Roberto Ferri, 8k"
        )
    },

    # -------------------------------------------------------------
    # CASA 12 (Piscis · Trascendencia y el Océano del Retorno)
    # -------------------------------------------------------------
    "casa_12_v3_caliz_obsidiana_velo_seda": {
        "folder": "12_Casa_12_Trascendencia_Niebla",
        "width": 768, "height": 1376, "seed": 9123,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred relic study of the 12th Astrological House (House of Transcendence, the Dissolving Veil and Return to Source), strictly no human figures. "
            "On a submerged marble step rests a heavy chalice carved of black obsidian filled with luminescent holy water. "
            "A diaphanous, translucent veil of antique gossamer silk drapes over the edge, floating weightlessly upon motionless dark water. "
            "LIGHTING: Dreamlike, mystical low-key tenebrism with ghostly pale blue-white luminescence against 90% absolute pitch-black bitumen darkness (#000000). "
            "Heavy oil impasto, cracked varnish on linen, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_12_v4_gradas_sumergidas_niebla": {
        "folder": "12_Casa_12_Trascendencia_Niebla",
        "width": 768, "height": 1376, "seed": 9124,
        "prompt": (
            "masterpiece classical fine art oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural study of the 12th Astrological House, strictly no human figures. "
            "Colossal submerged ancient stone staircases descending slowly into a subterranean ocean of still black water blanketed in glowing silver mist. "
            "Cyclopean weathered arches fade progressively into the dense nocturnal fog, vanishing into the infinity of the void. "
            "LIGHTING: Haunting, quiet chiaroscuro with faint moonlight filtering through mist against 90% pitch-black bitumen darkness (#000000). "
            "Tactile oil on rough linen canvas, heavy impasto, authentic Roberto Ferri, 8k"
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
    # Prioridad: Tokens 3, 4, 5, 6 (más frescos), luego 2 y 1
    for i in [3, 4, 5, 6, 2, 1]:
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
                    token_idx += 1
                    attempts += 1
                    if attempts < len(tokens):
                        print(f"  🔄 Probando con token #{token_idx % len(tokens) + 1}...")
                        client = get_client(token_idx)
                    else:
                        break

def main():
    parser = argparse.ArgumentParser(description="Generador de variables v3 y v4 para las 12 Casas.")
    parser.add_argument("--dry-run", action="store_true", help="Solo listar inventario")
    args = parser.parse_args()

    if args.dry_run:
        print(f"📋 DRY-RUN: {len(CATALOG_CASAS_V3_V4)} activos listados:")
        for k, v in CATALOG_CASAS_V3_V4.items():
            print(f" - [{k}] -> {v['folder']}/{k}.webp")
        return

    run_batch(CATALOG_CASAS_V3_V4)

if __name__ == "__main__":
    main()
