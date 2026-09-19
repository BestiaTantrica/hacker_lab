"""
audio_generator.py
──────────────────
Genera locución con Edge-TTS.
La generación de subtítulos (.srt) fue delegada a subtitle_generator.py
(Whisper local) para garantizar sincronización perfecta con FFmpeg.
"""

import asyncio
import edge_tts
import os


class AudioGenerator:
    def __init__(self, voice: str = "es-AR-TomasNeural"):
        # Voces en español recomendadas:
        #   es-MX-JorgeNeural  — masculina, México, muy natural
        #   es-ES-AlvaroNeural — masculina, España
        #   es-AR-TomasNeural  — masculina, Argentina (si disponible)
        self.voice = voice

    async def _generate_audio_async(self, text: str, output_filepath: str):
        # +20% velocidad → ideal para TikTok/Reels
        communicate = edge_tts.Communicate(text, self.voice, rate="+20%")

        with open(output_filepath, "wb") as audio_file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_file.write(chunk["data"])
                # NOTE: Los chunks de WordBoundary/SentenceBoundary de Edge-TTS
                # fueron eliminados. El SRT se genera con Whisper (subtitle_generator.py)
                # para garantizar sincronización real con el audio.

    def generate_audio(self, text: str, output_filepath: str):
        """
        Genera el MP3 con Edge-TTS.
        El .srt se genera por separado con subtitle_generator.generate_srt().
        """
        print(f"🎙️  Generando locución → {output_filepath}")
        asyncio.run(self._generate_audio_async(text, output_filepath))
        print(f"✅ Audio listo: {os.path.basename(output_filepath)}")


if __name__ == "__main__":
    generator = AudioGenerator("es-MX-JorgeNeural")
    test_text = (
        "Bienvenidos a la fábrica de horóscopos. "
        "El universo no te debe nada, pero aquí te lo explicamos igual."
    )
    generator.generate_audio(test_text, "prueba_locucion.mp3")
    print("Prueba completada. Archivo guardado como prueba_locucion.mp3")
