#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WHATS LOOKUP - Herramienta Avanzada de OSINT para WhatsApp y Números Telefónicos
Versión 2.0 (Autónoma con TUX Mejorada)
"""

import os
import re
import sys
import json
import time
import base64
import argparse
from datetime import datetime
from typing import Dict, Any, Optional

import requests
from dotenv import load_dotenv

# Librerías TUI y OSINT
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich import box
from rich.columns import Columns

import phonenumbers
from phonenumbers import geocoder, carrier, timezone, PhoneNumberType

# Cargar variables de entorno si existen
load_dotenv()

console = Console()

RAPIDAPI_HOST = "whatsapp-osint.p.rapidapi.com"


# ==============================================================================
# BANNERS Y ESTÉTICA TUI (TUX)
# ==============================================================================

def print_banner():
    banner_text = Text()
    banner_text.append("""
  ╦ ╦╦ ╦╔═╗╔╦╗╔═╗  ╦  ╔═╗╔═╗╦╔═╦ ╦╔═╗
  ║║║╠═╣╠═╣ ║ ╚═╗  ║  ║ ║║ ║╠╩╗║ ║╠═╝
  ╚╩╝╩ ╩╩ ╩ ╩ ╚═╝  ╩═╝╚═╝╚═╝╩ ╩╚═╝╩  
""", style="bold bright_cyan")
    
    subtitle = Text("🕵️  ADVANCED WHATSAPP & PHONE OSINT SUITE v2.0", style="bold bright_yellow")
    info = Text("⚡ 100% Autónomo • Sin dependencias de pago obligatorias • Multi-Herramienta", style="italic white")
    
    panel = Panel(
        Text.assemble(banner_text, "\n", subtitle, "\n", info),
        border_style="bright_blue",
        box=box.DOUBLE_EDGE,
        padding=(0, 2)
    )
    console.print(panel)


# ==============================================================================
# MOTOR OSINT NATIVO: ANÁLISIS DE TELECOMUNICACIONES
# ==============================================================================

def parse_and_validate_number(raw_phone: str) -> Optional[Dict[str, Any]]:
    """Analiza y valida un número usando phonenumbers (Google libphonenumber)."""
    cleaned = raw_phone.strip()
    if not cleaned.startswith("+"):
        # Si no tiene '+', lo agregamos para intentar parseo internacional
        test_phone = "+" + cleaned
    else:
        test_phone = cleaned

    try:
        parsed = phonenumbers.parse(test_phone, None)
    except phonenumbers.NumberParseException:
        # Intento fallback si se introdujo número local
        try:
            parsed = phonenumbers.parse(raw_phone, "ES")
        except Exception:
            return None

    if not phonenumbers.is_possible_number(parsed):
        return None

    is_valid = phonenumbers.is_valid_number(parsed)
    country_code = parsed.country_code
    national_number = str(parsed.national_number)
    
    # Formatos estándar
    e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    intl_format = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    nat_format = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
    rfc3966 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.RFC3966)
    digits_only = re.sub(r"[^\d]", "", e164)

    # Ubicación / Geocodificación
    loc_es = geocoder.description_for_number(parsed, "es") or "No disponible"
    loc_en = geocoder.description_for_number(parsed, "en") or loc_es
    region_code = phonenumbers.region_code_for_number(parsed) or "Desconocido"

    # Operador telefónico (Carrier)
    carrier_es = carrier.name_for_number(parsed, "es") or "No disponible / Portabilidad abierta"
    carrier_en = carrier.name_for_number(parsed, "en") or carrier_es

    # Tipo de línea
    num_type_enum = phonenumbers.number_type(parsed)
    type_map = {
        PhoneNumberType.MOBILE: "📱 Móvil (Mobile)",
        PhoneNumberType.FIXED_LINE: "☎️ Línea Fija (Fixed Line)",
        PhoneNumberType.FIXED_LINE_OR_MOBILE: "📱/☎️ Fijo o Móvil",
        PhoneNumberType.TOLL_FREE: "🆓 Número Gratuito (Toll Free)",
        PhoneNumberType.PREMIUM_RATE: "💎 Tarifa Especial (Premium)",
        PhoneNumberType.SHARED_COST: "⚖️ Costo Compartido",
        PhoneNumberType.VOIP: "💻 Voz sobre IP (VoIP)",
        PhoneNumberType.PERSONAL_NUMBER: "👤 Número Personal",
        PhoneNumberType.PAGER: "📟 Buscapersonas (Pager)",
        PhoneNumberType.UAN: "🏢 Número de Acceso Universal (UAN)",
        PhoneNumberType.VOICEMAIL: "🎙️ Buzón de Voz",
        PhoneNumberType.UNKNOWN: "❓ Desconocido"
    }
    line_type = type_map.get(num_type_enum, "❓ Desconocido")

    # Zonas horarias
    tz_list = list(timezone.time_zones_for_number(parsed))

    return {
        "is_valid": is_valid,
        "country_code": country_code,
        "region_code": region_code,
        "national_number": national_number,
        "e164": e164,
        "digits_only": digits_only,
        "international_format": intl_format,
        "national_format": nat_format,
        "rfc3966": rfc3966,
        "location": loc_es,
        "location_en": loc_en,
        "carrier": carrier_es,
        "line_type": line_type,
        "timezones": tz_list,
        "parsed_object": parsed
    }


def display_telecom_table(data: Dict[str, Any]):
    """Muestra los datos de telecomunicaciones en una tabla Rich."""
    table = Table(title="📡 ANÁLISIS DE TELECOMUNICACIONES & CARRIER", box=box.ROUNDED, border_style="bright_cyan", header_style="bold bright_white")
    table.add_column("Atributo", style="cyan", width=26)
    table.add_column("Detalle OSINT", style="bright_white")

    valid_badge = "[bold green]✓ VÁLIDO[/bold green]" if data["is_valid"] else "[bold red]✗ INVÁLIDO O INCOMPLETO[/bold red]"
    table.add_row("Estado de Validez", valid_badge)
    table.add_row("Formato E.164", f"[bold yellow]{data['e164']}[/bold yellow]")
    table.add_row("Formato Internacional", data["international_format"])
    table.add_row("Formato Nacional", data["national_format"])
    table.add_row("Código de País / Región", f"+{data['country_code']} (ISO: {data['region_code']})")
    table.add_row("Ubicación Geográfica", f"[bold green]{data['location']}[/bold green]")
    table.add_row("Operador / ISP Móvil", f"[bold bright_magenta]{data['carrier']}[/bold bright_magenta]")
    table.add_row("Tipo de Línea", data["line_type"])
    table.add_row("Zonas Horarias", ", ".join(data["timezones"]) if data["timezones"] else "No disponible")

    console.print(table)


# ==============================================================================
# MOTOR OSINT NATIVO: WHATSAPP DEEP LINKS & VERIFICACIÓN
# ==============================================================================

def analyze_whatsapp_links(data: Dict[str, Any]) -> Dict[str, str]:
    """Genera y comprueba enlaces de WhatsApp públicos."""
    digits = data["digits_only"]
    wa_me_url = f"https://wa.me/{digits}"
    api_url = f"https://api.whatsapp.com/send?phone={digits}"
    web_url = f"https://web.whatsapp.com/send?phone={digits}"
    app_deep_link = f"whatsapp://send?phone={digits}"

    return {
        "wa_me": wa_me_url,
        "api_send": api_url,
        "whatsapp_web": web_url,
        "app_protocol": app_deep_link
    }


def verify_whatsapp_web(data: Dict[str, Any]) -> Dict[str, Any]:
    """Realiza una petición ligera a la pasarela web de WhatsApp para comprobar respuesta HTTP."""
    digits = data["digits_only"]
    url = f"https://api.whatsapp.com/send?phone={digits}"
    result = {
        "url": url,
        "status_code": None,
        "accessible": False,
        "registered_hint": "Desconocido (WhatsApp oculta estados directos en peticiones sin sesión)"
    }
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        result["status_code"] = r.status_code
        if r.status_code == 200:
            result["accessible"] = True
            result["registered_hint"] = "🟢 Endpoint activo y listo para apertura de chat directo"
        else:
            result["registered_hint"] = f"Código HTTP {r.status_code}"
    except Exception as e:
        result["registered_hint"] = f"Error de conexión: {e}"

    return result


def display_whatsapp_table(data: Dict[str, Any], wa_links: Dict[str, str], wa_verify: Dict[str, Any]):
    """Muestra la tabla con los enlaces de interacción de WhatsApp."""
    table = Table(title="💬 WHATSAPP DIRECT ACCESS & DEEP LINKS", box=box.ROUNDED, border_style="green", header_style="bold bright_white")
    table.add_column("Canal de Acceso", style="bright_green", width=24)
    table.add_column("Enlace / URI", style="bright_white")

    table.add_row("Direct Chat (wa.me)", f"[underline cyan]{wa_links['wa_me']}[/underline cyan]")
    table.add_row("WhatsApp Web", f"[underline cyan]{wa_links['whatsapp_web']}[/underline cyan]")
    table.add_row("API Gateway", f"[underline cyan]{wa_links['api_send']}[/underline cyan]")
    table.add_row("Protocolo Nativo App", f"[bold yellow]{wa_links['app_protocol']}[/bold yellow]")
    table.add_row("Estado de Pasarela Web", wa_verify["registered_hint"])

    console.print(table)


# ==============================================================================
# MOTOR OSINT: GOOGLE DORKS AUTOMATIZADOS
# ==============================================================================

def generate_google_dorks(data: Dict[str, Any]) -> Dict[str, str]:
    """Genera una lista de Google Dorks dirigidos al número."""
    digits = data["digits_only"]
    nat = data["national_number"]
    e164 = data["e164"]

    dorks = {
        "Grupos de WhatsApp": f'site:chat.whatsapp.com "{digits}" OR "{nat}"',
        "Enlaces Directos wa.me": f'site:wa.me "{digits}" OR inurl:"{digits}"',
        "Fugas & Pastebin": f'site:pastebin.com OR site:ghostbin.com OR site:justpaste.it "{digits}" OR "{e164}"',
        "Documentos Expuestos": f'filetype:pdf OR filetype:xlsx OR filetype:docx OR filetype:csv "{digits}" OR "{e164}"',
        "Redes Sociales": f'site:facebook.com OR site:twitter.com OR site:instagram.com OR site:linkedin.com "{digits}" OR "{e164}"',
        "Menciones en GitHub / Código": f'site:github.com OR site:gitlab.com "{digits}" OR "{e164}"',
        "Telegram Pivots": f'site:t.me "{digits}" OR inurl:"{digits}"'
    }
    return dorks


def display_dorks_table(dorks: Dict[str, str]):
    """Muestra los Dorks generados en una tabla de Rich."""
    table = Table(title="🔎 GOOGLE DORKS OSINT (Búsqueda de Fugas y Menciones)", box=box.ROUNDED, border_style="yellow", header_style="bold bright_white")
    table.add_column("Categoría de Búsqueda", style="bright_yellow", width=26)
    table.add_column("Google Dork Query", style="bright_white")

    for cat, query in dorks.items():
        table.add_row(cat, query)

    console.print(table)
    console.print("[dim]💡 Copia y pega cualquiera de estas consultas en Google para descubrir apariciones públicas o grupos indexados.[/dim]\n")


# ==============================================================================
# MOTOR OSINT: FOOTPRINTING MULTIPLATAFORMA
# ==============================================================================

def generate_cross_platform_links(data: Dict[str, Any]) -> Dict[str, str]:
    """Genera enlaces OSINT hacia plataformas de identificación y mensajería."""
    digits = data["digits_only"]
    nat = data["national_number"]
    cc = str(data["country_code"])

    links = {
        "Telegram Direct Lookup": f"https://t.me/+{digits}",
        "Truecaller Web Search": f"https://www.truecaller.com/search/{cc}/{nat}",
        "Sync.me Lookup": f"https://sync.me/search/?number={digits}",
        "Whoscall Identificador": "https://whoscall.com/",
        "ListaSpam (Reportes España/Latam)": f"https://www.listaspam.com/busca.php?Telefono={digits}",
        "Tellows (Reputación Telefónica)": f"https://www.tellows.es/num/{digits}",
        "SpyDialer (US/Internacional)": f"https://www.spydialer.com/"
    }
    return links


def display_cross_platform_table(links: Dict[str, str]):
    """Muestra la tabla de huella digital multiplataforma."""
    table = Table(title="🌐 FOOTPRINTING & BÚSQUEDA MULTIPLATAFORMA", box=box.ROUNDED, border_style="bright_magenta", header_style="bold bright_white")
    table.add_column("Plataforma", style="bright_magenta", width=30)
    table.add_column("Enlace Directo", style="bright_white")

    for plat, url in links.items():
        table.add_row(plat, f"[underline cyan]{url}[/underline cyan]")

    console.print(table)


# ==============================================================================
# GENERADOR DE VCARD (.VCF)
# ==============================================================================

def generate_vcard_file(data: Dict[str, Any], output_path: Optional[str] = None) -> str:
    """Crea un archivo vCard (.vcf) para importar el contacto en el móvil fácilmente."""
    digits = data["digits_only"]
    e164 = data["e164"]
    carrier_name = data["carrier"]
    loc = data["location"]
    
    if not output_path:
        output_path = f"target_{digits}.vcf"

    vcard_content = f"""BEGIN:VCARD
VERSION:3.0
FN:OSINT_{digits}
N:;OSINT_{digits};;;
TEL;TYPE=CELL,VOICE:{e164}
NOTE:OSINT Target - Carrier: {carrier_name} | Location: {loc}
CATEGORIES:OSINT_Target
END:VCARD
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(vcard_content)

    return output_path


# ==============================================================================
# MÓDULO RAPIDAPI (OPCIONAL / FALLBACK MEJORADO)
# ==============================================================================

def execute_rapidapi_scan(phone_str: str, api_key: str):
    """Ejecuta consultas a RapidAPI con diagnóstico y manejo inteligente de errores."""
    console.print("\n[bold cyan]🔑 Conectando a RapidAPI (whatsapp-osint.p.rapidapi.com)...[/bold cyan]")
    
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    
    endpoints = {
        "1. Foto de Perfil (Base64)": {"url": "https://whatsapp-osint.p.rapidapi.com/wspic/b64", "method": "GET"},
        "2. Estado del Usuario (/about)": {"url": "https://whatsapp-osint.p.rapidapi.com/about", "method": "GET"},
        "3. Verificación Business (/bizos)": {"url": "https://whatsapp-osint.p.rapidapi.com/bizos", "method": "POST"},
        "4. Dispositivos Vinculados (/devices)": {"url": "https://whatsapp-osint.p.rapidapi.com/devices", "method": "GET"},
        "5. Datos OSINT Completos (/wspic/dck)": {"url": "https://whatsapp-osint.p.rapidapi.com/wspic/dck", "method": "GET"},
        "6. Configuración de Privacidad (/privacy)": {"url": "https://whatsapp-osint.p.rapidapi.com/privacy", "method": "GET"},
    }

    table = Table(title="☁️ RESULTADOS DE RAPIDAPI", box=box.ROUNDED, border_style="blue", header_style="bold bright_white")
    table.add_column("Endpoint", style="cyan", width=32)
    table.add_column("HTTP", style="bold", width=8)
    table.add_column("Diagnóstico / Respuesta", style="bright_white")

    clean_digits = re.sub(r"[^\d]", "", phone_str)

    with console.status("[bold green]Consultando endpoints de RapidAPI...[/bold green]", spinner="dots"):
        for name, config in endpoints.items():
            try:
                if config["method"] == "GET":
                    r = requests.get(config["url"], headers=headers, params={"phone": clean_digits}, timeout=15)
                else:
                    r = requests.post(config["url"], headers=headers, json={"phone": clean_digits}, timeout=15)
                
                status = str(r.status_code)
                body = r.text.strip()

                # Interpretación inteligente de respuestas
                if r.status_code == 200:
                    try:
                        data = r.json()
                        if data == {} or data == []:
                            diag = "[yellow]Respuesta vacía (Sin datos públicos o sesión no disponible)[/yellow]"
                        elif "Info" in data and "maintenance" in data["Info"].lower():
                            diag = f"[bold yellow]⚠️ {data['Info']}[/bold yellow]"
                        elif "message" in data:
                            diag = f"[green]{data['message']}[/green]"
                        elif "base64" in data or "data" in data or "image" in data:
                            b64 = data.get("base64") or data.get("data") or data.get("image")
                            img_name = f"whatsapp_{clean_digits}.jpg"
                            try:
                                with open(img_name, "wb") as img_f:
                                    img_f.write(base64.b64decode(b64))
                                diag = f"[bold green]✓ Foto guardada como {img_name}[/bold green]"
                            except Exception:
                                diag = "[green]Foto recibida (Base64 presente)[/green]"
                        else:
                            diag = f"[green]{json.dumps(data, ensure_ascii=False)[:80]}...[/green]"
                    except Exception:
                        diag = f"[white]{body[:80]}[/white]"
                elif "business" in body.lower() or "pictures are only available" in body.lower():
                    diag = "[bold red]Restringido: WhatsApp solo permite fotos de cuentas Business en esta API[/bold red]"
                elif r.status_code == 530 or r.status_code == 503:
                    diag = f"[red]Error {r.status_code}: {body[:60]}[/red]"
                elif r.status_code == 401 or r.status_code == 403:
                    diag = "[bold red]Clave de RapidAPI inválida o sin suscripción activa[/bold red]"
                elif r.status_code == 429:
                    diag = "[bold red]Límite de peticiones alcanzado (Rate Limit)[/bold red]"
                else:
                    diag = f"[red]Error {r.status_code}: {body[:60]}[/red]"

                table.add_row(name, status, diag)
            except Exception as e:
                table.add_row(name, "ERR", f"[red]Fallo de conexión: {e}[/red]")

    console.print(table)


# ==============================================================================
# EXPORTACIÓN DE INFORMES
# ==============================================================================

def export_full_report(data: Dict[str, Any], wa_links: Dict[str, str], dorks: Dict[str, str], cross_links: Dict[str, str], format_type: str = "json") -> str:
    """Exporta los hallazgos en formato JSON o TXT."""
    digits = data["digits_only"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    report_payload = {
        "timestamp": datetime.now().isoformat(),
        "target": {
            "e164": data["e164"],
            "national_format": data["national_format"],
            "international_format": data["international_format"],
            "is_valid": data["is_valid"],
            "country_code": data["country_code"],
            "region_code": data["region_code"],
            "location": data["location"],
            "carrier": data["carrier"],
            "line_type": data["line_type"],
            "timezones": data["timezones"]
        },
        "whatsapp_deep_links": wa_links,
        "google_dorks": dorks,
        "cross_platform_lookups": cross_links
    }

    if format_type.lower() == "json":
        filename = f"osint_report_{digits}_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report_payload, f, indent=2, ensure_ascii=False)
    else:
        filename = f"osint_report_{digits}_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"=====================================================\n")
            f.write(f"WHATS LOOKUP OSINT REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"=====================================================\n\n")
            f.write(f"TARGET: {data['e164']}\n")
            f.write(f"Validez: {data['is_valid']}\n")
            f.write(f"Ubicación: {data['location']}\n")
            f.write(f"Operador: {data['carrier']}\n")
            f.write(f"Tipo de línea: {data['line_type']}\n")
            f.write(f"Zonas Horarias: {', '.join(data['timezones'])}\n\n")
            f.write(f"WHATSAPP LINKS:\n")
            for k, v in wa_links.items():
                f.write(f"  - {k}: {v}\n")
            f.write(f"\nGOOGLE DORKS:\n")
            for k, v in dorks.items():
                f.write(f"  - {k}: {v}\n")
            f.write(f"\nCROSS PLATFORM:\n")
            for k, v in cross_links.items():
                f.write(f"  - {k}: {v}\n")

    return filename


# ==============================================================================
# INVESTIGACIÓN COMPLETA (1-CLIC)
# ==============================================================================

def run_full_investigation(raw_phone: str, api_key: Optional[str] = None, force_rapidapi: bool = False, output_format: str = "json", is_interactive: bool = False):
    """Ejecuta el flujo integral de OSINT de 1 clic."""
    with console.status("[bold green]Analizando número y ejecutando comprobaciones OSINT...[/bold green]", spinner="arc"):
        data = parse_and_validate_number(raw_phone)
        if not data:
            console.print(f"[bold red]❌ El número '{raw_phone}' no tiene un formato telefónico válido.[/bold red]")
            console.print("[yellow]💡 Introduce el número con prefijo internacional. Ejemplo: +34612345678 o 51987654321[/yellow]")
            return

        wa_links = analyze_whatsapp_links(data)
        wa_verify = verify_whatsapp_web(data)
        dorks = generate_google_dorks(data)
        cross_links = generate_cross_platform_links(data)

    console.print()
    display_telecom_table(data)
    console.print()
    display_whatsapp_table(data, wa_links, wa_verify)
    console.print()
    display_dorks_table(dorks)
    console.print()
    display_cross_platform_table(cross_links)
    console.print()

    # Generación de vCard
    vcard_file = generate_vcard_file(data)
    console.print(f"[bold green]📇 Tarjeta vCard creada:[/bold green] [cyan]{vcard_file}[/cyan] (Importable en tu smartphone)")

    # Exportación de informe
    report_file = export_full_report(data, wa_links, dorks, cross_links, output_format)
    console.print(f"[bold green]📄 Informe {output_format.upper()} generado:[/bold green] [cyan]{report_file}[/cyan]")

    # Manejo de RapidAPI
    if force_rapidapi and api_key:
        execute_rapidapi_scan(raw_phone, api_key)
    elif is_interactive and api_key:
        console.print()
        if Confirm.ask("[bold yellow]¿Deseas ejecutar también la consulta a RapidAPI (Opcional)?[/bold yellow]", default=False):
            execute_rapidapi_scan(raw_phone, api_key)


# ==============================================================================
# MENÚ INTERACTIVO (TUX)
# ==============================================================================

def interactive_menu():
    """Bucle principal de la interfaz interactiva."""
    print_banner()
    api_key = os.getenv("RAPIDAPI_KEY")

    while True:
        menu_table = Table(title="📌 MENÚ PRINCIPAL", box=box.ROUNDED, border_style="bright_blue", header_style="bold bright_white")
        menu_table.add_column("Opción", style="bold yellow", width=8, justify="center")
        menu_table.add_column("Módulo OSINT", style="bright_white")
        menu_table.add_column("Descripción", style="dim")

        menu_table.add_row("1", "🕵️‍♂️ Investigación Completa (1-Clic)", "Telecom + WhatsApp + Dorks + Footprinting + Reporte")
        menu_table.add_row("2", "📡 Análisis Telecom & Operador", "Carrier, país, tipo de línea y geolocalización")
        menu_table.add_row("3", "💬 WhatsApp Links & Verificación", "Direct chat, WhatsApp Web y Deep Links")
        menu_table.add_row("4", "🔎 Generador de Google Dorks", "Búsqueda de grupos indexados y fugas públicas")
        menu_table.add_row("5", "🌐 Footprinting Multiplataforma", "Pivotes hacia Telegram, Truecaller, SyncMe, etc.")
        menu_table.add_row("6", "📇 Generar vCard (.vcf)", "Exportar contacto listo para inspeccionar en WhatsApp")
        menu_table.add_row("7", "☁️ Consultar RapidAPI (Opcional)", "Probar endpoints externos con diagnóstico")
        menu_table.add_row("0", "❌ Salir", "Cerrar la herramienta")

        console.print(menu_table)
        choice = Prompt.ask("[bold cyan]Selecciona una opción[/bold cyan]", choices=["1", "2", "3", "4", "5", "6", "7", "0"], default="1")

        if choice == "0":
            console.print("\n[bold green]👋 ¡Hasta pronto! Buenas investigaciones OSINT.[/bold green]\n")
            break

        phone = Prompt.ask("\n[bold green]Introduce el número telefónico[/bold green] (con código de país, ej. +34612345678 o 51916574069)").strip()
        data = parse_and_validate_number(phone)
        if not data:
            console.print(f"[bold red]❌ El número '{phone}' no es válido.[/bold red] Asegúrate de incluir el prefijo internacional (ej. +34 o +51).\n")
            continue

        console.print()
        if choice == "1":
            run_full_investigation(phone, api_key, is_interactive=True)
        elif choice == "2":
            display_telecom_table(data)
        elif choice == "3":
            wa_links = analyze_whatsapp_links(data)
            wa_verify = verify_whatsapp_web(data)
            display_whatsapp_table(data, wa_links, wa_verify)
        elif choice == "4":
            dorks = generate_google_dorks(data)
            display_dorks_table(dorks)
        elif choice == "5":
            cross_links = generate_cross_platform_links(data)
            display_cross_platform_table(cross_links)
        elif choice == "6":
            vcf = generate_vcard_file(data)
            console.print(f"[bold green]✅ Archivo vCard generado:[/bold green] [cyan]{vcf}[/cyan]\n")
        elif choice == "7":
            if not api_key:
                api_key_input = Prompt.ask("[yellow]No se detectó RAPIDAPI_KEY en .env. Introduce tu clave[/yellow]").strip()
                if api_key_input:
                    execute_rapidapi_scan(phone, api_key_input)
                else:
                    console.print("[red]❌ Operación cancelada: se requiere API Key.[/red]")
            else:
                execute_rapidapi_scan(phone, api_key)

        console.print("\n" + "─" * 60 + "\n")


# ==============================================================================
# PUNTO DE ENTRADA CLI
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="WhatsLookup OSINT Suite v2.0")
    parser.add_argument("-p", "--phone", help="Número telefónico objetivo (con código de país, ej: +34612345678)")
    parser.add_argument("-a", "--all", action="store_true", help="Ejecutar investigación completa automáticamente")
    parser.add_argument("-o", "--output", choices=["json", "txt"], default="json", help="Formato de exportación del informe (default: json)")
    parser.add_argument("--rapidapi", action="store_true", help="Ejecutar también escaneo en RapidAPI")

    args = parser.parse_args()

    if args.phone:
        print_banner()
        api_key = os.getenv("RAPIDAPI_KEY")
        data = parse_and_validate_number(args.phone)
        if not data:
            console.print(f"[bold red]❌ Número inválido: {args.phone}[/bold red]")
            sys.exit(1)

        run_full_investigation(
            raw_phone=args.phone, 
            api_key=api_key, 
            force_rapidapi=args.rapidapi, 
            output_format=args.output, 
            is_interactive=False
        )
    else:
        interactive_menu()


if __name__ == "__main__":
    main()

