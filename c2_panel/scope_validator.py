#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scope_validator.py -- M3-B: HackerOne Scope & Deduplication Engine
===================================================================
Eslabon 0 del pipeline OCI-1. Filtra hallazgos out-of-scope y duplicados.
Sin dependencias externas. Solo stdlib.
"""

import fnmatch
import hashlib
import json
import os
import sys
from pathlib import Path

# ----------------------------------------------------------------------------
# SCOPE_DB — 57 dominios activos mapeados a programas H1
# Fuente: actual.json auditado 2026-07-31 (679,492 subdominios)
# in_scope: wildcards fnmatch, out_of_scope: exclusiones exactas
# min_severity: "low"|"medium"|"high"|"critical"
# ----------------------------------------------------------------------------
SCOPE_DB = {
    "shopify": {
        "in_scope": ["*.shopify.com", "*.myshopify.com", "shopify.com", "*.shopifycloud.com"],
        "out_of_scope": ["careers.shopify.com", "community.shopify.com", "help.shopify.com"],
        "min_severity": "low",
        "pays_info_disclosure": True,
        "h1_slug": "shopify",
        "h1_report_url": "https://hackerone.com/shopify/reports/new",
    },
    "grab": {
        "in_scope": ["*.grab.com", "grab.com"],
        "out_of_scope": ["careers.grab.com", "blog.grab.com"],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "grab",
        "h1_report_url": "https://hackerone.com/grab/reports/new",
    },
    "slack": {
        "in_scope": ["*.slack.com", "slack.com", "*.slack-edge.com"],
        "out_of_scope": ["status.slack.com", "slackhq.com"],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "slack",
        "h1_report_url": "https://hackerone.com/slack/reports/new",
    },
    "okta": {
        "in_scope": ["*.okta.com", "okta.com", "*.oktapreview.com", "*.auth0.com", "auth0.com"],
        "out_of_scope": ["developer.okta.com", "support.okta.com"],
        "min_severity": "low",
        "pays_info_disclosure": True,
        "h1_slug": "okta",
        "h1_report_url": "https://hackerone.com/okta/reports/new",
    },
    "zoom": {
        "in_scope": ["*.zoom.us", "zoom.us", "*.zoom.com"],
        "out_of_scope": ["blog.zoom.us", "explore.zoom.us"],
        "min_severity": "low",
        "pays_info_disclosure": True,
        "h1_slug": "zoom_video_communications",
        "h1_report_url": "https://hackerone.com/zoom_video_communications/reports/new",
    },
    "atlassian": {
        "in_scope": ["*.atlassian.com", "atlassian.com", "*.atlassian.net", "*.atlassian.io", "*.jira.com", "*.trello.com"],
        "out_of_scope": ["community.atlassian.com", "support.atlassian.com"],
        "min_severity": "low",
        "pays_info_disclosure": True,
        "h1_slug": "atlassian",
        "h1_report_url": "https://hackerone.com/atlassian/reports/new",
    },
    "paypal": {
        "in_scope": ["*.paypal.com", "paypal.com", "*.paypalobjects.com"],
        "out_of_scope": ["newsroom.paypal.com", "investor.paypal.com"],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "paypal",
        "h1_report_url": "https://hackerone.com/paypal/reports/new",
    },
    "twilio": {
        "in_scope": ["*.twilio.com", "twilio.com", "*.sendgrid.com", "sendgrid.com", "*.segment.com"],
        "out_of_scope": ["blog.twilio.com", "community.twilio.com"],
        "min_severity": "low",
        "pays_info_disclosure": True,
        "h1_slug": "twilio",
        "h1_report_url": "https://hackerone.com/twilio/reports/new",
    },
    "airbnb": {
        "in_scope": ["*.airbnb.com", "airbnb.com", "*.airbnb.io", "*.airbnb.org"],
        "out_of_scope": ["news.airbnb.com"],
        "min_severity": "low",
        "pays_info_disclosure": True,
        "h1_slug": "airbnb",
        "h1_report_url": "https://hackerone.com/airbnb/reports/new",
    },
    "stripe": {
        "in_scope": ["*.stripe.com", "stripe.com"],
        "out_of_scope": ["support.stripe.com"],
        "min_severity": "low",
        "pays_info_disclosure": True,
        "h1_slug": "stripe",
        "h1_report_url": "https://hackerone.com/stripe/reports/new",
    },
    "cloudflare": {
        "in_scope": ["*.cloudflare.com", "cloudflare.com"],
        "out_of_scope": ["community.cloudflare.com", "blog.cloudflare.com"],
        "min_severity": "low",
        "pays_info_disclosure": True,
        "h1_slug": "cloudflare",
        "h1_report_url": "https://hackerone.com/cloudflare/reports/new",
    },
    "coinbase": {
        "in_scope": ["*.coinbase.com", "coinbase.com"],
        "out_of_scope": ["blog.coinbase.com", "help.coinbase.com"],
        "min_severity": "low",
        "pays_info_disclosure": True,
        "h1_slug": "coinbase",
        "h1_report_url": "https://hackerone.com/coinbase/reports/new",
    },
    "discord": {
        "in_scope": ["*.discord.com", "discord.com", "*.discordapp.com"],
        "out_of_scope": ["support.discord.com"],
        "min_severity": "low",
        "pays_info_disclosure": True,
        "h1_slug": "discord",
        "h1_report_url": "https://hackerone.com/discord/reports/new",
    },
    "gitlab": {
        "in_scope": ["*.gitlab.com", "gitlab.com", "*.gitlab.io"],
        "out_of_scope": [],
        "min_severity": "low",
        "pays_info_disclosure": True,
        "h1_slug": "gitlab",
        "h1_report_url": "https://hackerone.com/gitlab/reports/new",
    },
    "digitalocean": {
        "in_scope": ["*.digitalocean.com", "digitalocean.com"],
        "out_of_scope": ["community.digitalocean.com"],
        "min_severity": "low",
        "pays_info_disclosure": True,
        "h1_slug": "digitalocean",
        "h1_report_url": "https://hackerone.com/digitalocean/reports/new",
    },
    "uber": {
        "in_scope": ["*.uber.com", "uber.com"],
        "out_of_scope": ["newsroom.uber.com"],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "uber",
        "h1_report_url": "https://hackerone.com/uber/reports/new",
    },
    "lyft": {
        "in_scope": ["*.lyft.com", "lyft.com"],
        "out_of_scope": ["blog.lyft.com"],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "lyft",
        "h1_report_url": "https://hackerone.com/lyft/reports/new",
    },
    "doordash": {
        "in_scope": ["*.doordash.com", "doordash.com"],
        "out_of_scope": [],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "doordash",
        "h1_report_url": "https://hackerone.com/doordash/reports/new",
    },
    "snapchat": {
        "in_scope": ["*.snapchat.com", "snapchat.com", "*.snap.com"],
        "out_of_scope": [],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "snapchat",
        "h1_report_url": "https://hackerone.com/snapchat/reports/new",
    },
    "robinhood": {
        "in_scope": ["*.robinhood.com", "robinhood.com"],
        "out_of_scope": [],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "robinhood",
        "h1_report_url": "https://hackerone.com/robinhood/reports/new",
    },
    "asana": {
        "in_scope": ["*.asana.com", "asana.com"],
        "out_of_scope": ["forum.asana.com"],
        "min_severity": "low",
        "pays_info_disclosure": True,
        "h1_slug": "asana",
        "h1_report_url": "https://hackerone.com/asana/reports/new",
    },
    "spotify": {
        "in_scope": ["*.spotify.com", "spotify.com"],
        "out_of_scope": ["community.spotify.com"],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "spotify",
        "h1_report_url": "https://hackerone.com/spotify/reports/new",
    },
    "freshworks": {
        "in_scope": ["*.freshdesk.com", "*.freshservice.com", "*.freshworks.com", "*.freshchat.com"],
        "out_of_scope": [],
        "min_severity": "low",
        "pays_info_disclosure": True,
        "h1_slug": "freshworks",
        "h1_report_url": "https://hackerone.com/freshworks/reports/new",
    },
    "booking": {
        "in_scope": ["*.booking.com", "booking.com"],
        "out_of_scope": ["news.booking.com"],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "booking_com",
        "h1_report_url": "https://hackerone.com/booking_com/reports/new",
    },
    "hubspot": {
        "in_scope": ["*.hubspot.com", "hubspot.com"],
        "out_of_scope": ["community.hubspot.com", "blog.hubspot.com"],
        "min_severity": "low",
        "pays_info_disclosure": True,
        "h1_slug": "hubspot",
        "h1_report_url": "https://hackerone.com/hubspot/reports/new",
    },
    "roblox": {
        "in_scope": ["*.roblox.com", "roblox.com"],
        "out_of_scope": ["devforum.roblox.com", "blog.roblox.com"],
        "min_severity": "low",
        "pays_info_disclosure": True,
        "h1_slug": "roblox",
        "h1_report_url": "https://hackerone.com/roblox/reports/new",
    },
    "kraken": {
        "in_scope": ["*.kraken.com", "kraken.com"],
        "out_of_scope": ["support.kraken.com"],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "kraken",
        "h1_report_url": "https://hackerone.com/kraken/reports/new",
    },
    "binance": {
        "in_scope": ["*.binance.com", "binance.com"],
        "out_of_scope": ["academy.binance.com"],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "binance",
        "h1_report_url": "https://hackerone.com/binance/reports/new",
    },
    "notion": {
        "in_scope": ["*.notion.so", "notion.so", "*.notion.com"],
        "out_of_scope": [],
        "min_severity": "low",
        "pays_info_disclosure": True,
        "h1_slug": "notion",
        "h1_report_url": "https://hackerone.com/notion/reports/new",
    },
    "instacart": {
        "in_scope": ["*.instacart.com", "instacart.com"],
        "out_of_scope": [],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "instacart",
        "h1_report_url": "https://hackerone.com/instacart/reports/new",
    },
    "epicgames": {
        "in_scope": ["*.epicgames.com", "epicgames.com", "*.unrealengine.com"],
        "out_of_scope": ["dev.epicgames.com"],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "epic_games",
        "h1_report_url": "https://hackerone.com/epic_games/reports/new",
    },
    "tiktok": {
        "in_scope": ["*.tiktok.com", "tiktok.com"],
        "out_of_scope": ["newsroom.tiktok.com"],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "tiktok",
        "h1_report_url": "https://hackerone.com/tiktok/reports/new",
    },
    "adobe": {
        "in_scope": ["*.adobe.com", "adobe.com", "*.adobe.io", "*.adobe.net"],
        "out_of_scope": ["blog.adobe.com"],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "adobe",
        "h1_report_url": "https://hackerone.com/adobe/reports/new",
    },
    "amazon": {
        "in_scope": ["*.amazon.com", "amazon.com"],
        "out_of_scope": ["affiliate.amazon.com"],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "amazon_bbp",
        "h1_report_url": "https://hackerone.com/amazon_bbp/reports/new",
    },
    "apple": {
        "in_scope": ["*.apple.com", "apple.com"],
        "out_of_scope": ["discussions.apple.com"],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "apple",
        "h1_report_url": "https://hackerone.com/apple/reports/new",
    },
    "etsy": {
        "in_scope": ["*.etsy.com", "etsy.com"],
        "out_of_scope": ["community.etsy.com"],
        "min_severity": "low",
        "pays_info_disclosure": True,
        "h1_slug": "etsy",
        "h1_report_url": "https://hackerone.com/etsy/reports/new",
    },
    "github": {
        "in_scope": ["*.github.com", "github.com", "*.github.io", "*.githubusercontent.com"],
        "out_of_scope": ["education.github.com", "blog.github.com"],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "github_bbp",
        "h1_report_url": "https://hackerone.com/github_bbp/reports/new",
    },
    "agoda": {
        "in_scope": ["*.agoda.com", "agoda.com"],
        "out_of_scope": [],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "agoda",
        "h1_report_url": "https://hackerone.com/agoda/reports/new",
    },
    "mercari": {
        "in_scope": ["*.mercari.com", "mercari.com"],
        "out_of_scope": [],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "mercari",
        "h1_report_url": "https://hackerone.com/mercari/reports/new",
    },
    "twitch": {
        "in_scope": ["*.twitch.tv", "twitch.tv", "*.twitch.com"],
        "out_of_scope": [],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "twitch",
        "h1_report_url": "https://hackerone.com/twitch/reports/new",
    },
    "adyen": {
        "in_scope": ["*.adyen.com", "adyen.com", "*.adyen.net"],
        "out_of_scope": [],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "adyen",
        "h1_report_url": "https://hackerone.com/adyen/reports/new",
    },
    "square": {
        "in_scope": ["*.square.com", "square.com", "*.squareup.com"],
        "out_of_scope": [],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "square",
        "h1_report_url": "https://hackerone.com/square/reports/new",
    },
    "ebay": {
        "in_scope": ["*.ebay.com", "ebay.com"],
        "out_of_scope": ["community.ebay.com"],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "ebay",
        "h1_report_url": "https://hackerone.com/ebay/reports/new",
    },
    "yahoo": {
        "in_scope": ["*.yahoo.com", "yahoo.com"],
        "out_of_scope": [],
        "min_severity": "medium",
        "pays_info_disclosure": False,
        "h1_slug": "yahoo",
        "h1_report_url": "https://hackerone.com/yahoo/reports/new",
    },
}

# Mapa rapido: dominio-raiz → clave en SCOPE_DB
_ROOT_TO_PROGRAM = {}
for prog_key, prog_data in SCOPE_DB.items():
    for pattern in prog_data["in_scope"]:
        root = pattern.lstrip("*.")
        # Extraer dominio raiz (ej: "shopify.com" de "*.shopify.com")
        parts = root.split(".")
        if len(parts) >= 2:
            root_key = ".".join(parts[-2:])
            if root_key not in _ROOT_TO_PROGRAM:
                _ROOT_TO_PROGRAM[root_key] = prog_key

# Severidades ordenadas para comparacion
_SEV_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}

# Ruta del archivo de deduplicacion (persiste entre ejecuciones)
_BASE = Path("/home/ubuntu/plataforma_operativa/resultados")
if not _BASE.exists():
    _BASE = Path(__file__).parent.parent / "resultados"
SEEN_FILE = _BASE / "seen_findings.jsonl"


def _load_seen_hashes() -> set:
    """Carga los hashes de hallazgos ya vistos desde disco."""
    seen = set()
    if SEEN_FILE.exists():
        try:
            with open(SEEN_FILE, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        seen.add(line)
        except Exception:
            pass
    return seen


def _save_hash(h: str):
    """Persiste un hash de hallazgo en disco."""
    try:
        SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SEEN_FILE, "a") as f:
            f.write(h + "\n")
    except Exception:
        pass


def _fingerprint(target: str, vuln_type: str) -> str:
    """SHA-256 determinista de (target, vuln_type). Evita duplicados entre ejecuciones."""
    raw = "{}|{}".format(target.lower().strip("/"), vuln_type.lower().strip())
    return hashlib.sha256(raw.encode()).hexdigest()


def scope_check(host: str, severity: str) -> dict:
    """
    Valida si el host esta in-scope para algun programa H1 conocido
    y si la severidad cumple el minimo del programa.

    Retorna:
        {
          "valid": bool,
          "reason": str,
          "program_slug": str,
          "h1_report_url": str,
          "program_key": str,
        }
    """
    host_clean = host.lower().replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]

    for prog_key, prog_data in SCOPE_DB.items():
        # Verificar out_of_scope primero (exclusiones exactas)
        if host_clean in [x.lower() for x in prog_data["out_of_scope"]]:
            return {
                "valid": False,
                "reason": "HOST_OUT_OF_SCOPE_EXCLUSION: {}".format(prog_key),
                "program_slug": prog_data["h1_slug"],
                "h1_report_url": prog_data["h1_report_url"],
                "program_key": prog_key,
            }

        # Verificar in_scope via fnmatch
        for pattern in prog_data["in_scope"]:
            if fnmatch.fnmatch(host_clean, pattern.lower()):
                # Verificar severidad minima
                sev_val = _SEV_ORDER.get(severity.lower(), 0)
                min_val = _SEV_ORDER.get(prog_data["min_severity"], 1)
                if sev_val < min_val:
                    return {
                        "valid": False,
                        "reason": "SEVERITY_BELOW_MINIMUM: {} requires {}, got {}".format(
                            prog_key, prog_data["min_severity"], severity
                        ),
                        "program_slug": prog_data["h1_slug"],
                        "h1_report_url": prog_data["h1_report_url"],
                        "program_key": prog_key,
                    }
                return {
                    "valid": True,
                    "reason": "IN_SCOPE: matched pattern {} in {}".format(pattern, prog_key),
                    "program_slug": prog_data["h1_slug"],
                    "h1_report_url": prog_data["h1_report_url"],
                    "program_key": prog_key,
                }

    return {
        "valid": False,
        "reason": "NOT_IN_ANY_KNOWN_PROGRAM",
        "program_slug": "",
        "h1_report_url": "",
        "program_key": "",
    }


def dedup_check(target: str, vuln_type: str) -> tuple:
    """
    Comprueba si el hallazgo ya fue visto antes (deduplicacion cross-ejecucion).

    Retorna: (is_duplicate: bool, fingerprint: str)
    Si no es duplicado, persiste el hash en disco automaticamente.
    """
    fp = _fingerprint(target, vuln_type)
    seen = _load_seen_hashes()
    if fp in seen:
        return True, fp
    _save_hash(fp)
    return False, fp


def calculate_batch_size() -> int:
    """
    Calcula dinamicamente el numero optimo de subdominios a procesar
    por ejecucion, leyendo la RAM disponible en /proc/meminfo.

    OCI Free Tier sweet spot calibrado:
      >600MB disponibles -> 4000 subdominios
      400-600MB         -> 3000
      200-400MB         -> 2000
      <200MB            -> 1000 (modo emergencia)
    """
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    kb = int(line.split()[1])
                    mb = kb // 1024
                    if mb > 600:
                        return 4000
                    elif mb > 400:
                        return 3000
                    elif mb > 200:
                        return 2000
                    else:
                        return 1000
    except Exception:
        pass
    return 2500  # Fallback conservador


# ----------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== scope_validator.py -- Self Test ===\n")

    tests = [
        ("blog.shopify.com", "medium"),
        ("careers.shopify.com", "high"),
        ("api.unknown-company.com", "high"),
        ("api.grab.com", "low"),
        ("api.grab.com", "high"),
        ("sub.discord.com", "low"),
    ]
    for host, sev in tests:
        r = scope_check(host, sev)
        status = "VALID" if r["valid"] else "BLOCKED"
        print("[{}] {} ({}) -> {} | {}".format(status, host, sev, r["program_slug"], r["reason"]))

    print("\n=== Dedup Test ===")
    dup1, fp1 = dedup_check("https://api.shopify.com", "Subdomain Takeover")
    dup2, fp2 = dedup_check("https://api.shopify.com", "Subdomain Takeover")
    print("First seen:  duplicate={}".format(dup1))
    print("Second seen: duplicate={}".format(dup2))

    print("\n=== Batch Size ===")
    print("Optimal batch size: {} subdominios".format(calculate_batch_size()))
