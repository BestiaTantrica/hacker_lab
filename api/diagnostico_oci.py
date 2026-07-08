#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diagnostico_oci.py — Panel de control y diagnóstico para el Nodo OCI.
Permite verificar el estado del servidor, optimizar memoria, actualizar objetivos 
y ejecutar pruebas de descubrimiento pasivo desde la terminal local.
"""

import os
import sys
import subprocess
import argparse

# Configuración de conexión OCI
KEY_PATH = "/home/tomas2/WORKSPACE/tomas2/.ssh/id_rsa"
SERVER_IP = "129.80.73.248"
SSH_USER = "ubuntu"

# Estilos de consola (ANSI Colors)
C_BLUE = "\033[36m"
C_GREEN = "\033[32m"
C_YELLOW = "\033[33m"
C_RED = "\033[31m"
C_MAGENTA = "\033[35m"
C_BOLD = "\033[1m"
C_RESET = "\033[0m"

def print_banner():
    print(f"{C_BLUE}{C_BOLD}" + "=" * 65)
    print("  🛰️  SISTEMA DE CONTROL Y DIAGNÓSTICO DEL NODO OCI")
    print("  Director Técnico Lab - Ciberseguridad & Bug Bounty")
    print("=" * 65 + f"{C_RESET}\n")

def ejecutar_ssh(comando_remoto):
    """Ejecuta un comando en el servidor OCI via SSH."""
    cmd = [
        "ssh",
        "-F", "/dev/null",  # Ignorar configs rotas del sandbox
        "-i", KEY_PATH,
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=8",
        f"{SSH_USER}@{SERVER_IP}",
        comando_remoto
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        return res.returncode, res.stdout, res.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT: La conexión excedió el límite de tiempo."
    except Exception as e:
        return -2, "", f"EXCEPCIÓN LOCAL: {str(e)}"

def diagnosticar():
    print(f"{C_BOLD}🔌 Conectando con {SSH_USER}@{SERVER_IP}...{C_RESET}")
    
    # Comando consolidado para obtener información en un solo viaje SSH
    comando_consolidado = (
        "echo '---MEMORIA---' && free -h && "
        "echo '---CARGA---' && uptime && "
        "echo '---PROCESOS---' && ps aux | grep -E 'python|discovery|comparador' | grep -v grep || echo 'Ninguno' && "
        "echo '---CRON---' && crontab -l 2>/dev/null || echo 'Sin cron' && "
        "echo '---OBJETIVOS---' && cat ~/plataforma_operativa/config/objetivos.txt 2>/dev/null || echo 'No existe' && "
        "echo '---LOGS---' && ls -lh ~/plataforma_operativa/logs/ 2>/dev/null || echo 'Vacio' && "
        "echo '---RESULTADOS---' && ls -lh ~/plataforma_operativa/resultados/ 2>/dev/null || echo 'Vacio'"
    )
    
    code, stdout, stderr = ejecutar_ssh(comando_consolidado)
    if code != 0:
        print(f"{C_RED}[ERROR] No se pudo conectar o ejecutar en el servidor OCI.{C_RESET}")
        print(f"Detalle: {stderr}")
        sys.exit(1)
        
    secciones = stdout.split("---")
    datos = {}
    
    for sec in secciones:
        if not sec.strip():
            continue
        lineas = sec.strip().split("\n")
        titulo = lineas[0].strip()
        contenido = "\n".join(lineas[1:])
        datos[titulo] = contenido
        
    # --- RENDERIZADO DE RESULTADOS ---
    print_banner()
    
    # 1. Estado de Recursos
    print(f"{C_BOLD}📊 ESTADO DE MEMORIA & RECURSOS (free -h){C_RESET}")
    print("-" * 50)
    print(datos.get("MEMORIA", f"{C_RED}No se obtuvo información de memoria.{C_RESET}"))
    print()
    
    # 2. Carga y Uptime
    print(f"{C_BOLD}⚡ CARGA DEL SISTEMA & UPTIME{C_RESET}")
    print("-" * 50)
    print(datos.get("CARGA", "No disponible").strip())
    print()
    
    # 3. Procesos Activos
    print(f"{C_BOLD}🐍 PROCESOS DE MONITOREO ACTIVOS{C_RESET}")
    print("-" * 50)
    procesos = datos.get("PROCESOS", "Ninguno").strip()
    if procesos == "Ninguno" or not procesos:
        print(f"{C_GREEN}No hay scripts de monitoreo corriendo en este momento (Ideal para evitar consumo).{C_RESET}")
    else:
        print(f"{C_YELLOW}{procesos}{C_RESET}")
    print()
    
    # 4. Configuración Cron
    print(f"{C_BOLD}⏰ PLANIFICADOR CRON (crontab -l){C_RESET}")
    print("-" * 50)
    cron = datos.get("CRON", "Sin cron").strip()
    if "run_pipeline" in cron:
        print(f"{C_GREEN}✅ Automatización activa:{C_RESET}\n{cron}")
    else:
        print(f"{C_RED}⚠️ No se detectó la automatización de run_pipeline.sh en el cron.{C_RESET}")
        print(f"Contenido crudo del cron:\n{cron}")
    print()
    
    # 5. Objetivos
    print(f"{C_BOLD}🎯 OBJETIVOS MONITOREADOS (config/objetivos.txt){C_RESET}")
    print("-" * 50)
    objetivos = datos.get("OBJETIVOS", "").strip()
    if objetivos == "No existe" or not objetivos:
        print(f"{C_RED}⚠️ El archivo objetivos.txt no existe o está vacío.{C_RESET}")
    else:
        lista_obj = [o.strip() for o in objetivos.split("\n") if o.strip()]
        for idx, obj in enumerate(lista_obj, 1):
            color = C_GREEN if "mongodb" in obj else C_YELLOW
            print(f"  {idx}. {color}{obj}{C_RESET}")
        if "mongodb.com" not in objetivos:
            print(f"\n{C_RED}❌ CRÍTICO: 'mongodb.com' NO está siendo monitoreado.{C_RESET}")
            print(f"Por eso no te han llegado alertas de MongoDB. Usa el parámetro --add-targets para agregarlo.")
    print()

    # 6. Estructura de Salida
    print(f"{C_BOLD}📁 ARCHIVOS DE LOGS Y RESULTADOS{C_RESET}")
    print("-" * 50)
    print(f"{C_BLUE}[LOGS]:{C_RESET}")
    print(datos.get("LOGS", "Vacío").strip())
    print(f"\n{C_BLUE}[RESULTADOS]:{C_RESET}")
    print(datos.get("RESULTADOS", "Vacío").strip())
    print()

def actualizar_objetivos(targets_raw):
    nuevos = [t.strip().lower() for t in targets_raw.split(",") if t.strip()]
    if not nuevos:
        print(f"{C_RED}[ERROR] Lista de objetivos vacía.{C_RESET}")
        return
        
    print(f"{C_BOLD}🔄 Leyendo objetivos actuales en el servidor...{C_RESET}")
    code, stdout, stderr = ejecutar_ssh("cat ~/plataforma_operativa/config/objetivos.txt 2>/dev/null || echo ''")
    
    actuales = [line.strip().lower() for line in stdout.split("\n") if line.strip()]
    
    original_len = len(actuales)
    agregados = []
    for n in nuevos:
        if n not in actuales:
            actuales.append(n)
            agregados.append(n)
            
    if not agregados:
        print(f"{C_GREEN}Todos los objetivos indicados ya estaban en la lista. No se requieren cambios.{C_RESET}")
        return
        
    print(f"Modificando objetivos. Agregando: {C_GREEN}{', '.join(agregados)}{C_RESET}")
    
    nuevo_contenido = "\n".join(actuales) + "\n"
    # Escribir el nuevo archivo al servidor
    code, stdout, stderr = ejecutar_ssh(f"cat << 'EOF' > ~/plataforma_operativa/config/objetivos.txt\n{nuevo_contenido}EOF")
    
    if code == 0:
        print(f"{C_GREEN}✅ Lista de objetivos actualizada correctamente en el servidor.{C_RESET}")
    else:
        print(f"{C_RED}[ERROR] No se pudo guardar la lista en el servidor.{C_RESET}")
        print(stderr)

def correr_discovery_manual():
    print(f"{C_BOLD}🚀 Lanzando ejecución manual de Discovery Pasivo en OCI...{C_RESET}")
    print("Esto puede tardar hasta 1 minuto. Por favor espera...")
    
    # Ejecuta el script de discovery usando el venv correcto del servidor
    cmd_run = (
        "cd ~/plataforma_operativa && "
        "~/workspace_lab/venv/bin/python3 monitores/discovery_pasivo.py"
    )
    code, stdout, stderr = ejecutar_ssh(cmd_run)
    
    print("\n" + "=" * 50)
    print(f"{C_BOLD}RESULTADO DEL DISCOVERY (OCI STDOUT):{C_RESET}")
    print("-" * 50)
    print(stdout.strip() or "(Sin salida estándar)")
    
    if stderr.strip():
        print("-" * 50)
        print(f"{C_YELLOW}ALERTAS / ERRORES (OCI STDERR):{C_RESET}")
        print(stderr.strip())
    print("=" * 50)
    
    if code == 0:
        print(f"\n{C_GREEN}✅ Discovery completado exitosamente en OCI.{C_RESET}")
        # Mostrar el resultado final
        _, show_stdout, _ = ejecutar_ssh("cat ~/plataforma_operativa/resultados/actual.json 2>/dev/null || cat ~/plataforma_operativa/resultados/discovery_crudo.json 2>/dev/null || echo 'No se encontró el JSON de salida.'")
        print(f"\n{C_BOLD}Contenido del JSON de salida:{C_RESET}")
        print(show_stdout.strip())
    else:
        print(f"\n{C_RED}❌ El script de Discovery falló con código de salida: {code}{C_RESET}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Herramienta de Diagnóstico y Gestión OCI.")
    parser.add_argument("--add-targets", help="Lista de dominios separados por coma a añadir a objetivos.txt")
    parser.add_argument("--run-discovery", action="store_true", help="Lanza manualmente el script de Discovery pasivo en el servidor")
    
    args = parser.parse_code = parser.parse_args()
    
    if args.add_targets:
        actualizar_objetivos(args.add_targets)
    elif args.run_discovery:
        correr_discovery_manual()
    else:
        diagnosticar()
