import os

base_dir = "produccion"
short_cta = "Calculá el impacto de este tránsito en tu carta natal en el link."

for root, dirs, files in os.walk(base_dir):
    if "guion.txt" in files and "Resumen" not in root:
        guion_path = os.path.join(root, "guion.txt")
        with open(guion_path, "r", encoding="utf-8") as f:
            lines = f.read().strip().split('\n')
            
        if len(lines) > 0:
            last_line = lines[-1].lower()
            if "link" in last_line and short_cta.lower() not in last_line.lower():
                lines[-1] = short_cta
            elif "link" not in last_line:
                lines.append(short_cta)
                
        with open(guion_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
            
print("CTA estandarizado en todos los guiones.")
