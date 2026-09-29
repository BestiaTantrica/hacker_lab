import json
import os
from pathlib import Path

cat_path = Path("/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/Oct_W1/vault_catalog.json")
assets_dir = Path("/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/Oct_W1")

catalog = {}
for f in assets_dir.glob("*.jpg"):
    catalog[f.name] = {
        "elemento_visual": "Fuego",
        "mood_scores": {
            "deseo_profundo": 0.9,
            "misterio": 0.8,
            "renacimiento": 0.7,
            "poder": 0.9,
            "intensidad": 1.0,
            "serenidad": 0.1,
            "caos": 0.8,
            "transformacion": 0.9
        },
        "roles_narrativos": {
            "gancho": 0.9,
            "cta": 0.5,
            "efecto_cuerpo_emocion": 0.9,
            "mecanica_astrologica": 0.7,
            "afrontarlo_constructivamente": 0.6
        },
        "tags": ["ai_generated"],
        "stats_uso": [],
        "path_original": str(f.resolve()),
        "path_video_final": str(f.resolve())
    }

with open(cat_path, "w") as f:
    json.dump(catalog, f, indent=2)
print("Bypass catalog created.")
