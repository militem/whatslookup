<h1 align="center">WHATS LOOKUP 🕵️‍♂️ v2.0</h1>

<p align="center">
  Suite avanzada de <strong>OSINT para WhatsApp y Números Telefónicos</strong>.<br>
  <strong>100% Autónoma</strong> (sin necesidad obligatoria de APIs de pago externas) con una <strong>TUI/CLI Moderna e Interactiva</strong>.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white" alt="Python version">
  <img src="https://img.shields.io/badge/TUX-Rich%20Terminal-9cf?logo=gnometerminal&logoColor=white">
  <img src="https://img.shields.io/badge/OSINT-Autonomous-green">
  <img src="https://img.shields.io/badge/License-MIT-green?logo=open-source-initiative&logoColor=white" alt="License">
</p>

---

## 🚀 Nuevas Características (v2.0)

- ⚡ **Modo Autónomo**: Análisis completo sin depender de APIs de terceros caídas o de pago.
- 📡 **Análisis de Telecomunicaciones & Carrier**: Detección de operador telefónico (Carrier/ISP móvil), país, región, geolocalización aproximada, zona horaria y tipo de línea (Móvil, Fija, VoIP, Tarifa especial) con soporte de Google `libphonenumber`.
- 💬 **WhatsApp Direct Access & Deep Links**: Generación de enlaces directos (`wa.me`), WhatsApp Web, y protocolos nativos de app (`whatsapp://send`).
- 📇 **Generador de Tarjetas de Contacto vCard (.vcf)**: Crea archivos `.vcf` con 1 clic para importar el objetivo en la agenda de tu smartphone y visualizar su foto/estado de WhatsApp al instante.
- 🔎 **Generador de Google Dorks Automatizados**: Búsquedas automáticas para descubrir grupos de WhatsApp indexados (`chat.whatsapp.com`), fugas en Pastebin/Ghostbin, menciones en GitHub y redes sociales.
- 🌐 **Footprinting Multiplataforma**: Pivotes rápidos hacia Telegram (`t.me/+...`), Truecaller, Sync.me, ListaSpam y bases de reputación telefónica.
- 📊 **Exportación de Informes**: Guarda automáticamente los hallazgos en formato estructurado **JSON** o **TXT**.
- ☁️ **Módulo RapidAPI Inteligente (Opcional)**: Diagnóstico detallado con interpretación de códigos de error (`530`, `503`, cuotas y estados de mantenimiento).
- 🎨 **Experiencia de Usuario en Terminal (TUX)**: Interfaz basada en `rich` con tablas estilizadas, paneles, spinners y menús interactivos.

---

## 📌 Requisitos

- Python 3.8 o superior
- Dependencias: `rich`, `phonenumbers`, `requests`, `python-dotenv`, `colorama`

```bash
pip install -r requirements.txt
```

---

## 🐍 Modos de Uso

### 1. Modo Interactivo (Menú TUX Completo)
```bash
python3 whats_lookup.py
```
Desplegará un menú interactivo con opciones numeradas para realizar escaneos completos o por módulos específicos.

### 2. Modo Directo por Línea de Comandos (CLI)

- **Investigación Completa (1-Clic)**:
```bash
python3 whats_lookup.py -p "+34605797764" -a
```

- **Exportar Informe en formato Texto (.txt)**:
```bash
python3 whats_lookup.py -p "+51916574069" -a -o txt
```

- **Incluir Escaneo en RapidAPI (si tienes clave configurada)**:
```bash
python3 whats_lookup.py -p "+34605797764" -a --rapidapi
```

---

## 🔑 Configuración Opcional (RapidAPI)

Si deseas utilizar adicionalmente los endpoints de RapidAPI, puedes configurar tu archivo `.env`:

```bash
cp .env.example .env
```
Edita `.env` con tu clave:
```env
RAPIDAPI_KEY=tu_api_key_aqui
```

> **Nota sobre RapidAPI**: WhatsApp restringe activamente las APIs de scraping externas. Si el endpoint de fotos devuelve aviso de cuenta Business o mantenimiento, utiliza el **generador de vCard** (`.vcf`) y los **enlaces directos** nativos de la herramienta.

---

## ⚠️ Advertencia de uso

Esta herramienta ha sido creada exclusivamente para:
- Investigaciones de ciberseguridad legítimas
- Auditorías y peritajes autorizados
- Proyectos de OSINT con fines educativos y de concienciación
- Análisis con consentimiento explícito

🔴 **No utilices esta herramienta para actividades ilícitas o acoso.**

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más información.
