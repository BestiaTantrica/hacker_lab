#!/usr/bin/env python3
"""
generar_casas_y_geometria.py
Script de automatización para generar las 12 Casas Astrológicas y Geometría Sagrada/Sigilos
en FLUX.1-dev o API compatible para El Glifo Maestro (Astrology Factory).
"""

import os
import sys
import argparse
import subprocess
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv("/home/LAB/astrology_factory/.env")

VAULT_BASE = Path("/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/Imagenes/Glifo_Maestro")

CASAS_CATALOG = {
    "casa_01_templo_umbral_aurora": {
        "folder": "04_Casas_Astrologicas/01_Casa_1_Identidad_Umbral",
        "width": 768, "height": 1376, "seed": 1001,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural altar study of the 1st Astrological House (House of Identity and Emergence), "
            "strictly no human figures, completely pure fine art. A monumental cyclopean temple threshold of raw dark basalt "
            "and veined antique marble standing at the boundary of existence. A colossal cracked stone portal is partially ajar; "
            "through the narrow vertical opening, a fierce, razor-sharp diagonal beam of golden-rose dawn light strikes across cold "
            "rustic flagstones, casting dramatic raking shadows. Beside the portal sits an ancient bronze brazier with smoldering "
            "sacred embers emitting faint threads of aromatic smoke. Archaic solar and Aries sigils faintly etched into the stone masonry. "
            "LIGHTING: Ruthless chiaroscuro. Single blinding directional dawn beam cutting across dark weathered stone against "
            "90% absolute pitch-black bitumen darkness (#000000). Tactile raw oil on rough linen canvas, heavy impasto brushstrokes, "
            "authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_02_boveda_recursos_oro": {
        "folder": "04_Casas_Astrologicas/02_Casa_2_Recursos_Boveda",
        "width": 768, "height": 1376, "seed": 1002,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural altar study of the 2nd Astrological House (House of Resources, Value and Earthly Substance), "
            "strictly no human figures, completely pure fine art. A subterranean sacred treasury vault built of cyclopean dark green "
            "serpentine stone and slate. On a heavy stone dais rests an open antique hand-forged black iron coffer overflowing with thick "
            "burnished antique gold ingots with centuries of patina, raw emerald crystals, and unpolished copper ore. Next to the coffer, "
            "a massive two-pan balance scale of oxidized bronze rests in absolute equilibrium on cold stone, beside an earthen amphora "
            "filled with golden fossil wheat grains. LIGHTING: Deep chiaroscuro. Warm golden candle glow reflecting off the burnished gold "
            "and polished bronze, casting long rich shadows against 85% impenetrable pitch-black bitumen oil void (#000000). "
            "Tactile raw oil on rough linen canvas, heavy impasto, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_03_galeria_pergaminos_puentes": {
        "folder": "04_Casas_Astrologicas/03_Casa_3_Mente_Biblioteca",
        "width": 768, "height": 1376, "seed": 1003,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural study of the 3rd Astrological House (House of Intellect, Bridges, and Sacred Communication), "
            "strictly no human figures, completely pure fine art. A monumental double-arched renaissance loggia carved of pale grey limestone "
            "suspended over a deep shadowy mist-filled abyss. On ancient stone lecterns and pedestals lie thick rolls of aged vellum scrolls "
            "inscribed with illuminated geometric diagrams, quills of crow feathers, and glass vials of quicksilver mercury. "
            "Outside the stone arcade, two slender stone bridges span across the chasm, leading into the nocturnal unknown. "
            "LIGHTING: Sharp directional quicksilver chiaroscuro. Pale silver-white light glancing across the stone balustrades, parchment, "
            "and arched windows, surrounded by 90% flat pitch-black bitumen darkness (#000000). Tactile raw oil on rough linen canvas, "
            "heavy impasto brushstrokes, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_04_santuario_fuego_ancestral": {
        "folder": "04_Casas_Astrologicas/04_Casa_4_Raiz_Santuario",
        "width": 768, "height": 1376, "seed": 1004,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural altar study of the 4th Astrological House (House of Ancestry, Sanctuary, and the Primordial Hearth), "
            "strictly no human figures, completely pure fine art. An intimate subterranean crypt of ancient limestone masonry. "
            "In the center of a rustic hearth carved into living rock, a sacred eternal fire burns with steady, warm ember-orange flames. "
            "Deep stone niches along the curved wall enshrine weathered marble funerary busts of forgotten forebears covered in pale patina. "
            "In the foreground floor, a calm circular stone basin holds still, mirror-dark sacred water catching the warm flicker of the hearth. "
            "LIGHTING: Warm, protective low-key chiaroscuro. Rich amber and vermilion firelight illuminating the hearth, stone floor, and ancestral niches, "
            "fading softly into 85% absolute pitch-black bitumen oil darkness (#000000). Tactile raw oil on rough linen canvas, heavy impasto brushstrokes, "
            "authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_05_teatro_altar_fuego_creativo": {
        "folder": "04_Casas_Astrologicas/05_Casa_5_Creacion_Teatro",
        "width": 768, "height": 1376, "seed": 1005,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural altar study of the 5th Astrological House (House of Divine Sovereignty, Creative Fire, and Sacred Play), "
            "strictly no human figures, completely pure fine art. A semicircular classical theater proscenium of veined red Verona marble "
            "in majestic ruins. In the center of the elevated stone stage stands a blazing bronze tripodal altar roaring with golden flames. "
            "Resting on a dark crimson velvet ceremonial cushion beside the flames lies a hand-wrought golden laurel crown and an antique "
            "carved scepter of solid gold. Dramatic classical tragedy masks of beaten bronze hang upon the fluted columns. "
            "LIGHTING: Theatrical high-contrast tenebrism. Radiant golden-amber and ruby firelight carving the marble stage and gold crown, "
            "surrounded by 90% impenetrable pitch-black bitumen darkness (#000000). Tactile raw oil on rough linen canvas, heavy impasto, "
            "authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_06_taller_alquimista_botanica": {
        "folder": "04_Casas_Astrologicas/06_Casa_6_Alquimia_Taller",
        "width": 768, "height": 1376, "seed": 1006,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural study of the 6th Astrological House (House of Daily Craft, Sacred Botany, and Somatic Healing), "
            "strictly no human figures, completely pure fine art. A monastic apothecary and alchemical workshop carved of rustic grey granite. "
            "Heavy aged oak worktables lined with rows of dark glass vials containing herbal tinctures, granite mortars holding crushed dried medicinal herbs, "
            "and a polished copper alembic still with condensation drops. Bundles of lavender, sage, and dried chamomile hang drying from rustic stone beams. "
            "An ancient bronze measuring scale stands meticulously calibrated on the table. LIGHTING: Quiet, contemplative chiaroscuro. "
            "Soft directional golden-amber beam from an unseen high stone slit lighting the bottles, copper still, and herb textures, "
            "surrounded by 85% deep pitch-black bitumen void (#000000). Tactile raw oil on rough linen canvas, heavy impasto, "
            "authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_07_templo_alianzas_espejos": {
        "folder": "04_Casas_Astrologicas/07_Casa_7_Alianzas_Espejos",
        "width": 768, "height": 1376, "seed": 1007,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural altar study of the 7th Astrological House (House of Partnership, Sacred Pacts, and the Mirror of the Other), "
            "strictly no human figures, completely pure fine art. A twin peristyle colonnade of fluted Ionic columns carved from translucent white marble "
            "standing upon a vast polished dark marble floor reflecting like still water. Between the paired columns stands an immense circular antique bronze mirror "
            "frame with intricate filigree of paired vines; upon its polished burnished surface, the faint golden-violet glow of a setting sun reflects into the darkness. "
            "A heavy mantle of moss-green velvet lies draped across a stone balustrade. LIGHTING: Exquisite dusk chiaroscuro. Luminous rose-amber and twilight-violet light "
            "grazing the white marble flutes and bronze mirror rim, surrounded by 90% absolute pitch-black bitumen darkness (#000000). "
            "Tactile raw oil on rough linen canvas, heavy impasto, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_08_cripta_transmutacion_crisol": {
        "folder": "04_Casas_Astrologicas/08_Casa_8_Transmutacion_Cripta",
        "width": 768, "height": 1376, "seed": 1008,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural altar study of the 8th Astrological House (House of Radical Transformation, Death, and Alchemical Rebirth), "
            "strictly no human figures, completely pure fine art. An abyssal subterranean crypt constructed of cracked black basalt and mirror-like obsidian slabs. "
            "In the center rests a heavy cast-iron crucible over subterranean volcanic coals, sending up delicate curls of dark aromatic incense smoke and violet sparks. "
            "Resting upon a stone altar plinth beside the crucible is a weathered human skull carved from pale Carrara marble with a living coiled black serpent "
            "resting serenely across its crown. LIGHTING: Extreme dark tenebrism chiaroscuro. Faint incandescent crimson-amber glow from the coals and a cold sliver of "
            "silver moonbeams from a cracked subterranean fissure carving the skull and obsidian edges against 90% flat pitch-black bitumen void (#000000). "
            "Tactile raw oil on rough linen canvas, heavy impasto, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_09_observatorio_armilar_cumbre": {
        "folder": "04_Casas_Astrologicas/09_Casa_9_Filosofia_Observatorio",
        "width": 768, "height": 1376, "seed": 1009,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural altar study of the 9th Astrological House (House of Higher Wisdom, Distant Horizons, and Sacred Philosophy), "
            "strictly no human figures, completely pure fine art. A colossal cyclopean stone terrace perched on the summit of a sheer mountain peak "
            "open directly to the nocturnal cosmos. Dominating the stone platform is a monumental armillary sphere and astrolabe crafted from dark patinated bronze "
            "and interlocking rings of gold, finely engraved with zodiacal coordinates. Beside the instrument stands a carved stone lectern holding an open atlas of "
            "astronomical maps illuminated with gold leaf. LIGHTING: Cold starlight chiaroscuro combined with a warm oil lamp glow on the stone lectern, "
            "casting dramatic long shadows into the abyssal void, surrounded by 85% pitch-black bitumen night (#000000). "
            "Tactile raw oil on rough linen canvas, heavy impasto, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_10_ciudadela_trono_cenit": {
        "folder": "04_Casas_Astrologicas/10_Casa_10_Destino_Ciudadela",
        "width": 768, "height": 1376, "seed": 1010,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural altar study of the 10th Astrological House (House of Zenith, Destiny, and Worldly Sovereign Authority), "
            "strictly no human figures, completely pure fine art. A cyclopean megalithic citadel of polished black basalt at the highest zenith. "
            "A monumental flight of sheer stone steps leads upward to an austere throne carved directly into the living mountain bedrock. "
            "Upon the stone seat rests a heavy carved imperial orb of lapis lazuli and an antique iron rod of governance with a gold capstone. "
            "Astrological sigils of Saturn and Capricorn chiseled deeply into the stepped stone. LIGHTING: Spectacular perpendicular zenith chiaroscuro. "
            "A solitary vertical shaft of divine white-gold light falls from directly above, striking the throne and cascading down the stone steps, "
            "surrounded by 90% impenetrable pitch-black bitumen darkness (#000000). Tactile raw oil on rough linen canvas, heavy impasto, "
            "authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_11_agora_mecanismo_cosmico": {
        "folder": "04_Casas_Astrologicas/11_Casa_11_Vision_Agora",
        "width": 768, "height": 1376, "seed": 1011,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural study of the 11th Astrological House (House of Collective Vision, Future Ideals, and the Sacred Agora), "
            "strictly no human figures, completely pure fine art. A roofless circular forum enclosed by slender fluted columns of grey volcanic stone "
            "open to an expanse of nocturnal constellations. In the center of the ring of stone seating sits a monumental circular table of dark porphyry; "
            "hovering or mounted precisely in its center is an intricate mechanical orrery of the cosmos made of platinum gears and glowing crystal orbs "
            "representing universal fellowship. LIGHTING: Ethereal silver-electric chiaroscuro. Distant star clusters cast a crystalline cool rim light over "
            "the columns and orrery gears against 90% absolute pitch-black bitumen oil darkness (#000000). Tactile raw oil on rough linen canvas, "
            "heavy impasto, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "casa_12_santuario_niebla_aguas_silencio": {
        "folder": "04_Casas_Astrologicas/12_Casa_12_Trascendencia_Niebla",
        "width": 768, "height": 1376, "seed": 1012,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred architectural altar study of the 12th Astrological House (House of Sacred Isolation, the Oceanic Subconscious, and Mystical Dissolution), "
            "strictly no human figures, completely pure fine art. A partially submerged classical sanctuary of pale limestone columns rising out of still, glassy, "
            "mirror-black nocturnal waters. Soft ribbons of cold subterranean mist roll lazily across the water surface and envelop the bases of the stone arches. "
            "Floating upon the dark water are large bronze votive braziers whose gentle amber flames cast shimmering liquid caustic reflections onto the half-drowned "
            "stone carvings. LIGHTING: Dreamlike, dissolved low-key chiaroscuro. Pale silver mist and trembling warm amber candlelight reflecting on black water "
            "against 90% impenetrable pitch-black bitumen void (#000000). Tactile raw oil on rough linen canvas, heavy impasto brushstrokes, "
            "authentic Roberto Ferri museum masterpiece, 8k"
        )
    }
}

GEOMETRIA_CATALOG = {
    "aspecto_01_conjuncion_fusion_oro": {
        "folder": "03_Geometria_y_Sigilos/01_Aspectos_Astrologicos",
        "width": 1024, "height": 1024, "seed": 2001,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, 1:1 square composition. "
            "Sacred geometric study of the Astrological Conjunction (0 degrees), strictly no human figures, completely pure fine art. "
            "Two monumental spherical discs of heavy burnished antique gold and molten brass merging perfectly at their center like a sacred solar eclipse. "
            "Thin tendrils of liquid gold bridge the perimeter of the two overlapping circles, emitting a concentrated radiant warm amber glow. "
            "Surrounding the perimeter are delicate engraved degrees in antique Latin calligraphy on dark basalt flagstones. "
            "LIGHTING: Intense concentrated chiaroscuro radiating from the union point against 90% absolute pitch-black bitumen void (#000000). "
            "Heavy impasto, cracked oil glaze on linen, 8k"
        )
    },
    "aspecto_02_oposicion_polaridad_tension": {
        "folder": "03_Geometria_y_Sigilos/01_Aspectos_Astrologicos",
        "width": 768, "height": 1376, "seed": 2002,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, 9:16 vertical composition. "
            "Sacred geometric study of the Astrological Opposition (180 degrees), strictly no human figures, completely pure fine art. "
            "Two massive celestial orbs positioned at opposite poles of the frame: the upper orb forged of cool selenita silver emitting blue-silver light, "
            "the lower orb forged of volcanic basalt and molten gold emitting warm amber light. Connecting the two opposing poles is a razor-thin, "
            "vibrating golden cord of taut tension stretched straight across the void. Faint alchemical sigils etched along the axis line. "
            "LIGHTING: Bipolar chiaroscuro against 90% flat pitch-black bitumen darkness (#000000). "
            "Tactile raw oil on rough linen canvas, heavy impasto, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "aspecto_03_trigono_triangulo_aureo": {
        "folder": "03_Geometria_y_Sigilos/01_Aspectos_Astrologicos",
        "width": 1024, "height": 1024, "seed": 2003,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, 1:1 square composition. "
            "Sacred geometric study of the Astrological Trine (120 degrees), strictly no human figures, completely pure fine art. "
            "An equilateral triangle crafted of heavy cast bronze and gold leaf levitating gracefully in the void. "
            "At each of the three vertices rests a polished alchemical sphere (ruby fire, sapphire water, emerald earth). "
            "Fluid, continuous golden light threads circulate smoothly through the three edges in effortless perpetual flow. "
            "LIGHTING: Harmonious warm golden chiaroscuro illuminating the bronze facets against 90% pitch-black bitumen oil void (#000000). "
            "Heavy impasto brushstrokes, cracked glaze on linen, 8k"
        )
    },
    "aspecto_04_cuadratura_cruz_piedra": {
        "folder": "03_Geometria_y_Sigilos/01_Aspectos_Astrologicos",
        "width": 1024, "height": 1024, "seed": 2004,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, 1:1 square composition. "
            "Sacred geometric study of the Astrological Square (90 degrees), strictly no human figures, completely pure fine art. "
            "A monumental square foundation plinth and orthogonal cross carved of rough, fractured black basalt. "
            "At the sharp 90-degree right angle vertex, a seam of red-hot glowing steel is forged under pressure, releasing tiny sparks of orange embers into the dark. "
            "Chiseled Roman numerals and astrological degree markings along the stone edges. "
            "LIGHTING: Dramatic high-friction chiaroscuro with fiery orange embers cutting across the stone against 90% impenetrable pitch-black bitumen void (#000000). "
            "Heavy impasto, authentic Roberto Ferri, 8k"
        )
    },
    "aspecto_05_sextil_estrella_armonica": {
        "folder": "03_Geometria_y_Sigilos/01_Aspectos_Astrologicos",
        "width": 1024, "height": 1024, "seed": 2005,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, 1:1 square composition. "
            "Sacred geometric study of the Astrological Sextile (60 degrees), strictly no human figures, completely pure fine art. "
            "An intricate hexagram structure forged of slender oxidized platinum and lapis lazuli inlays, forming a precise 60-degree interlocking sacred geometry. "
            "Fine crystalline prisms at the joints refract delicate needle-thin rays of pale silver-white light into the dark space. "
            "LIGHTING: Razor-sharp silver and cyan rim lighting against 90% flat pitch-black bitumen oil darkness (#000000). "
            "Tactile oil on rough linen canvas, heavy impasto, 8k"
        )
    },
    "aspecto_06_quincuncio_ajuste_alquimico": {
        "folder": "03_Geometria_y_Sigilos/01_Aspectos_Astrologicos",
        "width": 768, "height": 1376, "seed": 2006,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, 9:16 vertical composition. "
            "Sacred geometric study of the Astrological Inconjunct / Quincunx (150 degrees), strictly no human figures, completely pure fine art. "
            "An asymmetrical helical geometric apparatus made of darkened antique bronze and blown apothecary glass. "
            "A 150-degree oblique golden rod connects two non-aligned stone plinths across the dark void, with a drop of liquid quicksilver suspended in mid-air "
            "along the subtle tension line. LIGHTING: Deep tenebrism with amber highlights tracing the oblique angle against 90% absolute pitch-black bitumen void (#000000). "
            "Heavy impasto, authentic Roberto Ferri, 8k"
        )
    },
    "mandala_01_rueda_zodiacal_oro_basalto": {
        "folder": "03_Geometria_y_Sigilos/02_Mandalas_y_Rueda_Zodiacal",
        "width": 1024, "height": 1024, "seed": 2007,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, 1:1 square composition. "
            "Sacred monumental mandala study of the Astrological Zodiac Wheel, strictly no human figures, completely pure fine art. "
            "A massive circular disc of mirror-polished black basalt carved with twelve precise triangular segments. "
            "Inlaid into the stone are deep relief glyphs of the 12 zodiac signs crafted of molten antique gold leaf and aged silver with delicate natural fissures. "
            "The central hub features the four cardinal points (ASC, IC, DSC, MC) joined by an alchemical cross. "
            "LIGHTING: Low-angle dramatic golden raking light revealing the chiseled stone relief and glittering gold leaf against 90% flat pitch-black bitumen oil darkness (#000000). "
            "Tactile raw oil on rough linen canvas, heavy impasto, authentic museum masterpiece, 8k"
        )
    },
    "mandala_02_carta_natal_vacia": {
        "folder": "03_Geometria_y_Sigilos/02_Mandalas_y_Rueda_Zodiacal",
        "width": 768, "height": 1376, "seed": 2008,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, vertical 9:16 composition. "
            "Sacred cartographic study of the Empty Natal Chart Matrix, strictly no human figures, completely pure fine art. "
            "An archaic cosmological map engraved onto a slab of dark grey slate stone. The twelve curved astrological houses are chiseled in deep sunken relief, "
            "with circular rings indicating planetary orbits and concentric degree rings etched in fine pale gold dust. "
            "The four angles (Ascendant, Descendant, Midheaven, Imum Coeli) stand out as raised ridges of burnished bronze. "
            "LIGHTING: Piercing diagonal shaft of warm amber chiaroscuro light crossing the chart surface, surrounded by 85% pitch-black bitumen void (#000000). "
            "Heavy impasto, cracked oil glaze on linen canvas, authentic Roberto Ferri, 8k"
        )
    },
    "elemento_01_fuego_tetraedro": {
        "folder": "03_Geometria_y_Sigilos/03_Elementos_y_Solidos_Platonicos",
        "width": 1024, "height": 1024, "seed": 3001,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, 1:1 square composition. "
            "Sacred geometric study of the Fire Element as the Platonic Tetrahedron, strictly no human figures, completely pure fine art. "
            "A regular tetrahedron forged of glowing red-hot gold and hammered brass levitating over a dark stone altar. "
            "Inside the translucent geometric facets burns a living sacred flame of golden-orange plasma, casting intense amber reflections "
            "onto cold dark basalt flagstones. LIGHTING: Concentrated firelight chiaroscuro against 90% absolute pitch-black bitumen oil void (#000000). "
            "Heavy impasto, cracked oil glaze on linen canvas, authentic Roberto Ferri museum masterpiece, 8k"
        )
    },
    "elemento_02_tierra_cubo": {
        "folder": "03_Geometria_y_Sigilos/03_Elementos_y_Solidos_Platonicos",
        "width": 1024, "height": 1024, "seed": 3002,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, 1:1 square composition. "
            "Sacred geometric study of the Earth Element as the Platonic Hexahedron (Cube), strictly no human figures, completely pure fine art. "
            "A colossal monolithic cube carved of polished dark green serpentine stone and veins of raw malachite, resting firmly upon ancient bedrock. "
            "Fine alchemical fissures run through the edges with roots of fossilized stone and gold leaf creeping into the cracks. "
            "LIGHTING: Deep directional amber-gold raking light carving the cubic facets against 90% flat pitch-black bitumen darkness (#000000). "
            "Tactile raw oil on rough linen canvas, heavy impasto, authentic Roberto Ferri, 8k"
        )
    },
    "elemento_03_aire_octaedro": {
        "folder": "03_Geometria_y_Sigilos/03_Elementos_y_Solidos_Platonicos",
        "width": 1024, "height": 1024, "seed": 3003,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, 1:1 square composition. "
            "Sacred geometric study of the Air Element as the Platonic Octahedron, strictly no human figures, completely pure fine art. "
            "An elegant eight-sided regular octahedron crafted of slender oxidized platinum filigree and transparent blue-sapphire crystal "
            "hovering effortlessly in the void. Inside the facets swirls a luminous vapor of silver wind and morning mist. "
            "LIGHTING: Ethereal silver-white and cyan rim lighting tracing the platinum edges against 90% absolute pitch-black bitumen darkness (#000000). "
            "Heavy impasto, authentic Roberto Ferri, 8k"
        )
    },
    "elemento_04_agua_icosaedro": {
        "folder": "03_Geometria_y_Sigilos/03_Elementos_y_Solidos_Platonicos",
        "width": 1024, "height": 1024, "seed": 3004,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, 1:1 square composition. "
            "Sacred geometric study of the Water Element as the Platonic Icosahedron, strictly no human figures, completely pure fine art. "
            "A twenty-faceted regular icosahedron sculpted of pale translucent moon-selenita stone and mother-of-pearl. "
            "Across its gleaming facets cling glistening dew drops and ribbons of still, mirror-dark water that drip slowly into the void. "
            "LIGHTING: Cold lunar-silver chiaroscuro with liquid caustic reflections against 90% flat pitch-black bitumen oil darkness (#000000). "
            "Tactile raw oil on rough linen canvas, heavy impasto, 8k"
        )
    },
    "elemento_05_eter_dodecaedro": {
        "folder": "03_Geometria_y_Sigilos/03_Elementos_y_Solidos_Platonicos",
        "width": 1024, "height": 1024, "seed": 3005,
        "prompt": (
            "masterpiece classical oil painting by Roberto Ferri, 1:1 square composition. "
            "Sacred geometric study of the Quintessence / Aether Element as the Platonic Dodecahedron, strictly no human figures, completely pure fine art. "
            "A twelve-sided regular dodecahedron forged of pure rock crystal and celestial gold filigree. "
            "Trapped within the crystalline dodecahedron is a miniature glowing stellar nebula with spinning cosmic dust and golden star points. "
            "LIGHTING: Spectacular cosmic chiaroscuro radiating outward from the dodecahedron against 90% absolute pitch-black bitumen void (#000000). "
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
    # Prioridad: HF_TOKEN_1 a HF_TOKEN_6, luego HF_TOKEN
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
        print("❌ Error: gradio_client no está instalado en este entorno.")
        return

    tokens = get_tokens_pool()
    if not tokens:
        print("❌ Error: No se encontraron tokens HF_TOKEN en el entorno.")
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
                if "ZeroGPU runs limit" in err_str or "exceeded" in err_str.lower():
                    token_idx += 1
                    attempts += 1
                    if attempts < len(tokens):
                        print(f"  🔄 Rotando a token #{token_idx % len(tokens) + 1}...")
                        client = get_client(token_idx)
                    else:
                        print("  ❌ Todos los tokens han agotado su cuota de ZeroGPU.")
                else:
                    print(f"  ❌ Error irrecuperable en {name}: {e}")
                    break

def main():
    parser = argparse.ArgumentParser(description="Generador automatizado de Casas y Geometría Sagrada.")
    parser.add_argument("--block", choices=["casas", "geometria", "all"], default="all")
    parser.add_argument("--dry-run", action="store_true", help="Solo imprimir inventario y prompts")
    args = parser.parse_args()

    selected_catalog = {}
    if args.block in ["casas", "all"]:
        selected_catalog.update(CASAS_CATALOG)
    if args.block in ["geometria", "all"]:
        selected_catalog.update(GEOMETRIA_CATALOG)

    if args.dry_run:
        print(f"📋 DRY-RUN: {len(selected_catalog)} activos listados:")
        for k, v in selected_catalog.items():
            print(f" - [{k}] -> {v['folder']}/{k}.webp")
        return

    run_batch(selected_catalog)

if __name__ == "__main__":
    main()
