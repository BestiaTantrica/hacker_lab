#!/usr/bin/env python3
"""
🌔 GENERADOR BINAURAL REAL
Usa matemáticas puras (numpy/scipy) para generar frecuencias sanadoras auténticas.
Genera WAVs con diferencia de fase exacta entre canal L y R.
"""

import argparse
import numpy as np
from scipy.io import wavfile
from pathlib import Path
import sys

def generar_binaural(base_freq: float, beat_freq: float, duration: float, sample_rate: int = 44100, volume: float = 0.5):
    """
    Genera un audio binaural.
    Canal Izquierdo = base_freq - (beat_freq / 2)
    Canal Derecho = base_freq + (beat_freq / 2)
    """
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Frecuencias para L y R
    freq_l = base_freq - (beat_freq / 2.0)
    freq_r = base_freq + (beat_freq / 2.0)
    
    # Ondas sinusoidales puras
    wave_l = np.sin(2 * np.pi * freq_l * t)
    wave_r = np.sin(2 * np.pi * freq_r * t)
    
    # Modulación sutil de amplitud (pulsación lenta) para hacerlo más orgánico
    mod_l = 0.8 + 0.2 * np.sin(2 * np.pi * 0.05 * t)
    mod_r = 0.8 + 0.2 * np.sin(2 * np.pi * 0.05 * t + np.pi)
    
    wave_l = wave_l * mod_l * volume
    wave_r = wave_r * mod_r * volume
    
    # Fade in/out de 4 segundos para evitar clics
    fade_len = int(sample_rate * 4.0)
    if fade_len > len(t) / 2:
        fade_len = int(len(t) / 2)
        
    fade_in = np.linspace(0, 1, fade_len)
    fade_out = np.linspace(1, 0, fade_len)
    
    wave_l[:fade_len] *= fade_in
    wave_r[:fade_len] *= fade_in
    wave_l[-fade_len:] *= fade_out
    wave_r[-fade_len:] *= fade_out
    
    # Combinar en estéreo
    audio = np.vstack((wave_l, wave_r)).T
    
    # Convertir a 16-bit PCM
    audio_16 = np.int16(audio * 32767)
    return audio_16

def generar_sfx_transicion(elemento: str, duration: float = 3.0, sample_rate: int = 44100, volume: float = 0.5):
    """
    Genera un SFX orgánico para transiciones basado en el elemento.
    """
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    if elemento == "fuego":
        # Ruido marrón filtrado + resonancia cálida
        noise = np.random.normal(0, 1, len(t))
        # Filtro pasabajos crudo
        b = np.exp(-t * 10)
        noise = np.convolve(noise, b, mode='same') * 0.1
        tone = np.sin(2 * np.pi * 128 * t) * np.exp(-t * 2)
        wave = (noise + tone) * volume
    elif elemento == "agua":
        # Ruido rosa + modulación
        noise = np.random.normal(0, 1, len(t))
        wave = noise * np.sin(2 * np.pi * 2 * t) * np.exp(-t) * volume * 0.2
        tone = np.sin(2 * np.pi * 432 * t) * np.exp(-t * 1.5) * 0.5
        wave += tone * volume
    elif elemento == "tierra":
        # Frecuencia muy grave (drone)
        wave = np.sin(2 * np.pi * 54 * t) * np.exp(-t * 0.5) * volume
        wave += np.sin(2 * np.pi * 108 * t) * np.exp(-t) * volume * 0.5
    else: # Aire
        # Ruido blanco filtrado muy agudo (whoosh)
        noise = np.random.normal(0, 1, len(t))
        env = np.sin(np.pi * t / duration)
        wave = noise * env * volume * 0.1
        tone = np.sin(2 * np.pi * 852 * t) * env * 0.3
        wave += tone * volume
        
    # Aplicar fades
    fade_len = int(sample_rate * 0.5)
    if fade_len > len(t) / 2:
        fade_len = int(len(t) / 2)
    
    fade_in = np.linspace(0, 1, fade_len)
    fade_out = np.linspace(1, 0, fade_len)
    
    wave[:fade_len] *= fade_in
    wave[-fade_len:] *= fade_out
    
    # Mono a Stereo
    audio = np.vstack((wave, wave)).T
    
    # Normalizar para evitar recortes, pero mantener el volumen relativo
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val * volume
        
    audio_16 = np.int16(audio * 32767)
    return audio_16

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tipo", choices=["binaural", "sfx"], required=True)
    parser.add_argument("--salida", required=True)
    parser.add_argument("--duracion", type=float, required=True)
    parser.add_argument("--freq", type=float, default=528)
    parser.add_argument("--beat", type=float, default=7.0) # Frecuencia Theta
    parser.add_argument("--elemento", type=str, default="aire")
    parser.add_argument("--volumen", type=float, default=0.5)
    args = parser.parse_args()
    
    if args.tipo == "binaural":
        audio = generar_binaural(args.freq, args.beat, args.duracion, volume=args.volumen)
    else:
        audio = generar_sfx_transicion(args.elemento, args.duracion, volume=args.volumen)
        
    wavfile.write(args.salida, 44100, audio)
    print(f"✅ Audio {args.tipo} generado en {args.salida}")

if __name__ == "__main__":
    main()
