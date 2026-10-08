import json

def build_volume_expression(timeline_path):
    with open(timeline_path) as f:
        data = json.load(f)
    tomas = data.get("tomas", [])
    expr_parts = []
    for t in tomas:
        rol = t.get("rol", "")
        start = t.get("inicio_ms", 0) / 1000.0
        end = t.get("fin_ms", 0) / 1000.0
        
        # Determine volume based on role
        if rol in ["gancho", "mecanica_astrologica", "tension_oportunidad", "climax", "transitos_principales"]:
            vol = 0.65
        else:
            vol = 0.25
            
        expr_parts.append(f"if(between(t,{start},{end}), {vol}, 0)")
        
    full_expr = " + ".join(expr_parts)
    if not full_expr:
        full_expr = "0.4"
    return full_expr

print(build_volume_expression("/home/tomas2/MediaContingencia/Privada/Astrology_Vault/timeline_huecos/luna_sagitario_oct04.json"))
