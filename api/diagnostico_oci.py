#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diagnostico_oci.py — Panel de control y diagnóstico para el Nodo OCI.
Ejecutar sin argumentos: muestra el estado completo del servidor.
  --add-targets "dominio1.com,dominio2.com"  — añade objetivos a objetivos.txt
  --run-discovery                            — ejecuta discovery_pasivo.py manualmente
  --install-cron                             — instala el cron de automatización diario
"""

import os
import sys
import subprocess
import argparse
import base64

# Configuración de conexión OCI
KEY_PATH  = "/home/tomas2/WORKSPACE/tomas2/.ssh/id_rsa"
SERVER_IP = "129.80.73.248"
SSH_USER  = "ubuntu"

# Estilos de consola (ANSI)
C_BLUE   = "\033[36m"
C_GREEN  = "\033[32m"
C_YELLOW = "\033[33m"
C_RED    = "\033[31m"
C_BOLD   = "\033[1m"
C_RESET  = "\033[0m"


def ejecutar_ssh(comando_remoto, timeout=90):
    """Ejecuta un comando en el servidor OCI via SSH. Devuelve (code, stdout, stderr)."""
    cmd = [
        "ssh",
        "-F", "/dev/null",
        "-i", KEY_PATH,
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=10",
        f"{SSH_USER}@{SERVER_IP}",
        comando_remoto,
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return res.returncode, res.stdout, res.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT: La conexión excedió el límite de tiempo."
    except Exception as e:
        return -2, "", f"EXCEPCIÓN LOCAL: {type(e).__name__}: {e}"


def seccion(titulo):
    print(f"\n{C_BOLD}{titulo}{C_RESET}")
    print("-" * 55)


def ok(msg):   print(f"{C_GREEN}✅ {msg}{C_RESET}")
def warn(msg): print(f"{C_YELLOW}⚠️  {msg}{C_RESET}")
def err(msg):  print(f"{C_RED}❌ {msg}{C_RESET}")


# ─────────────────────────────────────────────────────────────────────────────
def diagnosticar():
    print(f"{C_BOLD}🔌 Conectando con {SSH_USER}@{SERVER_IP}...{C_RESET}", flush=True)

    # ── Verificar conectividad primero ──────────────────────────────────────
    code, _, stderr = ejecutar_ssh("true", timeout=12)
    if code != 0:
        err(f"No se pudo conectar al servidor OCI.\n   Detalle: {stderr.strip()}")
        sys.exit(1)

    print(f"\n{C_BLUE}{C_BOLD}" + "=" * 65)
    print("  🛰️  SISTEMA DE CONTROL Y DIAGNÓSTICO DEL NODO OCI")
    print("  Director Técnico Lab — Ciberseguridad & Bug Bounty")
    print("=" * 65 + C_RESET)

    # ── 1. Memoria y carga ──────────────────────────────────────────────────
    seccion("📊 MEMORIA & CARGA")
    _, out, _ = ejecutar_ssh("free -h && echo '---' && uptime")
    partes = out.split("---")
    print(partes[0].strip() if partes else "(sin datos)")
    if len(partes) > 1:
        print(f"\n{C_BOLD}Uptime:{C_RESET} {partes[1].strip()}")

    # ── 2. Procesos de monitoreo ────────────────────────────────────────────
    seccion("🐍 PROCESOS DE MONITOREO ACTIVOS")
    _, out, _ = ejecutar_ssh(
        "ps aux | grep -E 'discovery_pasivo|comparador|run_pipeline' | grep -v grep || true"
    )
    if out.strip():
        print(f"{C_YELLOW}{out.strip()}{C_RESET}")
    else:
        ok("Ningún script de monitoreo corriendo ahora (correcto fuera de horario cron).")

    # ── 3. Crontab ──────────────────────────────────────────────────────────
    seccion("⏰ PLANIFICADOR CRON")
    _, out, _ = ejecutar_ssh("crontab -l 2>/dev/null || echo '__VACIO__'")
    out = out.strip()
    if out == "__VACIO__" or not out:
        err("No hay crontab configurado — el pipeline NO se ejecuta automáticamente.")
        warn("Usa  ./diagnostico_oci.py --install-cron  para configurarlo.")
    elif "run_pipeline" in out:
        ok("Automatización activa:")
        print(out)
    else:
        warn("Hay crontab pero sin la tarea run_pipeline.sh:")
        print(out)

    # ── 4. Objetivos monitoreados ───────────────────────────────────────────
    seccion("🎯 OBJETIVOS EN config/objetivos.txt")
    _, out, _ = ejecutar_ssh(
        "cat ~/plataforma_operativa/config/objetivos.txt 2>/dev/null || echo '__NO_EXISTE__'"
    )
    out = out.strip()
    if out == "__NO_EXISTE__" or not out:
        err("El archivo objetivos.txt no existe o está vacío.")
    else:
        dominios = [d.strip() for d in out.splitlines() if d.strip()]
        for i, d in enumerate(dominios, 1):
            color = C_GREEN if "mongodb" in d else C_YELLOW
            print(f"  {i}. {color}{d}{C_RESET}")
        if not any("mongodb" in d for d in dominios):
            err("'mongodb.com' NO está en la lista — agrega con --add-targets mongodb.com")

    # ── 5. Estado del pipeline de resultados ───────────────────────────────
    seccion("📁 LOGS & RESULTADOS")
    _, out_logs, _ = ejecutar_ssh(
        "ls -lh ~/plataforma_operativa/logs/ 2>/dev/null || echo '__VACIO__'"
    )
    _, out_res, _ = ejecutar_ssh(
        "ls -lh ~/plataforma_operativa/resultados/ 2>/dev/null || echo '__VACIO__'"
    )
    print(f"{C_BOLD}[LOGS]:{C_RESET}")
    logs = out_logs.strip()
    print(logs if logs != "__VACIO__" and logs else f"{C_YELLOW}  (directorio vacío){C_RESET}")
    print(f"\n{C_BOLD}[RESULTADOS]:{C_RESET}")
    res = out_res.strip()
    print(res if res != "__VACIO__" and res else f"{C_YELLOW}  (directorio vacío){C_RESET}")

    # ── 6. Último JSON de resultados ────────────────────────────────────────
    seccion("📄 ÚLTIMO RESULTADO DE DISCOVERY")
    _, out, _ = ejecutar_ssh(
        "cat ~/plataforma_operativa/resultados/actual.json 2>/dev/null || echo '__NO_EXISTE__'"
    )
    if out.strip() == "__NO_EXISTE__":
        warn("No existe actual.json todavía.")
    else:
        print(out.strip())

    # ── 7. Estado de crt.sh (fuente de datos) ──────────────────────────────
    seccion("🌐 DISPONIBILIDAD DE crt.sh (fuente de subdominios)")
    _, out, _ = ejecutar_ssh(
        'curl -s -o /dev/null -w "%{http_code} | %{size_download}bytes | %{time_total}s" '
        '"https://crt.sh/?q=%.mongodb.com&output=json" --max-time 15 2>/dev/null || echo "FALLO"'
    )
    out = out.strip()
    if "FALLO" in out or not out:
        err("crt.sh no respondió o el comando falló.")
    elif out.startswith("200"):
        ok(f"crt.sh responde correctamente: {out}")
    elif out.startswith("502") or out.startswith("000"):
        err(f"crt.sh está caído o sobrecargado: {out}")
        warn("Esto explica por qué el discovery no encuentra subdominios.")
        warn("Solución: esperar y volver a correr --run-discovery más tarde.")
    else:
        warn(f"crt.sh respondió con estado inusual: {out}")

    print()


# ─────────────────────────────────────────────────────────────────────────────
def actualizar_objetivos(targets_raw):
    nuevos = [t.strip().lower() for t in targets_raw.split(",") if t.strip()]
    if not nuevos:
        err("Lista de objetivos vacía.")
        return

    print(f"{C_BOLD}🔄 Leyendo objetivos actuales en el servidor...{C_RESET}")
    _, out, _ = ejecutar_ssh(
        "cat ~/plataforma_operativa/config/objetivos.txt 2>/dev/null || true"
    )
    actuales = [l.strip().lower() for l in out.splitlines() if l.strip()]

    agregados = [n for n in nuevos if n not in actuales]
    if not agregados:
        ok("Todos los objetivos indicados ya estaban en la lista. No se requieren cambios.")
        print(f"  Lista actual: {', '.join(actuales)}")
        return

    print(f"  Agregando: {C_GREEN}{', '.join(agregados)}{C_RESET}")
    actuales.extend(agregados)
    nuevo_contenido = "\n".join(actuales)

    # Escribir usando printf para evitar problemas de heredoc en SSH
    cmd_write = f"printf '%s\\n' {' '.join(actuales)} > ~/plataforma_operativa/config/objetivos.txt"
    code, _, stderr = ejecutar_ssh(cmd_write)
    if code == 0:
        ok(f"Lista actualizada: {', '.join(actuales)}")
    else:
        err(f"No se pudo guardar en el servidor: {stderr.strip()}")

# ─────────────────────────────────────────────────────────────────────────────
def remover_objetivos(targets_raw):
    eliminar = [t.strip().lower() for t in targets_raw.split(",") if t.strip()]
    if not eliminar:
        err("Lista de objetivos a eliminar vacía.")
        return

    print(f"{C_BOLD}🔄 Leyendo objetivos actuales en el servidor...{C_RESET}")
    _, out, _ = ejecutar_ssh(
        "cat ~/plataforma_operativa/config/objetivos.txt 2>/dev/null || true"
    )
    actuales = [l.strip().lower() for l in out.splitlines() if l.strip()]

    removidos = [n for n in eliminar if n in actuales]
    if not removidos:
        ok("Ninguno de los objetivos indicados estaba en la lista.")
        print(f"  Lista actual: {', '.join(actuales)}")
        return

    print(f"  Eliminando: {C_RED}{', '.join(removidos)}{C_RESET}")
    nuevos_actuales = [n for n in actuales if n not in removidos]
    
    if not nuevos_actuales:
        cmd_write = "echo '' > ~/plataforma_operativa/config/objetivos.txt"
    else:
        cmd_write = f"printf '%s\\n' {' '.join(nuevos_actuales)} > ~/plataforma_operativa/config/objetivos.txt"
        
    code, _, stderr = ejecutar_ssh(cmd_write)
    if code == 0:
        ok(f"Lista actualizada: {', '.join(nuevos_actuales) if nuevos_actuales else '(vacía)'}")
    else:
        err(f"No se pudo guardar en el servidor: {stderr.strip()}")


# ─────────────────────────────────────────────────────────────────────────────
def instalar_cron():
    """
    Instala o actualiza el crontab del servidor OCI para que corra a las 03:00 UTC.
    - Remueve cualquier cron antiguo de discovery_pasivo.py o de run_pipeline.sh.
    - Agrega la línea de run_pipeline.sh programada a las 03:00 UTC.
    """
    print(f"{C_BOLD}⏰ Configurando crontab en OCI para ejecutarse a las 03:00 UTC...{C_RESET}")

    _, cron_actual, _ = ejecutar_ssh("crontab -l 2>/dev/null || echo ''")
    cron_actual = cron_actual.strip()

    linea_objetivo = (
        "0 3 * * * /home/ubuntu/plataforma_operativa/run_pipeline.sh "
        ">> /home/ubuntu/plataforma_operativa/logs/cron_output.log 2>"
        "/home/ubuntu/plataforma_operativa/logs/cron_error.log"
    )

    # Filtrar líneas anteriores relacionadas con monitoreo
    lineas_nuevas = []
    for linea in cron_actual.splitlines():
        linea_clean = linea.strip()
        if not linea_clean:
            continue
        # Excluir tareas anteriores de monitoreo para reemplazarlas
        if "run_pipeline.sh" in linea_clean or "discovery_pasivo.py" in linea_clean:
            continue
        lineas_nuevas.append(linea_clean)

    # Añadir nuestra línea objetivo
    lineas_nuevas.append(linea_objetivo)

    nuevo_cron = "\n".join(lineas_nuevas) + "\n"
    encoded_cron = base64.b64encode(nuevo_cron.encode('utf-8')).decode('utf-8')
    cmd = f"echo '{encoded_cron}' | base64 -d | crontab -"

    code, _, stderr = ejecutar_ssh(cmd)
    if code == 0:
        ok("Crontab actualizado exitosamente a las 03:00 UTC.")
        print(f"  Línea configurada: {linea_objetivo}")
    else:
        err(f"Error actualizando crontab: {stderr.strip()}")


# ─────────────────────────────────────────────────────────────────────────────
def correr_discovery_manual():
    print(f"{C_BOLD}🚀 Lanzando Discovery Pasivo manualmente en OCI...{C_RESET}")
    print("  (Esto puede tardar hasta 90 segundos)\n")

    cmd = (
        "cd ~/plataforma_operativa && "
        "~/workspace_lab/venv/bin/python3 monitores/discovery_pasivo.py"
    )
    code, stdout, stderr = ejecutar_ssh(cmd, timeout=120)

    print("=" * 60)
    print(f"{C_BOLD}STDOUT del servidor:{C_RESET}")
    print(stdout.strip() or "(Sin salida)")
    if stderr.strip():
        print(f"\n{C_YELLOW}STDERR:{C_RESET}")
        print(stderr.strip())
    print("=" * 60)

    if code == 0:
        ok("Discovery completado. JSON de salida:")
        _, json_out, _ = ejecutar_ssh(
            "cat ~/plataforma_operativa/resultados/actual.json 2>/dev/null || echo 'No encontrado'"
        )
        print(json_out.strip())
    else:
        err(f"Discovery falló (código {code}).")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Panel de Control del Nodo OCI.")
    parser.add_argument("--add-targets", metavar="DOMINIOS",
                        help="Dominios separados por coma a añadir a objetivos.txt")
    parser.add_argument("--remove-targets", metavar="DOMINIOS",
                        help="Dominios separados por coma a eliminar de objetivos.txt")
    parser.add_argument("--run-discovery", action="store_true",
                        help="Ejecuta manualmente discovery_pasivo.py en OCI")
    parser.add_argument("--install-cron", action="store_true",
                        help="Instala el crontab de ejecución diaria en OCI")
    args = parser.parse_args()

    if args.add_targets:
        actualizar_objetivos(args.add_targets)
    elif args.remove_targets:
        remover_objetivos(args.remove_targets)
    elif args.run_discovery:
        correr_discovery_manual()
    elif args.install_cron:
        instalar_cron()
    else:
        diagnosticar()
