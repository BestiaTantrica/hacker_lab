import json
from pathlib import Path

# Fix both possible locations just to be safe
paths = [
    Path("/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/vault_catalog.json"),
    Path("/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/Oct_W1/vault_catalog.json")
]

default_meta = {
  "elemento_visual": "Agua",
  "mood_scores": {"deseo_profundo": 1.0, "misterio": 1.0, "renacimiento": 0.5, "poder": 0.5, "intensidad": 0.8, "serenidad": 0.0, "caos": 0.0, "transformacion": 0.5},
  "roles_narrativos": {"gancho": 1.0, "cta": 1.0, "efecto_cuerpo_emocion": 1.0, "mecanica_astrologica": 1.0, "afrontarlo_constructivamente": 1.0},
  "stats_uso": [],
  "path_video_final": ""
}

images = ["toma1_portal_venus.jpg", "toma2_corazon_latido.jpg", "toma3_agua_profunda.jpg", "toma4_espejo_roto.jpg", "toma5_pergamino_astrologico.jpg"]

for p in paths:
    data = json.loads(p.read_text()) if p.exists() else {}
    for img in images:
        meta = default_meta.copy()
        meta["path_original"] = f"/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/Oct_W1/{img}"
        meta["path_video_final"] = f"/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/Oct_W1/{img}"
        data[img] = meta
    
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))

