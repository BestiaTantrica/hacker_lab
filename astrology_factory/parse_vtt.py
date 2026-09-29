import json
import re

def time_to_ms(t_str):
    h, m, s_ms = t_str.split(':')
    s, ms = s_ms.split(',')
    return int(h)*3600000 + int(m)*60000 + int(s)*1000 + int(ms)

def parse_vtt(vtt_file):
    subs = []
    with open(vtt_file) as f:
        lines = f.read().splitlines()
    
    current_sub = {}
    for line in lines:
        if '-->' in line:
            start, end = line.split(' --> ')
            current_sub['start_ms'] = time_to_ms(start)
            current_sub['end_ms'] = time_to_ms(end)
        elif line.strip() and not line.strip().isdigit() and 'WEBVTT' not in line:
            current_sub['text'] = line.strip()
            subs.append(current_sub)
            current_sub = {}
    return subs

def match_tomas(guion_file, vtt_file):
    with open(guion_file) as f:
        guion = json.load(f)
    tomas = guion['tomas']
    subs = parse_vtt(vtt_file)
    
    toma_idx = 0
    toma_chars_needed = len(re.sub(r'\s+', '', tomas[toma_idx]['texto']))
    toma_chars_found = 0
    
    toma_start_ms = subs[0]['start_ms']
    
    results = []
    
    for sub in subs:
        sub_chars = len(re.sub(r'\s+', '', sub['text']))
        toma_chars_found += sub_chars
        
        if toma_chars_found >= toma_chars_needed - 2: # tolerance
            results.append({
                'num': tomas[toma_idx]['num'],
                'texto': tomas[toma_idx]['texto'],
                'start_ms': toma_start_ms,
                'end_ms': sub['end_ms'],
                'duracion_ms': sub['end_ms'] - toma_start_ms
            })
            toma_idx += 1
            if toma_idx < len(tomas):
                toma_chars_needed = len(re.sub(r'\s+', '', tomas[toma_idx]['texto']))
                toma_chars_found = 0
                toma_start_ms = sub['end_ms'] # the next toma starts right where this one ends (or at the next subtitle's start?)
                # Wait, better to set toma_start_ms to the start_ms of the next subtitle, but if there's silence, maybe keep it continuous?
                # Continuous is better for no gaps. Let's set it to sub['end_ms'] or the next sub's start_ms. Let's just print.
                
    print(json.dumps(results, indent=2))

match_tomas('/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Guiones/guion_resaca_eclipse_oct03.json', 'test.vtt')
