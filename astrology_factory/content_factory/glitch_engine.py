import os
import subprocess
import random
import json

class GlitchEngine:
    def __init__(self, prod_dir: str):
        self.prod_dir = prod_dir
        self.assets_dir = os.path.join(prod_dir, "assets")
        self.glitch_dir = os.path.join(self.assets_dir, "glitches")
        os.makedirs(self.glitch_dir, exist_ok=True)
        
        # Cargar paletas astrológicas
        db_path = os.path.join(os.path.dirname(__file__), "astrology_palettes.json")
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                self.palettes = json.load(f)
        else:
            self.palettes = {}

    def apply_glitch_fx(self, input_file: str, aspect_type: str, out_name: str) -> str:
        """
        Aplica un filtro FFmpeg en base al tipo de aspecto astrológico.
        aspect_type: 'cuadratura', 'oposicion', 'trigono', 'conjuncion', 'sextil'
        """
        output_file = os.path.join(self.glitch_dir, out_name)
        
        # Extraer configuración de la base de datos
        aspect = aspect_type.lower()
        if aspect in self.palettes:
            vf = self.palettes[aspect]["glitch_vf"]
            duration_str = str(self.palettes[aspect]["glitch_duration"])
        else:
            vf = "eq=saturation=2.0"
            duration_str = "0.1"

        if input_file.endswith(('.jpg', '.png')):
            cmd = [
                "ffmpeg", "-y", "-loop", "1", "-i", input_file,
                "-vf", vf, "-t", duration_str, "-pix_fmt", "yuv420p", output_file
            ]
        else:
            # Si es video, extraemos un pedazo al azar
            cmd = [
                "ffmpeg", "-y", "-i", input_file,
                "-vf", vf, "-t", duration_str, "-pix_fmt", "yuv420p", output_file
            ]

        try:
            subprocess.run(cmd, capture_output=True, check=True)
            return output_file
        except subprocess.CalledProcessError as e:
            print(f"Error generando glitch para {input_file}: {e}")
            return ""

    def generate_stutter_sequence(self, broken_assets: list[str], aspect_type: str, seq_id: int) -> str:
        """
        Toma una lista de assets 'rotos', les aplica FX y los une en una micro-secuencia GIF de 0.3s - 0.5s.
        """
        if not broken_assets:
            return ""
            
        glitched_clips = []
        for i, asset in enumerate(broken_assets[:5]): # Max 5 frames
            out_name = f"glitch_frame_{seq_id}_{i}.mp4"
            clip = self.apply_glitch_fx(asset, aspect_type, out_name)
            if clip:
                glitched_clips.append(clip)
                
        if not glitched_clips:
            return ""

        # Concatenar
        list_file = os.path.join(self.glitch_dir, f"concat_list_{seq_id}.txt")
        with open(list_file, "w") as f:
            for clip in glitched_clips:
                f.write(f"file '{clip}'\n")

        final_seq = os.path.join(self.glitch_dir, f"sequence_{seq_id}.mp4")
        cmd_concat = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file,
            "-c", "copy", final_seq
        ]
        
        try:
            subprocess.run(cmd_concat, capture_output=True, check=True)
            return final_seq
        except subprocess.CalledProcessError as e:
            print(f"Error concatenando secuencia glitch {seq_id}: {e}")
            return ""
